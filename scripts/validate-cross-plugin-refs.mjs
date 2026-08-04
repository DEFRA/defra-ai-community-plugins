#!/usr/bin/env node
/**
 * Validate that agent prompts only reference skills from their own plugin or
 * from a plugin declared in `dependencies` in plugin.json.
 *
 * This marketplace does not auto-install dependencies — the validator is the
 * only gate that catches drift between an agent's prompt and its manifest.
 * Without this, an agent can name a skill from another plugin in its workflow
 * and the reference will silently dangle if the user installs this plugin
 * alone. Dependencies must resolve to a plugin in this same repo — a plugin
 * cannot depend on one published only in the official defra-ai-plugins
 * marketplace.
 */
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import matter from 'gray-matter'
import { REPO_ROOT } from './lib/load-schema.mjs'
import { discoverEntryPoints, listPluginDirs } from './lib/discover.mjs'

const PLUGINS_DIR = resolve(REPO_ROOT, 'plugins')

/**
 * Build a map of every skill name → the plugin that owns it.
 * @param {string[]} pluginDirs
 * @returns {Map<string, string>}
 */
function buildSkillRegistry(pluginDirs) {
  /** @type {Map<string, string>} */
  const registry = new Map()
  for (const dir of pluginDirs) {
    const pluginRoot = resolve(PLUGINS_DIR, dir)
    for (const entry of discoverEntryPoints(pluginRoot)) {
      if (entry.format === 'skill') {
        registry.set(entry.name, dir)
      }
    }
  }
  return registry
}

/**
 * Find every skill name from `registry` that appears as a whole word in `body`.
 * Skill names are kebab-case (≥ 2 chars) so substring collisions with English
 * prose are vanishingly rare; the `\b` word boundary guards against partial
 * matches like `defra-branching-extras`.
 * @param {string} body
 * @param {Map<string, string>} registry
 * @returns {Set<string>}
 */
function findSkillReferences(body, registry) {
  /** @type {Set<string>} */
  const hits = new Set()
  for (const name of registry.keys()) {
    const re = new RegExp(String.raw`\b${name}\b`)
    if (re.test(body)) {
      hits.add(name)
    }
  }
  return hits
}

/**
 * Read and parse a plugin.json. Returns null when missing or unparseable —
 * validate-plugins.mjs reports parse errors, so we silently skip here.
 * @param {string} manifestPath
 * @returns {object|null}
 */
function loadManifest(manifestPath) {
  if (!existsSync(manifestPath)) {
    return null
  }
  try {
    return JSON.parse(readFileSync(manifestPath, 'utf8'))
  } catch {
    return null
  }
}

/**
 * Undeclared-dependency errors for a single agent entry point. Returns [] for
 * non-agent entries and for files whose frontmatter won't parse (those are
 * reported by validate-frontmatter.mjs).
 * @returns {string[]}
 */
function refErrorsForEntry(entry, dir, skillRegistry, declaredDeps) {
  if (entry.format !== 'copilot-agent' && entry.format !== 'claude-agent') {
    return []
  }
  let parsed
  try {
    parsed = matter(readFileSync(entry.absPath, 'utf8'))
  } catch {
    return []
  }

  const errors = []
  for (const skillName of findSkillReferences(parsed.content, skillRegistry)) {
    const owningPlugin = skillRegistry.get(skillName)
    if (owningPlugin !== dir && !declaredDeps.has(owningPlugin)) {
      errors.push(
        `plugins/${dir}/${entry.relPath}: references skill "${skillName}" ` +
          `(owned by plugin "${owningPlugin}") but plugins/${dir}/plugin.json ` +
          `does not declare "${owningPlugin}" in "dependencies".`
      )
    }
  }
  return errors
}

function collectAgentRefErrors(dir, pluginRoot, skillRegistry, declaredDeps) {
  const errors = []
  for (const entry of discoverEntryPoints(pluginRoot)) {
    errors.push(...refErrorsForEntry(entry, dir, skillRegistry, declaredDeps))
  }
  return errors
}

/**
 * Errors for declared dependencies that don't resolve to a sibling plugin
 * (or that name the declaring plugin itself).
 * @param {string} dir
 * @param {Set<string>} declaredDeps
 * @param {string[]} dirs
 * @returns {string[]}
 */
function collectDepErrors(dir, declaredDeps, dirs) {
  const errors = []
  for (const depName of declaredDeps) {
    if (!dirs.includes(depName)) {
      errors.push(
        `plugins/${dir}/plugin.json: dependency "${depName}" is not a plugin in this marketplace ` +
          `(no plugins/${depName}/ directory).`
      )
    }
    if (depName === dir) {
      errors.push(`plugins/${dir}/plugin.json: plugin lists itself as a dependency.`)
    }
  }
  return errors
}

/**
 * @returns {string[]} list of error messages (empty if valid)
 */
export function validateCrossPluginRefs() {
  if (!existsSync(PLUGINS_DIR)) {
    return ['plugins/: directory does not exist']
  }

  const dirs = listPluginDirs(PLUGINS_DIR)
  const skillRegistry = buildSkillRegistry(dirs)
  const errors = []

  for (const dir of dirs) {
    const pluginRoot = resolve(PLUGINS_DIR, dir)
    const manifest = loadManifest(resolve(pluginRoot, 'plugin.json'))
    if (!manifest) {
      continue
    }
    const declaredDeps = new Set(Array.isArray(manifest.dependencies) ? manifest.dependencies : [])
    errors.push(
      ...collectAgentRefErrors(dir, pluginRoot, skillRegistry, declaredDeps),
      ...collectDepErrors(dir, declaredDeps, dirs)
    )
  }

  return errors
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const errors = validateCrossPluginRefs()
  if (errors.length) {
    console.error(`cross-plugin refs: ${errors.length} error(s)`)
    for (const e of errors) {
      console.error(`  - ${e}`)
    }
    process.exit(1)
  }
  console.log('cross-plugin refs: ok')
}

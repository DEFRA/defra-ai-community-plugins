#!/usr/bin/env node
/**
 * Validate every plugin under plugins/ against the plugin schema and
 * cross-check against the marketplace registry. Also enforces structural
 * requirements: each plugin needs a README.md and at least one entry point
 * (Copilot agent, Claude agent, or skill — see scripts/lib/discover.mjs).
 *
 * `plugins/_template/` is scaffolding, not a real plugin — listPluginDirs()
 * excludes it, and this repo starts with zero registered plugins, so an
 * empty catalogue is a valid (not an error) starting state.
 */
import { existsSync } from 'node:fs'
import { resolve, basename } from 'node:path'
import { REPO_ROOT, readJson, buildValidator } from './lib/load-schema.mjs'
import { discoverEntryPoints, listPluginDirs } from './lib/discover.mjs'

const PLUGINS_DIR = resolve(REPO_ROOT, 'plugins')
const MARKETPLACE_PATH = resolve(REPO_ROOT, '.github/plugin/marketplace.json')

/**
 * Build a name → marketplace-entry index, recording a read error in `errors`
 * if the registry can't be loaded.
 * @param {string[]} errors
 * @returns {Map<string, object>}
 */
function buildMarketplaceIndex(errors) {
  let marketplace = { plugins: [] }

  try {
    marketplace = readJson(MARKETPLACE_PATH)
  } catch (err) {
    errors.push(`marketplace.json: cannot read for cross-check: ${err.message}`)
  }

  const byName = new Map()

  if (Array.isArray(marketplace.plugins)) {
    for (const p of marketplace.plugins) {
      if (p && typeof p.name === 'string') {
        byName.set(p.name, p)
      }
    }
  }

  return byName
}

/**
 * Cross-check a plugin manifest against its marketplace registry entry.
 * @returns {string[]}
 */
function checkMarketplaceEntry(prefix, dir, manifest, marketplaceByName) {
  const entry = marketplaceByName.get(manifest.name)

  if (!entry) {
    return [`${prefix}: not registered in marketplace.json (expected entry "${manifest.name}")`]
  }

  const errors = []

  if (entry.description !== manifest.description) {
    errors.push(`${prefix}: description in plugin.json does not match marketplace.json entry`)
  }

  if (entry.version !== manifest.version) {
    errors.push(
      `${prefix}: version in plugin.json does not match marketplace.json entry ` +
        `(plugin: ${manifest.version}, marketplace: ${entry.version})`
    )
  }

  const expectedSource = `plugins/${dir}`

  if (entry.source !== expectedSource) {
    errors.push(
      `${prefix}: marketplace.json source "${entry.source}" should be "${expectedSource}"`
    )
  }

  return errors
}

/**
 * Entry-point existence + skill-directory naming checks for one plugin.
 * @returns {string[]}
 */
function checkEntryPoints(prefix, pluginRoot) {
  const errors = []
  const entries = discoverEntryPoints(pluginRoot)

  if (entries.length === 0) {
    errors.push(
      `${prefix}: no entry points found — expected one of agents/*.agent.md, ` +
        `agents/*.md, or skills/<name>/SKILL.md`
    )
  }

  // Skill folders must match the convention: skills/<name>/ where the dir name
  // is the skill identifier and matches SKILL.md frontmatter (checked elsewhere).
  for (const entry of entries) {
    if (entry.format === 'skill' && !/^[a-z][a-z0-9-]*[a-z0-9]$/.test(entry.name)) {
      errors.push(`${prefix}/${entry.relPath}: skill directory "${entry.name}" must be kebab-case`)
    }
  }

  return errors
}

/**
 * Validate a single plugin directory (manifest, schema, marketplace cross-check,
 * README, entry points). Returns early on the fatal cases (missing/unparseable
 * manifest) so the caller never has to use loop control.
 * @returns {string[]}
 */
function validateOnePlugin(dir, validatePlugin, marketplaceByName) {
  const pluginRoot = resolve(PLUGINS_DIR, dir)
  const manifestPath = resolve(pluginRoot, 'plugin.json')
  const prefix = `plugins/${dir}`

  if (!existsSync(manifestPath)) {
    return [`${prefix}: plugin.json missing`]
  }

  let manifest

  try {
    manifest = readJson(manifestPath)
  } catch (err) {
    return [`${prefix}/plugin.json: cannot parse: ${err.message}`]
  }

  const errors = []

  for (const e of validatePlugin(manifest)) {
    errors.push(`${prefix}/plugin.json: ${e}`)
  }

  if (manifest.name !== basename(pluginRoot)) {
    errors.push(`${prefix}/plugin.json: name "${manifest.name}" does not match directory "${dir}"`)
  }

  errors.push(...checkMarketplaceEntry(prefix, dir, manifest, marketplaceByName))

  if (!existsSync(resolve(pluginRoot, 'README.md'))) {
    errors.push(`${prefix}: README.md missing`)
  }

  errors.push(...checkEntryPoints(prefix, pluginRoot))
  return errors
}

/**
 * Reverse check: every marketplace entry must have a plugin directory.
 * @returns {string[]}
 */
function checkOrphanMarketplaceEntries(marketplaceByName, dirs) {
  const errors = []
  for (const [name, entry] of marketplaceByName) {
    if (!dirs.includes(name)) {
      errors.push(
        `marketplace.json: plugin "${name}" listed (source "${entry.source}") but no plugins/${name}/ directory`
      )
    }
  }
  return errors
}

/**
 * @returns {string[]} list of error messages (empty if valid)
 */
export function validatePlugins() {
  if (!existsSync(PLUGINS_DIR)) {
    return ['plugins/: directory does not exist']
  }

  const dirs = listPluginDirs(PLUGINS_DIR)

  const errors = []
  const validatePlugin = buildValidator('plugin.schema.json')
  const marketplaceByName = buildMarketplaceIndex(errors)
  for (const dir of dirs) {
    errors.push(...validateOnePlugin(dir, validatePlugin, marketplaceByName))
  }
  errors.push(...checkOrphanMarketplaceEntries(marketplaceByName, dirs))
  return errors
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const errors = validatePlugins()
  if (errors.length) {
    console.error(`plugins: ${errors.length} error(s)`)
    for (const e of errors) {
      console.error(`  - ${e}`)
    }
    process.exit(1)
  }
  console.log('plugins: ok')
}

#!/usr/bin/env node
/**
 * Validate the YAML frontmatter of every entry-point file under plugins/.
 * Format-agnostic: dispatches to per-format rules based on file path.
 *
 *   copilot-agent  →  agents/<name>.agent.md
 *                     requires: description, tools (non-empty array)
 *
 *   claude-agent   →  agents/<name>.md (any other .md)
 *                     requires: description
 *                     optional: tools (must be array if present)
 *
 *   skill          →  skills/<name>/SKILL.md
 *                     requires: name (must match parent dir), description
 */
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import matter from 'gray-matter'
import { REPO_ROOT } from './lib/load-schema.mjs'
import { discoverEntryPoints, listPluginDirs } from './lib/discover.mjs'

const PLUGINS_DIR = resolve(REPO_ROOT, 'plugins')
const MAX_DESCRIPTION_LENGTH = 500

/**
 * @param {Record<string, unknown>} data parsed frontmatter
 * @param {string} prefix path prefix used in error messages
 * @returns {string[]}
 */
function validateDescription(data, prefix) {
  const { description } = data
  if (typeof description !== 'string' || description.trim().length === 0) {
    return [`${prefix}: frontmatter "description" missing or empty`]
  }
  if (description.length > MAX_DESCRIPTION_LENGTH) {
    return [
      `${prefix}: frontmatter "description" is ${description.length} chars (max ${MAX_DESCRIPTION_LENGTH})`
    ]
  }
  return []
}

/**
 * @param {unknown} value value of the `tools` frontmatter field
 * @param {string} prefix path prefix used in error messages
 * @param {{ required: boolean }} options
 * @returns {string[]}
 */
function validateToolsArray(value, prefix, { required }) {
  const errors = []
  if (value === undefined || value === null) {
    if (required) {
      errors.push(`${prefix}: frontmatter "tools" missing or not an array`)
    }
    return errors
  }
  if (!Array.isArray(value)) {
    errors.push(`${prefix}: frontmatter "tools" must be an array`)
    return errors
  }
  if (required && value.length === 0) {
    errors.push(`${prefix}: frontmatter "tools" array is empty`)
  }
  for (const [i, tool] of value.entries()) {
    if (typeof tool !== 'string' || tool.trim().length === 0) {
      errors.push(`${prefix}: frontmatter "tools[${i}]" must be a non-empty string`)
    }
  }
  return errors
}

/**
 * @param {Record<string, unknown>} data
 * @param {string} prefix
 * @returns {string[]}
 */
function validateCopilotAgent(data, prefix) {
  return [
    ...validateDescription(data, prefix),
    ...validateToolsArray(data.tools, prefix, { required: true })
  ]
}

/**
 * @param {Record<string, unknown>} data
 * @param {string} prefix
 * @returns {string[]}
 */
function validateClaudeAgent(data, prefix) {
  return [
    ...validateDescription(data, prefix),
    ...validateToolsArray(data.tools, prefix, { required: false })
  ]
}

/**
 * @param {Record<string, unknown>} data
 * @param {string} prefix
 * @param {string} expectedName  the parent directory name (skill identifier)
 * @returns {string[]}
 */
function validateSkillName(name, prefix, expectedName) {
  if (typeof name !== 'string' || name.trim().length === 0) {
    return [`${prefix}: frontmatter "name" missing or empty`]
  }
  if (name !== expectedName) {
    return [`${prefix}: frontmatter "name" is "${name}" but parent directory is "${expectedName}"`]
  }
  return []
}

function validateSkill(data, prefix, expectedName) {
  return [
    ...validateSkillName(data.name, prefix, expectedName),
    ...validateDescription(data, prefix)
  ]
}

/**
 * Validate the frontmatter of a single entry point. Returns early on the fatal
 * cases (unparseable / missing frontmatter) so the caller needs no loop control.
 * @param {import('./lib/discover.mjs').EntryPoint} entry
 * @param {string} dir plugin directory name
 * @returns {string[]}
 */
function validateEntry(entry, dir) {
  const prefix = `plugins/${dir}/${entry.relPath}`

  let parsed
  try {
    parsed = matter(readFileSync(entry.absPath, 'utf8'))
  } catch (err) {
    return [`${prefix}: cannot parse frontmatter: ${err.message}`]
  }

  const { data } = parsed
  if (!data || typeof data !== 'object') {
    return [`${prefix}: missing frontmatter block`]
  }

  switch (entry.format) {
    case 'copilot-agent':
      return validateCopilotAgent(data, prefix)
    case 'claude-agent':
      return validateClaudeAgent(data, prefix)
    case 'skill':
      return validateSkill(data, prefix, entry.name)
    default:
      return []
  }
}

/**
 * @returns {string[]} list of error messages (empty if valid)
 */
export function validateFrontmatter() {
  if (!existsSync(PLUGINS_DIR)) {
    return ['plugins/: directory does not exist']
  }

  const dirs = listPluginDirs(PLUGINS_DIR)

  const errors = []
  for (const dir of dirs) {
    const pluginRoot = resolve(PLUGINS_DIR, dir)
    for (const entry of discoverEntryPoints(pluginRoot)) {
      errors.push(...validateEntry(entry, dir))
    }
  }
  return errors
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const errors = validateFrontmatter()
  if (errors.length) {
    console.error(`frontmatter: ${errors.length} error(s)`)
    for (const e of errors) {
      console.error(`  - ${e}`)
    }
    process.exit(1)
  }
  console.log('frontmatter: ok')
}

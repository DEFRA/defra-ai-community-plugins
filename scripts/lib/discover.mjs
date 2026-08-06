/**
 * Discover and classify plugin entry points (agents and skills) inside a
 * single plugin directory. Format-agnostic so the validators can support
 * Copilot, Claude Code, and Codex side by side.
 *
 * Recognised formats:
 *
 *   copilot-agent  →  agents/<name>.agent.md
 *   claude-agent   →  agents/<name>.md          (any other .md in agents/)
 *   skill          →  skills/<name>/SKILL.md
 */
import { existsSync, readdirSync, statSync } from 'node:fs'
import { resolve, basename } from 'node:path'

/**
 * @typedef {'copilot-agent' | 'claude-agent' | 'skill'} EntryPointFormat
 *
 * @typedef {Object} EntryPoint
 * @property {string} absPath  absolute path to the entry point file
 * @property {string} relPath  path relative to the plugin root
 * @property {EntryPointFormat} format
 * @property {string} name     identifier (filename stem for agents, dir name for skills)
 */

/**
 * True when `dir` exists and is a directory.
 * @param {string} dir
 * @returns {boolean}
 */
function isDir(dir) {
  return existsSync(dir) && statSync(dir).isDirectory()
}

/**
 * List real plugin directories under `pluginsDir` — every subdirectory
 * except those prefixed with `_` (e.g. `_template`), which are scaffolding,
 * not installable plugins, and are never registered in marketplace.json.
 * @param {string} pluginsDir
 * @returns {string[]}
 */
export function listPluginDirs(pluginsDir) {
  return readdirSync(pluginsDir)
    .filter((entry) => !entry.startsWith('_'))
    .filter((entry) => statSync(resolve(pluginsDir, entry)).isDirectory())
}

/**
 * Entry points under agents/ — copilot-agent (`*.agent.md`) or claude-agent
 * (any other `*.md`), keyed on the filename.
 * @param {string} pluginRoot
 * @returns {EntryPoint[]}
 */
function discoverAgents(pluginRoot) {
  const agentsDir = resolve(pluginRoot, 'agents')
  if (!isDir(agentsDir)) {
    return []
  }

  /** @type {EntryPoint[]} */
  const entries = []
  for (const file of readdirSync(agentsDir)) {
    if (!file.endsWith('.md')) {
      continue
    }
    const isCopilot = file.endsWith('.agent.md')
    entries.push({
      absPath: resolve(agentsDir, file),
      relPath: `agents/${file}`,
      format: isCopilot ? 'copilot-agent' : 'claude-agent',
      name: isCopilot ? file.replace(/\.agent\.md$/, '') : file.replace(/\.md$/, '')
    })
  }
  return entries
}

/**
 * Entry points under skills/ — one per `skills/<name>/SKILL.md`.
 * @param {string} pluginRoot
 * @returns {EntryPoint[]}
 */
function discoverSkills(pluginRoot) {
  const skillsDir = resolve(pluginRoot, 'skills')
  if (!isDir(skillsDir)) {
    return []
  }

  /** @type {EntryPoint[]} */
  const entries = []
  for (const skillName of readdirSync(skillsDir)) {
    const skillRoot = resolve(skillsDir, skillName)
    const skillFile = resolve(skillRoot, 'SKILL.md')
    if (statSync(skillRoot).isDirectory() && existsSync(skillFile)) {
      entries.push({
        absPath: skillFile,
        relPath: `skills/${skillName}/SKILL.md`,
        format: 'skill',
        name: basename(skillRoot)
      })
    }
  }
  return entries
}

/**
 * Walk a single plugin directory and return every entry point it contains.
 * @param {string} pluginRoot absolute path to the plugin's root directory
 * @returns {EntryPoint[]}
 */
export function discoverEntryPoints(pluginRoot) {
  return [...discoverAgents(pluginRoot), ...discoverSkills(pluginRoot)]
}

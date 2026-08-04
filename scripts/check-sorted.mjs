#!/usr/bin/env node
/**
 * Check that .github/plugin/marketplace.json plugins are sorted
 * alphabetically by name (case-insensitive).
 *
 * Pass --fix to sort and write back in place.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { REPO_ROOT } from './lib/load-schema.mjs'

const MARKETPLACE_PATH = resolve(REPO_ROOT, '.github/plugin/marketplace.json')

const compare = (a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase())

/**
 * @param {{ fix?: boolean }} options
 * @returns {string[]} list of error messages (empty if sorted or fixed)
 */
export function checkSorted({ fix = false } = {}) {
  const errors = []
  let raw
  try {
    raw = readFileSync(MARKETPLACE_PATH, 'utf8')
  } catch (err) {
    return [`marketplace.json: cannot read: ${err.message}`]
  }

  let marketplace
  try {
    marketplace = JSON.parse(raw)
  } catch (err) {
    return [`marketplace.json: invalid JSON: ${err.message}`]
  }

  if (!Array.isArray(marketplace.plugins)) {
    return ['marketplace.json: missing "plugins" array']
  }

  if (fix) {
    marketplace.plugins.sort(compare)
    writeFileSync(MARKETPLACE_PATH, JSON.stringify(marketplace, null, 2) + '\n')
    return []
  }

  for (let i = 1; i < marketplace.plugins.length; i++) {
    if (compare(marketplace.plugins[i - 1], marketplace.plugins[i]) > 0) {
      errors.push(
        `marketplace.json: plugins not sorted alphabetically — ` +
          `"${marketplace.plugins[i - 1].name}" should come after "${marketplace.plugins[i].name}". ` +
          `Run \`npm run validate:fix\` to fix.`
      )
      break
    }
  }

  return errors
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const fix = process.argv.includes('--fix')
  const errors = checkSorted({ fix })
  if (errors.length) {
    for (const e of errors) {
      console.error(`  - ${e}`)
    }
    process.exit(1)
  }
  console.log(fix ? 'marketplace.json: sorted' : 'marketplace.json: ordering ok')
}

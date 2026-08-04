#!/usr/bin/env node
/**
 * Validate .github/plugin/marketplace.json against the marketplace schema
 * and run structural checks (no duplicate plugin names).
 *
 * Exits 0 on success, 1 on validation failure.
 */
import { resolve } from 'node:path'
import { REPO_ROOT, readJson, buildValidator } from './lib/load-schema.mjs'

const MARKETPLACE_PATH = resolve(REPO_ROOT, '.github/plugin/marketplace.json')

/**
 * Structural check beyond JSON Schema: flag any plugin name that appears twice.
 * @param {unknown[]} plugins
 * @returns {string[]}
 */
function findDuplicateNames(plugins) {
  const errors = []
  const seen = new Set()
  for (const [i, p] of plugins.entries()) {
    if (!p || typeof p !== 'object' || typeof p.name !== 'string') {
      continue
    }
    if (seen.has(p.name)) {
      errors.push(`marketplace.json: plugins[${i}] duplicate plugin name "${p.name}"`)
    }
    seen.add(p.name)
  }
  return errors
}

/**
 * @returns {string[]} list of error messages (empty if valid)
 */
export function validateMarketplace() {
  let marketplace
  try {
    marketplace = readJson(MARKETPLACE_PATH)
  } catch (err) {
    return [`marketplace.json: cannot read or parse: ${err.message}`]
  }

  const errors = []
  const schemaErrors = buildValidator('marketplace.schema.json')(marketplace)
  for (const e of schemaErrors) {
    errors.push(`marketplace.json: ${e}`)
  }

  if (Array.isArray(marketplace.plugins)) {
    errors.push(...findDuplicateNames(marketplace.plugins))
  }

  return errors
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const errors = validateMarketplace()
  if (errors.length) {
    console.error(`marketplace.json: ${errors.length} error(s)`)
    for (const e of errors) {
      console.error(`  - ${e}`)
    }
    process.exit(1)
  }
  console.log('marketplace.json: ok')
}

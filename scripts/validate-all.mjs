#!/usr/bin/env node
/**
 * Run every validator in sequence and aggregate errors so a single CI
 * run reports every problem at once.
 */
import { validateMarketplace } from './validate-marketplace.mjs'
import { validatePlugins } from './validate-plugins.mjs'
import { validateFrontmatter } from './validate-frontmatter.mjs'
import { validateCrossPluginRefs } from './validate-cross-plugin-refs.mjs'
import { checkSorted } from './check-sorted.mjs'

const checks = [
  ['marketplace.json', validateMarketplace],
  ['plugins/', validatePlugins],
  ['agent frontmatter', validateFrontmatter],
  ['cross-plugin refs', validateCrossPluginRefs],
  ['marketplace ordering', () => checkSorted({ fix: false })]
]

let totalErrors = 0
for (const [label, run] of checks) {
  const errors = run()
  if (errors.length) {
    console.error(`✗ ${label}: ${errors.length} error(s)`)
    for (const e of errors) {
      console.error(`    - ${e}`)
    }
    totalErrors += errors.length
  } else {
    console.log(`✓ ${label}`)
  }
}

if (totalErrors > 0) {
  console.error(`\n${totalErrors} error(s) total. Fix and re-run.`)
  process.exit(1)
}

console.log('\nAll checks passed.')

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import Ajv from 'ajv'
import addFormats from 'ajv-formats'

const here = dirname(fileURLToPath(import.meta.url))
export const REPO_ROOT = resolve(here, '..', '..')

/**
 * Read a JSON file and parse it.
 * @param {string} filePath absolute path
 * @returns {unknown}
 */
export function readJson(filePath) {
  return JSON.parse(readFileSync(filePath, 'utf8'))
}

/**
 * Build an AJV validator for a given schema file.
 * Strips the `$schema` property from instances before validation, since
 * AJV does not allow unknown top-level keywords on data documents.
 * @param {string} schemaFile relative to schemas/ (e.g. 'marketplace.schema.json')
 * @returns {(data: unknown) => string[]} returns an array of error messages (empty if valid)
 */
export function buildValidator(schemaFile) {
  const schemaPath = resolve(REPO_ROOT, 'schemas', schemaFile)
  const schema = readJson(schemaPath)

  const ajv = new Ajv({ allErrors: true, strict: false })
  addFormats(ajv)
  const validate = ajv.compile(schema)

  return (data) => {
    // Allow $schema on instances without failing additionalProperties
    const cleaned = data && typeof data === 'object' ? { ...data } : data
    if (cleaned && typeof cleaned === 'object') {
      delete cleaned.$schema
    }

    const ok = validate(cleaned)
    if (ok) {
      return []
    }
    return (validate.errors ?? []).map((err) => {
      const path = err.instancePath || '(root)'
      return `${path} ${err.message}${err.params ? ' ' + JSON.stringify(err.params) : ''}`
    })
  }
}

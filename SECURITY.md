# Security policy

## Reporting a vulnerability

If you find a security vulnerability in this repository — in a plugin, in the validator scripts, in the CI workflow, or anywhere else — please **do not** open a public GitHub issue.

Instead, email the Defra AI dev team at:

> **AICapabilitiesEnablement@defra.gov.uk**

Use a subject line that begins with `[SECURITY] defra-ai-community-plugins`.

## What to include

Please include as much of the following as you can:

- A description of the issue
- The repository path of the affected file(s) or plugin(s)
- Steps to reproduce the issue
- The potential impact
- Any suggested mitigation
- Whether you intend to disclose the issue publicly later (and on what timeline)

## What happens next

The AI dev team will:

1. Acknowledge receipt within 5 working days
2. Triage and confirm the issue
3. Notify the plugin's maintaining team (per `plugin.json#author`) and coordinate a fix with them, since AICE does not maintain merged plugins directly
4. Credit you in the fix release notes if you would like to be named

We follow coordinated disclosure: please give us a reasonable window to fix the issue before disclosing it publicly.

Because plugins here are community-maintained, not AICE-maintained: if the maintaining team does not respond or ship a fix within **15 UK working days** of acknowledgement, AICE may unpublish the affected plugin from `marketplace.json` (removing it from the installable catalogue) pending a fix, to limit exposure for other users.

## Out of scope

This repository ships text content (agent prompts, skills) for use by Copilot CLI and Claude Code. It does not execute network calls or process user data directly. Vulnerability classes typically out of scope:

- Issues in third-party tools that Copilot CLI or Claude Code calls (raise upstream)
- Issues in Defra services built with the help of these plugins (raise with the relevant service team)
- Theoretical issues with no practical exploitation path

If in doubt, email us anyway — we'd rather see false positives than miss something real.

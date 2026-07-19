# blockedpath-skills

[![Validate marketplace](https://github.com/BlockedPath/Skills/actions/workflows/validate.yml/badge.svg)](https://github.com/BlockedPath/Skills/actions/workflows/validate.yml)
[![CodeQL](https://github.com/BlockedPath/Skills/actions/workflows/codeql.yml/badge.svg)](https://github.com/BlockedPath/Skills/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/BlockedPath/Skills/badge)](https://scorecard.dev/viewer/?uri=github.com/BlockedPath/Skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![npm](https://img.shields.io/npm/v/blockedpath-skills.svg)](https://www.npmjs.com/package/blockedpath-skills)
[![GitHub release](https://img.shields.io/github/v/release/BlockedPath/Skills)](https://github.com/BlockedPath/Skills/releases/latest)
![Claude](https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=claude&logoColor=white)
![Codex](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)

A plugin marketplace containing skills and plugins for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex).


https://github.com/user-attachments/assets/de5a9884-9a9a-4842-9cd1-884e00e7b512


## Installation

### Quick install (npx)

```
npx blockedpath-skills
```

Detects whichever of Claude Code / Codex you have installed, adds this marketplace, and installs the available plugins.

### Claude Code

```
/plugin marketplace add BlockedPath/Skills
/plugin install x-article-to-markdown@blockedpath-skills
```

See [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

### Codex

```
codex plugin marketplace add BlockedPath/Skills
```

Then open the plugins directory (`codex /plugins`), select `blockedpath-skills`, and install `x-article-to-markdown`. See [Codex plugins](https://developers.openai.com/codex/plugins).

## Plugins

### x-article-to-markdown

Scrapes an X (Twitter) long-form Article into a local Markdown file, faithfully preserving its structure (headings, formatting, lists, blockquotes, links) and downloading images for offline viewing. X Articles are login-gated and client-rendered, so this skill drives your already-logged-in Chrome via the DevTools protocol.

See [plugins/x-article-to-markdown/skills/x-article-to-markdown/SKILL.md](plugins/x-article-to-markdown/skills/x-article-to-markdown/SKILL.md) for details.

### hermes-tweet

Guides agents through Hermes Tweet, the native Hermes Agent X/Twitter plugin for Xquik. It covers endpoint discovery, read-only calls, approval-gated action calls, runtime checks, and credential safety.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

See [plugins/hermes-tweet/skills/hermes-tweet/SKILL.md](plugins/hermes-tweet/skills/hermes-tweet/SKILL.md) for details.

## Repository structure

```
package.json                       # npx installer (`npx blockedpath-skills`)
bin/install.js
.claude-plugin/marketplace.json    # marketplace catalog (Claude Code; also read by Codex as a legacy path)
plugins/
  <plugin-name>/
    package.json                   # optional: publish plugin to npm as an alternate source
    .claude-plugin/plugin.json     # plugin manifest for Claude Code
    .codex-plugin/plugin.json      # plugin manifest for Codex
    skills/<skill-name>/SKILL.md   # skill definition, shared by both
```

To add a new plugin, create a directory under `plugins/` with its own `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, then add an entry to `.claude-plugin/marketplace.json`.

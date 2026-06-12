# blockedpath-skills

A [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) containing skills and plugins for [Claude Code](https://claude.com/claude-code).

## Installation

```
/plugin marketplace add BlockedPath/Skills
```

Then install individual plugins:

```
/plugin install x-article-to-markdown@blockedpath-skills
```

## Plugins

### x-article-to-markdown

Scrapes an X (Twitter) long-form Article into a local Markdown file, faithfully preserving its structure (headings, formatting, lists, blockquotes, links) and downloading images for offline viewing. X Articles are login-gated and client-rendered, so this skill drives your already-logged-in Chrome via the DevTools protocol.

See [plugins/x-article-to-markdown/skills/x-article-to-markdown/SKILL.md](plugins/x-article-to-markdown/skills/x-article-to-markdown/SKILL.md) for details.

## Repository structure

```
.claude-plugin/marketplace.json   # marketplace catalog
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json     # plugin manifest
    skills/<skill-name>/SKILL.md   # skill definition
```

To add a new plugin, create a directory under `plugins/` with its own `.claude-plugin/plugin.json`, then add an entry to `.claude-plugin/marketplace.json`.

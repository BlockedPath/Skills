# blockedpath-skills

A plugin marketplace containing skills and plugins for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex).

## Installation

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

## Repository structure

```
.claude-plugin/marketplace.json   # marketplace catalog (Claude Code; also read by Codex as a legacy path)
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json     # plugin manifest for Claude Code
    .codex-plugin/plugin.json      # plugin manifest for Codex
    skills/<skill-name>/SKILL.md   # skill definition, shared by both
```

To add a new plugin, create a directory under `plugins/` with its own `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, then add an entry to `.claude-plugin/marketplace.json`.

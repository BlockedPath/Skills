# Contributing

Thanks for your interest in contributing to this plugin marketplace!

## Adding a new plugin

1. Create a new directory under `plugins/<plugin-name>/`.
2. Add a Claude Code manifest at `plugins/<plugin-name>/.claude-plugin/plugin.json`.
3. Add a Codex manifest at `plugins/<plugin-name>/.codex-plugin/plugin.json` pointing `"skills"` at `./skills/`.
4. Add the skill itself at `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
5. Register the plugin in `.claude-plugin/marketplace.json` with a `name`, `source`, and `description`.
6. Validate before opening a PR:

   ```
   claude plugin validate .
   claude plugin validate ./plugins/<plugin-name>
   ```

## Updating an existing plugin

- Bump `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json` (and the Codex manifest if relevant) so users receive the update.
- Re-run `claude plugin validate .` to confirm nothing is broken.

## Publishing to npm

The root `package.json` (`blockedpath-skills`) powers `npx blockedpath-skills` (see [bin/install.js](bin/install.js)). Bump its `version` and run `npm publish` after meaningful changes to the installer.

Each plugin may also have its own `plugins/<plugin-name>/package.json` so it can be referenced as an npm `source` in `marketplace.json` (e.g. `@blockedpath/x-article-to-markdown`). Publish with `npm publish --access public` from that plugin's directory if you want to offer this as an alternate source.

## Pull requests

- Keep changes scoped to a single plugin or concern where possible.
- Describe what changed and why in the PR description.
- Make sure validation passes (see above) before requesting review.

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to abide by it.

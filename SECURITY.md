# Security Policy

## Reporting a Vulnerability

If you discover a security issue in one of these plugins or skills (for example, unsafe handling of credentials, unintended code execution, or a scraping script that exposes data), please report it privately rather than opening a public issue.

- Open a [private security advisory](https://github.com/BlockedPath/Skills/security/advisories/new), or
- Contact [@BlockedPath](https://github.com/BlockedPath) directly via GitHub.

Please include:

- The plugin/skill affected
- Steps to reproduce
- The potential impact

We'll acknowledge reports as soon as possible and work on a fix before public disclosure.

## Automated scanning

This repository runs:

- [CodeQL](https://github.com/BlockedPath/Skills/actions/workflows/codeql.yml) for static analysis of JS/Python sources
- [OpenSSF Scorecard](https://scorecard.dev/viewer/?uri=github.com/BlockedPath/Skills) for supply-chain security posture
- [Dependabot](.github/dependabot.yml) for dependency and GitHub Actions updates

## Scope notes

Some skills in this marketplace (e.g. `x-article-to-markdown`) drive a local browser via the DevTools Protocol. They operate against your already-authenticated browser session and run locally — review any script before running it if you have concerns about scope or permissions.

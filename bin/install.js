#!/usr/bin/env node
'use strict';

const { spawnSync } = require('child_process');

const MARKETPLACE_REPO = 'BlockedPath/Skills';
const MARKETPLACE_NAME = 'blockedpath-skills';
const PLUGINS = ['x-article-to-markdown'];

function commandExists(cmd) {
  const result = spawnSync(cmd, ['--version'], { stdio: 'ignore' });
  return !result.error;
}

function run(cmd, args) {
  console.log(`\n$ ${cmd} ${args.join(' ')}`);
  const result = spawnSync(cmd, args, { stdio: 'inherit' });
  return result.status === 0;
}

let found = false;

if (commandExists('claude')) {
  found = true;
  console.log('== Claude Code ==');
  run('claude', ['plugin', 'marketplace', 'add', MARKETPLACE_REPO]);
  for (const plugin of PLUGINS) {
    run('claude', ['plugin', 'install', `${plugin}@${MARKETPLACE_NAME}`]);
  }
} else {
  console.log('Claude Code CLI not found, skipping (https://claude.com/claude-code)');
}

if (commandExists('codex')) {
  found = true;
  console.log('\n== Codex ==');
  run('codex', ['plugin', 'marketplace', 'add', MARKETPLACE_REPO]);
  console.log(
    `\nMarketplace added. Run "codex /plugins" to install: ${PLUGINS.join(', ')}`
  );
} else {
  console.log('Codex CLI not found, skipping (https://developers.openai.com/codex)');
}

if (!found) {
  console.error(
    '\nNeither the Claude Code nor Codex CLI was found on your PATH. ' +
      'Install one of them first, then re-run this command.'
  );
  process.exit(1);
}

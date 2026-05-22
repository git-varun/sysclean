# SysClean Runbook

## Start the daemon
\`\`\`bash
sudo systemctl start syscleand
\`\`\`

## Submit a task
\`\`\`bash
sysclean-cli clean
\`\`\`

## View Queue
\`\`\`bash
sysclean-cli tui
\`\`\`

## Troubleshooting
- If tasks are stuck in \`EXECUTING\`, restart daemon. Crash recovery will mark them \`FAILED\`.
- Check logs in \`~/.local/share/sysclean/events.jsonl\`.

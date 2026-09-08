"""Scheduled SEO refreshes publish only when the approved inventory has changed."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
needed = True
if os.environ.get('GITHUB_EVENT_NAME') == 'schedule':
    local = json.loads((ROOT / '_site/assets/data/marketplace-snapshot.json').read_text())
    try:
        result = subprocess.run([
            'curl', '--fail', '--silent', '--show-error', '--max-time', '15',
            '-H', 'Cache-Control: no-cache',
            'https://timmuasmartcity.com/assets/data/marketplace-snapshot.json',
        ], capture_output=True, text=True)
        if result.returncode == 0:
            live = json.loads(result.stdout)
            needed = local['fingerprint'] != live.get('fingerprint')
    except (ValueError, OSError):
        pass  # Conservatively publish if the previous snapshot cannot be checked.
line = f'needed={str(needed).lower()}'
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write(line + '\n')
print(line)

# SPDX-License-Identifier: GPL-3.0-only
"""Verify each platform payload against its reviewed localization bytes."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
expected_name='release_payload_expected_windows.json' if sys.platform=='win32' else 'release_payload_expected.json'
expected = json.loads((ROOT / 'review' / expected_name).read_text(encoding='utf-8'))
payload = ROOT / 'installer/payload'
actual = json.loads((payload / 'manifest.json').read_text(encoding='utf-8'))
assert actual['version'] == expected['version'], 'Wrong payload version'
assert actual['files'] == expected['files'], 'Release payload differs from the reviewed build'
assert len(actual['files']) == 25, 'Incomplete localization payload'
for name, digest in expected['files'].items():
    assert hashlib.sha256((payload / 'mod' / name).read_bytes()).hexdigest() == digest, name
print('Verified all 25 assets against the reviewed release build')

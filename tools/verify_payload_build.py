# SPDX-License-Identifier: GPL-3.0-only
"""Require identical localization bytes on Linux and Windows release builds."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
expected = json.loads((ROOT / 'review/release_payload_expected.json').read_text(encoding='utf-8'))
payload = ROOT / 'installer/payload'
actual = json.loads((payload / 'manifest.json').read_text(encoding='utf-8'))
assert actual['version'] == expected['version'], 'Wrong payload version'
assert actual['files'] == expected['files'], 'Release payload differs from the reviewed build'
assert len(actual['files']) == 25, 'Incomplete localization payload'
for name, digest in expected['files'].items():
    assert hashlib.sha256((payload / 'mod' / name).read_bytes()).hexdigest() == digest, name
print('Verified all 25 assets against the reviewed release build')

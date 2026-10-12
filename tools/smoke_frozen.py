# SPDX-License-Identifier: GPL-3.0-only
"""Exercise the real packaged binary and its video decoder without installing."""
import os,sys,subprocess,json
from pathlib import Path
executable=Path(sys.argv[1]).resolve();target=Path(sys.argv[2]).resolve();target.parent.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,QT_QPA_PLATFORM='offscreen')
result=subprocess.run([str(executable),'--screenshot',str(target)],env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
if result.returncode:
    print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
report=json.loads(Path(str(target)+'.json').read_text(encoding='utf-8'))
assert report['video_frames']>3 and report['duration_ms']>15000 and not report['video_error'],report
assert report['payload_assets']==25,report
print('Packaged application and video playback verified:',report)

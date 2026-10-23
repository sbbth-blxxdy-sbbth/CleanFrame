"""Build and sign with the workspace-local official Tizen SDK (macOS).

Uses the signing profile that Certificate Manager saved in the SDK data folder.
Set "profile" in .local/device.json to choose another profile name.
"""
from pathlib import Path
import json
import subprocess
import zipfile
from font_assets import write_widget_archive

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / '.local/tizen-sdk'
CLI = SDK / 'tools/ide/bin/tizen'
if not CLI.exists():
    raise SystemExit('Local SDK missing. See docs/development.md.')
config_file = ROOT / '.local/device.json'
config = json.loads(config_file.read_text()) if config_file.exists() else {}
profile = config.get('profile', 'DieterHome')
dist = ROOT / 'dist'
dist.mkdir(exist_ok=True)
unsigned = dist / 'CleanFrame-unsigned.wgt'
write_widget_archive(unsigned)
signed_dir = dist / 'signed'
signed_dir.mkdir(exist_ok=True)
# The terminal stays attached, so the SDK can ask for a certificate password if the profile does not store one.
result = subprocess.run([str(CLI), 'package', '-t', 'wgt', '-s', profile, '-o', str(signed_dir), '--', str(unsigned)], stdout=subprocess.PIPE, text=True, timeout=180)
print(result.stdout, end='')
if result.returncode or 'is created successfully' not in result.stdout:
    raise SystemExit('SDK did not confirm a signed package.')
signed = signed_dir / unsigned.name
with zipfile.ZipFile(signed) as package:
    if not {'author-signature.xml', 'signature1.xml'}.issubset(package.namelist()):
        raise SystemExit('Package is missing its signing files.')
target = dist / 'CleanFrame.wgt'
target.write_bytes(signed.read_bytes())
print('Signed widget created: ' + str(target))

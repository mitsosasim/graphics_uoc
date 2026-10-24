"""Reassemble the original Windows build ZIP and verify its SHA-256."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 folder=ROOT/'assignments/04/windows-build'
 manifest=json.loads((folder/'manifest.json').read_text())
 output=ROOT/'build/runner-windows.zip'
 output.parent.mkdir(exist_ok=True)
 temporary=output.with_suffix('.partial')
 digest=hashlib.sha256()
 with temporary.open('wb') as stream:
  for part in manifest['parts']:
   data=(folder/part['name']).read_bytes()
   if hashlib.sha256(data).hexdigest()!=part['sha256']:raise ValueError('Damaged part: '+part['name'])
   digest.update(data);stream.write(data)
 if digest.hexdigest()!=manifest['sha256']:raise ValueError('Archive checksum mismatch')
 temporary.replace(output)
 print('Verified original archive:',output)
 print('Extract all files, then open Runner Game.exe on Windows.')
if __name__=='__main__':main()

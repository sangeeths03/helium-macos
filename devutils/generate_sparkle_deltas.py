import os
import argparse
import subprocess
import tempfile

from time import sleep
from requests import request

class mount(object):
    def __init__(self, dmg, mountpoint):
      self.dmg = dmg
      self.mountpoint = mountpoint
    def __enter__(self):
      subprocess.check_output([ 'hdiutil', 'attach', self.dmg, '-mountpoint', self.mountpoint ])
    def __exit__(self, *args, **kwargs):
      subprocess.check_output([ 'hdiutil', 'detach', '-force', self.mountpoint ])


def get_asset_url(release, arch):
  for asset in release['assets']:
      if asset['name'].endswith(f'_{arch}-macos.dmg'):
        return asset['browser_download_url']
  assert(False)


def get_historic_dmg_urls():
  repo = os.environ.get('GITHUB_REPOSITORY', 'imputnet/helium-macos')
  response = request('GET', f'https://api.github.com/repos/{repo}/releases?per_page=5')
  response.raise_for_status()

  urls = {}

  response = response.json()
  for release in response:
    version = release['tag_name'].split('-')[0]
    x86_url = get_asset_url(release, 'x86_64')
    arm_url = get_asset_url(release, 'arm64')
    urls[version] = (arm_url, x86_url)

  return urls


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--x86', help='.dmg')
  parser.add_argument('--arm', help='.dmg')
  parser.add_argument('--out', help='dir', required=True)

  args = parser.parse_args()
  return (args.arm, args.x86, args.out)


def do_diff(old_path, new_path, out_path):
  print(f'diffing: ({old_path} ~ {new_path}) -> {out_path}')
  subprocess.check_output([
    'BinaryDelta', 'create', '--version', '4',
    old_path, new_path, out_path
  ])


def generate_delta_for(version, urls, args):
  for i, arch in enumerate(['arm64', 'x86_64']):
    if args[i] is None:
      print(f'skipping {arch}')
      continue

    with tempfile.NamedTemporaryFile(suffix='.dmg') as f:
      with request('GET', urls[i], stream=True) as r:
        r.raise_for_status()
        f.write(r.content)
      print(f.name)
      with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        with mount(f.name, d1), mount(args[i], d2):
          do_diff(d1 + '/Helium.app', d2 + '/Helium.app', f'{args[2]}/{version}-{arch}.delta')


if __name__ == '__main__':
  args = parse_args()
  versions = get_historic_dmg_urls()
  for version in versions:
    print(f'doing {version}')
    generate_delta_for(version, versions[version], args)

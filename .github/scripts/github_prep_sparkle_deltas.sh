#!/bin/bash
set -ex

brew install sparkle
xattr -cr /opt/homebrew/Caskroom/sparkle/*/bin/BinaryDelta
export PATH="$(echo /opt/homebrew/Caskroom/sparkle/*/bin):$PATH"

python3 ./devutils/generate_sparkle_deltas.py "$@"

echo 'deltas<<EOF' >> $GITHUB_OUTPUT
find ./release_asset/ -name '*.delta' >> $GITHUB_OUTPUT
echo EOF >> $GITHUB_OUTPUT

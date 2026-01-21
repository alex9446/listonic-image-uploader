#!/bin/sh

set -e

CURRENT_PATH="$(pwd)"

cd "$(dirname "$(readlink -f "$0")")"

. venv/bin/activate

set -a
. ./.env.local
set +a

python3 -m src --image-path "$CURRENT_PATH"

# Command to run it from any folder
# cd ~/.local/bin/ && ln -s [DIRNAME]/run.sh listonic-image-uploader

#!/usr/bin/env fish

set -x https_proxy "<proxy if needed>"
set -x DISCORD_TOKEN "<discord token>"
set -x GEMINI_TOKEN "<gemini token>"

uv run -m src.main

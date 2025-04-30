#!/usr/bin/env fish

# Optional: if you need a proxy
set -x https_proxy "<proxy if needed>"

# token for your discord bot
set -x DISCORD_TOKEN "<discord token>"
# how much messages your bot remembers
set -x DISCORD_HISTORY_MAX_LEN 500

# gemini api key
set -x GEMINI_TOKEN "<gemini token>"
# gemini model code
set -x GEMINI_MODEL gemini-2.5-flash-preview-04-17
# gemini model prompt
set -x GEMINI_PROMPT "<gemini model prompt>"


uv run -m src.main

#!/bin/bash
# usage: build_run.sh steps.js out.js  — wraps lib + steps into one Playwright MCP function
d="$(cd "$(dirname "$0")" && pwd)"
{ echo "async (page) => {"; cat "$d/pw_lib.inc.js"; cat "$1"; echo "}"; } > "$2"

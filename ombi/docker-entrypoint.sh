#!/bin/sh
set -eu

template_index="/app/ombi/index.html.template"
runtime_index="/config/runtime/index.html"

mkdir -p "$(dirname "$runtime_index")"
cp -f "$template_index" "$runtime_index"

exec /app/ombi/Ombi "$@"

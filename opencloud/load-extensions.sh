#!/bin/sh
set -e

DEFAULT_TARGET_DIR="/var/lib/opencloud/web-extensions"
target_dir="${1:-${TARGET_DIR:-$DEFAULT_TARGET_DIR}}"

if [ -z "$target_dir" ]; then
  echo "ERROR: Target directory is not set"
  exit 1
fi

/bin/mkdir -p "$target_dir"
echo "Starting OpenCloud extensions loader into $target_dir..."

# Process all environment variables starting with OC_EXTENSION_
for var in $(/usr/bin/env | /bin/grep ^OC_EXTENSION_ | /usr/bin/cut -d= -f1); do
  # Get the extension name (remove OC_EXTENSION_ prefix)
  extension_name="${var#OC_EXTENSION_}"
  # Use eval for POSIX-compliant indirect variable expansion
  extension_url=""
  eval "extension_url=\$$var"
  echo "Loading extension $extension_name from $extension_url"
  
  # Create a temporary directory for downloads
  temp_dir="$(/bin/mktemp -d)"
  if [ ! -d "$temp_dir" ]; then
    echo "ERROR: Failed to create temporary directory"
    exit 1
  fi
  
  zip_file="$temp_dir/extension.zip"
  
  # Download and extract the extension; any failure must fail the build
  if ! /usr/bin/curl --fail --location --silent --show-error -o "$zip_file" "$extension_url"; then
    echo "ERROR: Failed to download $extension_name" >&2
    /bin/rm -rf "$temp_dir"
    exit 1
  fi

  if ! /usr/bin/unzip -o -q "$zip_file" -d "$target_dir"; then
    echo "ERROR: Failed to extract $extension_name" >&2
    /bin/rm -rf "$temp_dir"
    exit 1
  fi
  echo "Loaded extension $extension_name into $target_dir"

  # Clean up
  /bin/rm -rf "$temp_dir"

  /bin/ls -la "$target_dir"
done

echo "OpenCloud extensions loading completed"

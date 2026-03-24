#!/bin/sh

set -eu

config_dir=/config
tmpdir="${TMPDIR:-/config/tmp}"

if [ ! -d "${config_dir}" ]; then
    echo "Error: ${config_dir} is missing. Mount a writable volume at ${config_dir}." >&2
    exit 1
fi

if [ ! -w "${config_dir}" ]; then
    echo "Error: ${config_dir} is not writable by uid $(id -u) gid $(id -g). Ensure the mounted volume is writable by 10001:10001." >&2
    exit 1
fi

if ! mkdir -p "${tmpdir}"; then
    echo "Error: unable to create TMPDIR '${tmpdir}'. Ensure ${config_dir} is writable or override TMPDIR to a writable path." >&2
    exit 1
fi

write_test="${tmpdir}/.lidarr-write-test"

if ! : > "${write_test}"; then
    echo "Error: TMPDIR '${tmpdir}' is not writable by uid $(id -u) gid $(id -g)." >&2
    exit 1
fi

rm -f "${write_test}"

exec /app/bin/Lidarr --nobrowser --data=/config "$@"

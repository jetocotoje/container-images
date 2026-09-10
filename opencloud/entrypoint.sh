#!/bin/sh
set -e

echo "Checking presence of opencloud.yaml config"
if [ ! -f /var/lib/opencloud/opencloud.yaml ]; then
  echo "Creating a new opencloud config"
  /usr/bin/opencloud init --insecure=false > /dev/null;
  /bin/mv /etc/opencloud/opencloud.yaml /var/lib/opencloud/;
else
  echo "Config already exists";
fi

/bin/ln -sf /var/lib/opencloud/opencloud.yaml /etc/opencloud/opencloud.yaml;

if [ -r /etc/opencloud-configs ]; then
  if /bin/ls /etc/opencloud-configs/*.yaml >/dev/null 2>&1; then
    echo "Copying opencloud config files";
    /bin/cp -L /etc/opencloud-configs/*.yaml /etc/opencloud/;
  else
    echo "No custom configuration files in /etc/opencloud-configs. Skipping config copy."
  fi
else
  echo "Warning: /etc/opencloud-configs is not readable. Skipping config copy." >&2
fi

# Volume mounts (k8s PVCs) shadow extensions baked into the image; refresh
# them from the immutable copy so volumes stay in lockstep with image content.
echo "Syncing web extensions"
/bin/mkdir -p /var/lib/opencloud/web-extensions
/bin/cp -fR /opt/web-extensions/. /var/lib/opencloud/web-extensions/

echo "Starting Opencloud"

exec /usr/bin/opencloud server "$@"

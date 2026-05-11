#!/usr/bin/env bash
set -Eeuo pipefail

: "${MODE:=standalone}"
: "${WEBPORT:=8080}"
: "${TITLE:=LibreSpeed}"
: "${TAGLINE:=No Flash, No Java, No Websockets, No Bullsh*t}"
: "${TELEMETRY:=false}"
: "${PASSWORD:=}"
: "${ENABLE_ID_OBFUSCATION:=false}"
: "${REDACT_IP_ADDRESSES:=false}"
: "${USE_NEW_DESIGN:=false}"

SOURCE_DIR=${LIBRESPEED_SOURCE_DIR:-/opt/librespeed}
RUNTIME_DIR=${LIBRESPEED_RUNTIME_DIR:-/tmp/librespeed}
WEBROOT=$RUNTIME_DIR/www
APACHE_ROOT=$RUNTIME_DIR/apache
APACHE_CONF_DIR=$APACHE_ROOT/conf
APACHE_RUN_DIR=$APACHE_ROOT/run
APACHE_LOCK_DIR=$APACHE_ROOT/lock
APACHE_LOG_DIR=$APACHE_ROOT/log

html_escape() {
  printf '%s' "$1" | sed \
    -e 's/&/\&amp;/g' \
    -e 's/</\&lt;/g' \
    -e 's/>/\&gt;/g' \
    -e 's/"/\&quot;/g' \
    -e "s/'/\&#39;/g"
}

sed_escape() {
  printf '%s\n' "$1" | sed 's/[&/\\]/\\&/g; s/\$/\\$/g'
}

sed_replacement_escape() {
  printf '%s\n' "$1" | sed 's/[&|\\]/\\&/g'
}

php_string_escape() {
  local value=$1
  value=${value//\\/\\\\}
  value=${value//\'/\\\'}
  printf '%s' "$value"
}

set_php_string() {
  local file=$1 name=$2 value=$3 escaped replacement
  escaped=$(php_string_escape "$value")
  replacement=$(sed_replacement_escape "$escaped")
  sed -i "s|\\\$$name = '.*'|\\\$$name = '$replacement'|g" "$file"
}

require_writable_dir() {
  local dir=$1 reason=$2
  if [ ! -d "$dir" ] || [ ! -w "$dir" ]; then
    echo "ERROR: $dir must be a writable directory ($reason)." >&2
    exit 1
  fi
}

case "$MODE" in
  standalone|frontend|backend|dual) ;;
  *) echo "ERROR: MODE must be standalone, frontend, backend, or dual." >&2; exit 1 ;;
esac

case "$WEBPORT" in
  ''|*[!0-9]*) echo "ERROR: WEBPORT must be numeric." >&2; exit 1 ;;
esac

if [ "$WEBPORT" -lt 1024 ]; then
  echo "ERROR: WEBPORT must be >= 1024 for rootless Apache." >&2
  exit 1
fi

require_writable_dir /tmp "runtime webroot and Apache config"

case "$RUNTIME_DIR" in
  /tmp|/tmp/*) ;;
  *) echo "ERROR: LIBRESPEED_RUNTIME_DIR must be under /tmp for safe read-only operation." >&2; exit 1 ;;
esac

if [ ! -d "$SOURCE_DIR" ]; then
  echo "ERROR: $SOURCE_DIR must exist." >&2
  exit 1
fi

rm -rf "$WEBROOT" "$APACHE_ROOT"
mkdir -p "$WEBROOT" "$APACHE_CONF_DIR" "$APACHE_RUN_DIR" "$APACHE_LOCK_DIR" "$APACHE_LOG_DIR"

echo "Setting up LibreSpeed runtime..."
echo "MODE: $MODE"
echo "USE_NEW_DESIGN: $USE_NEW_DESIGN"
echo "SERVER_LIST_URL: ${SERVER_LIST_URL:-}"
echo "WEBPORT: $WEBPORT"
echo "REDACT_IP_ADDRESSES: $REDACT_IP_ADDRESSES"
echo "DB_TYPE: ${DB_TYPE:-}"
echo "ENABLE_ID_OBFUSCATION: $ENABLE_ID_OBFUSCATION"
echo "GDPR_EMAIL: ${GDPR_EMAIL:-}"

cp "$SOURCE_DIR"/*.js "$WEBROOT"/
cp "$SOURCE_DIR/config.json" "$SOURCE_DIR/design-switch.js" "$SOURCE_DIR/favicon.ico" "$WEBROOT"/

if [[ "$MODE" == "standalone" || "$MODE" == "dual" ]]; then
  cp -R "$SOURCE_DIR/backend" "$WEBROOT/backend"
  if [ -n "${IPINFO_APIKEY:-}" ]; then
    set_php_string "$WEBROOT/backend/getIP_ipInfo_apikey.php" IPINFO_APIKEY "$IPINFO_APIKEY"
  fi
fi

if [ "$MODE" = "backend" ]; then
  cp -R "$SOURCE_DIR/backend/." "$WEBROOT"
  if [ -n "${IPINFO_APIKEY:-}" ]; then
    set_php_string "$WEBROOT/getIP_ipInfo_apikey.php" IPINFO_APIKEY "$IPINFO_APIKEY"
  fi
fi

if [[ "$MODE" == "frontend" || "$MODE" == "dual" || "$MODE" == "standalone" ]]; then
  cp "$SOURCE_DIR/index.html" "$SOURCE_DIR/index-classic.html" "$SOURCE_DIR/index-modern.html" "$WEBROOT"/
  mkdir -p "$WEBROOT/styling" "$WEBROOT/javascript" "$WEBROOT/images" "$WEBROOT/fonts"
  cp -R "$SOURCE_DIR/frontend/styling/." "$WEBROOT/styling/"
  cp -R "$SOURCE_DIR/frontend/javascript/." "$WEBROOT/javascript/"
  cp -R "$SOURCE_DIR/frontend/images/." "$WEBROOT/images/"
  cp -R "$SOURCE_DIR/frontend/fonts/." "$WEBROOT/fonts/" 2>/dev/null || true
  cp "$SOURCE_DIR/frontend/settings.json" "$WEBROOT/settings.json" 2>/dev/null || true

  if [ -f /servers.json ]; then
    echo "using mounted /servers.json for server-list.json"
    cp /servers.json "$WEBROOT/server-list.json"
  else
    echo "no /servers.json found, create one for local host"
    printf '%s\n' '[{"name":"local","server":"/backend", "dlURL":"garbage.php", "ulURL":"empty.php", "pingURL":"empty.php", "getIpURL":"getIP.php", "sponsorName":"", "sponsorURL":"", "id":1}]' > "$WEBROOT/server-list.json"
  fi

  if [ -n "${SERVER_LIST_URL:-}" ]; then
    echo "using SERVER_LIST_URL for frontend server list"
    server_list_url_escaped=$(sed_escape "$SERVER_LIST_URL")
    sed -i "s/var SPEEDTEST_SERVERS = \"server-list.json\";/var SPEEDTEST_SERVERS = \"$server_list_url_escaped\";/" "$WEBROOT/index-modern.html"
    sed -i "s/var SPEEDTEST_SERVERS = \\[/var SPEEDTEST_SERVERS = \"$server_list_url_escaped\";\\n\\t\\t\\/\\*/" "$WEBROOT/index-classic.html"
  fi

  if [ -n "$TITLE" ]; then
    title_one_line=${TITLE//$'\r'/}
    title_one_line=${title_one_line//$'\n'/ }
    title_escaped=$(sed_escape "$(html_escape "$title_one_line")")
    sed -i "s/<title>LibreSpeed<\\/title>/<title>$title_escaped<\\/title>/g; s/<h1>LibreSpeed<\\/h1>/<h1>$title_escaped<\\/h1>/g" "$WEBROOT/index-classic.html"
    sed -i "s/<title>LibreSpeed<\\/title>/<title>$title_escaped<\\/title>/g" "$WEBROOT/index.html"
    sed -i "s/<title>LibreSpeed - Free and Open Source Speedtest<\\/title>/<title>$title_escaped - Free and Open Source Speedtest<\\/title>/g; s/<h1>Free and Open Source Speedtest\\.<\\/h1>/<h1>$title_escaped<\\/h1>/g" "$WEBROOT/index-modern.html"
  fi

  if [ -n "$TAGLINE" ]; then
    tagline_one_line=${TAGLINE//$'\r'/}
    tagline_one_line=${tagline_one_line//$'\n'/ }
    tagline_escaped=$(sed_escape "$(html_escape "$tagline_one_line")")
    sed -i "s/<p class=\"tagline\">No Flash, No Java, No Websockets, No Bullsh\\*t<\\/p>/<p class=\"tagline\">$tagline_escaped<\\/p>/g" "$WEBROOT/index-modern.html"
  fi

  if [ -z "${GDPR_EMAIL:-}" ] && [ -n "${EMAIL:-}" ]; then
    echo "WARNING: EMAIL env var is deprecated, please use GDPR_EMAIL instead" >&2
    GDPR_EMAIL=$EMAIL
  fi

  if [ -n "${GDPR_EMAIL:-}" ]; then
    gdpr_email_escaped=$(sed_escape "$GDPR_EMAIL")
    for html_file in "$WEBROOT/index-modern.html" "$WEBROOT/index-classic.html"; do
      [ -f "$html_file" ] && sed -i "s/TO BE FILLED BY DEVELOPER/$gdpr_email_escaped/g; s/PUT@YOUR_EMAIL.HERE/$gdpr_email_escaped/g" "$html_file"
    done
  fi
fi

if [ "$USE_NEW_DESIGN" = "true" ]; then
  sed -i 's/"useNewDesign": false/"useNewDesign": true/' "$WEBROOT/config.json"
fi

if [[ "$TELEMETRY" == "true" && ("$MODE" == "frontend" || "$MODE" == "standalone" || "$MODE" == "dual") ]]; then
  if [ -z "$PASSWORD" ]; then
    echo "ERROR: PASSWORD must be set when TELEMETRY=true." >&2
    exit 1
  fi

  cp -R "$SOURCE_DIR/results" "$WEBROOT/results"
  [ -f "$WEBROOT/settings.json" ] && sed -i 's/telemetry_level": ".*"/telemetry_level": "basic"/' "$WEBROOT/settings.json"

  if [ "$MODE" = "frontend" ]; then
    mkdir -p "$WEBROOT/backend"
    cp "$SOURCE_DIR/backend/getIP_util.php" "$WEBROOT/backend"
  fi

  telemetry_settings=$WEBROOT/results/telemetry_settings.php
  case "${DB_TYPE:-sqlite}" in
    mysql)
      set_php_string "$telemetry_settings" db_type mysql
      set_php_string "$telemetry_settings" MySql_username "${DB_USERNAME:-}"
      set_php_string "$telemetry_settings" MySql_password "${DB_PASSWORD:-}"
      set_php_string "$telemetry_settings" MySql_hostname "${DB_HOSTNAME:-}"
      set_php_string "$telemetry_settings" MySql_databasename "${DB_NAME:-}"
      [ -n "${DB_PORT:-}" ] && set_php_string "$telemetry_settings" MySql_port "$DB_PORT"
      ;;
    postgresql)
      set_php_string "$telemetry_settings" db_type postgresql
      set_php_string "$telemetry_settings" PostgreSql_username "${DB_USERNAME:-}"
      set_php_string "$telemetry_settings" PostgreSql_password "${DB_PASSWORD:-}"
      set_php_string "$telemetry_settings" PostgreSql_hostname "${DB_HOSTNAME:-}"
      set_php_string "$telemetry_settings" PostgreSql_databasename "${DB_NAME:-}"
      ;;
    sqlite|'')
      require_writable_dir /database "SQLite telemetry database"
      set_php_string "$telemetry_settings" db_type sqlite
      ;;
    *) echo "ERROR: DB_TYPE must be sqlite, mysql, or postgresql." >&2; exit 1 ;;
  esac

  set_php_string "$telemetry_settings" Sqlite_db_file /database/db.sql
  set_php_string "$telemetry_settings" stats_password "$PASSWORD"

  if [ "$ENABLE_ID_OBFUSCATION" = "true" ]; then
    sed -i 's/$enable_id_obfuscation = .*;/$enable_id_obfuscation = true;/g' "$telemetry_settings"
    if [ -n "${OBFUSCATION_SALT:-}" ]; then
      if [[ "$OBFUSCATION_SALT" =~ ^0x[0-9a-fA-F]+$ ]]; then
        printf '%s\n' '<?php' "\$OBFUSCATION_SALT = $OBFUSCATION_SALT;" > "$WEBROOT/results/idObfuscation_salt.php"
      else
        echo "WARNING: Invalid OBFUSCATION_SALT format. It must be a hex string (e.g. 0x1234abcd). Using random salt." >&2
      fi
    fi
  fi

  if [ "$REDACT_IP_ADDRESSES" = "true" ]; then
    sed -i 's/$redact_ip_addresses = .*;/$redact_ip_addresses = true;/g' "$telemetry_settings"
  fi
fi

cp -R /etc/apache2/. "$APACHE_CONF_DIR/"
sed -i "s#^Listen .*#Listen $WEBPORT#g" "$APACHE_CONF_DIR/ports.conf"
sed -i "s#<VirtualHost \*:.*>#<VirtualHost *:$WEBPORT>#g; s#DocumentRoot .*#DocumentRoot $WEBROOT#g; s#ErrorLog .*#ErrorLog /proc/self/fd/2#g; s#CustomLog .*#CustomLog /proc/self/fd/1 combined#g" "$APACHE_CONF_DIR/sites-available/000-default.conf"
cat >> "$APACHE_CONF_DIR/apache2.conf" <<EOF
ServerName localhost
<Directory "$WEBROOT">
    Options FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
EOF

export APACHE_CONFDIR=$APACHE_CONF_DIR
export APACHE_ENVVARS=$APACHE_CONF_DIR/envvars
export APACHE_RUN_USER=librespeed
export APACHE_RUN_GROUP=librespeed
export APACHE_RUN_DIR
export APACHE_LOCK_DIR
export APACHE_LOG_DIR
export APACHE_PID_FILE=$APACHE_RUN_DIR/apache2.pid

echo "Done, starting Apache"
exec apache2 -d "$APACHE_CONF_DIR" -f "$APACHE_CONF_DIR/apache2.conf" -DFOREGROUND

import ssl
import sys
from importlib.metadata import version
from pathlib import Path

sys.path.insert(0, "/app")

import certifi

pinned_version = (
    Path(__file__).with_name("requirements.txt").read_text().splitlines()[0]
    .split("==", 1)[1].split()[0]
)
expected = tuple(map(int, pinned_version.split(".")))
if any(
    tuple(map(int, value.split("."))) != expected
    for value in (certifi.__version__, version("certifi"))
):
    raise SystemExit("Selected certifi does not match its exact dependency pin")

context = ssl.create_default_context(cafile=certifi.where())
if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
    raise SystemExit("Certificate and hostname verification must remain enabled")
certs = context.get_ca_certs()
if not certs:
    raise SystemExit("The certifi trust store is empty")

incident_roots = {
    "emSign ECC Root CA - G3",
    "AAA Certificate Services",
}
names = {
    value
    for cert in certs
    for rdn in cert["subject"]
    for key, value in rdn
    if key == "commonName"
}
remaining = names & incident_roots
if remaining:
    raise SystemExit("Affected roots remain: " + ", ".join(sorted(remaining)))

print(f"certifi {certifi.__version__}: {len(certs)} roots, no affected roots")

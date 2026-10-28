import ssl
import sys
from importlib.metadata import distributions
from pathlib import Path

sys.path[:0] = ["/app/bin", "/app/bin/libs", "/app/bin/custom_libs"]

import certifi
import requests

vendor = Path("/app/bin/libs")
selected = [
    dist for dist in distributions(path=[str(vendor)])
    if dist.metadata["Name"].lower() == "certifi"
]
if len(selected) != 1:
    raise SystemExit("Exactly one vendored certifi distribution is required")

requirement = Path(__file__).with_name("requirements.txt").read_text().splitlines()[0]
pinned_version = requirement.split("==", 1)[1].split()[0]
expected = tuple(map(int, pinned_version.split(".")))
if any(
    tuple(map(int, value.split("."))) != expected
    for value in (certifi.__version__, selected[0].version)
):
    raise SystemExit("Selected certifi does not match its exact dependency pin")

module = Path(certifi.__file__).resolve()
if module != vendor / "certifi/__init__.py":
    raise SystemExit("Certifi must retain its vendored import location")
if Path(selected[0].locate_file("certifi/__init__.py")).resolve() != module:
    raise SystemExit("Certifi module and distribution location disagree")

bundle = Path(certifi.where()).resolve()
if Path(requests.certs.where()).resolve() != bundle:
    raise SystemExit("Requests does not select the updated certifi bundle")
if Path(requests.adapters.DEFAULT_CA_BUNDLE_PATH).resolve() != bundle:
    raise SystemExit("Requests adapter does not select the updated certifi bundle")
if requests.Session().verify is not True:
    raise SystemExit("Requests certificate verification must remain enabled")

context = ssl.create_default_context(cafile=str(bundle))
if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
    raise SystemExit("Certificate and hostname verification must remain enabled")
certs = context.get_ca_certs()
if not certs:
    raise SystemExit("The certifi trust store is empty")

incident_roots = {"emSign ECC Root CA - G3", "AAA Certificate Services"}
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

print(f"Requests selects vendored certifi {certifi.__version__}: {len(certs)} roots, no affected roots")

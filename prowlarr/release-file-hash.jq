# Requires --arg component (runtime, aspnetcore-runtime), version and name (file
# name in the release metadata). Fails unless a non-empty hash is listed.
first(.releases[][$component] | select(.version == $version) | .files[]? | select(.name == $name) | .hash | select(. != ""))
  // error("No SHA-512 for \($name) \($version) in the release metadata")

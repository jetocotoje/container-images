# Requires --arg old/new (runtime versions) and --slurpfile netcore/aspnetcore
# (the new runtime's framework deps.json files).
([$netcore[0], $aspnetcore[0]]
  | map(.targets[.runtimeTarget.name][] | (.runtime // {}) + (.native // {}))
  | add) as $assets
| def runtimepack: startswith("runtimepack.");
  def bump: sub("/" + $old + "$"; "/" + $new);
  def refresh: with_entries(.value = ($assets[.key] // .value));
.libraries |= with_entries(if .key | runtimepack then .key |= bump else . end)
| .targets[.runtimeTarget.name] |= with_entries(
    if .key | runtimepack then
      (.key |= bump)
      | .value |= with_entries(if .key == "runtime" or .key == "native" then .value |= refresh else . end)
    elif .value | has("dependencies") then
      .value.dependencies |= with_entries(if .key | runtimepack then .value = $new else . end)
    else . end)

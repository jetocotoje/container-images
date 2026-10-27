# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG PROWLARR_VERSION=2.6.6.5717@sha256:8ead2b6f1b5d744fc52849d455896809b2d290f2b78b05f1b3fb21f410866b58

FROM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION} AS upstream

FROM --platform=$BUILDPLATFORM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION} AS dotnet

# renovate: datasource=dotnet-version depName=dotnet-runtime
ARG DOTNET_VERSION=8.0.33
ARG TARGETARCH

USER root
WORKDIR /work

COPY --from=upstream /app/bin/*.deps.json /app/bin/Prowlarr.runtimeconfig.json /work/app/
COPY bump-runtime-pack.jq release-file-hash.jq /work/

RUN case "${TARGETARCH}" in \
        amd64) rid='linux-musl-x64' ;; \
        arm64) rid='linux-musl-arm64' ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && mkdir /out \
    && old_version="$(jq -er '[.runtimeOptions.includedFrameworks[]? | select(.name == "Microsoft.NETCore.App") | .version] | first // error("Microsoft.NETCore.App missing from runtimeOptions.includedFrameworks")' app/Prowlarr.runtimeconfig.json)" \
    && if [ "${old_version%%.*}" != "${DOTNET_VERSION%%.*}" ]; then \
        echo "Upstream bundles .NET ${old_version}, a different major than DOTNET_VERSION ${DOTNET_VERSION}; move DOTNET_VERSION to the new major by hand" >&2; exit 1; \
    fi \
    && if [ "$(printf '%s\n' "${old_version}" "${DOTNET_VERSION}" | sort -V | tail -n 1)" = "${old_version}" ]; then \
        echo "Upstream already bundles .NET ${old_version} (>= ${DOTNET_VERSION}); leaving /app/bin as shipped"; exit 0; \
    fi \
    && base_url="https://builds.dotnet.microsoft.com/dotnet" \
    && curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors \
        "${base_url}/release-metadata/${DOTNET_VERSION%.*}/releases.json" -o releases.json \
    && runtime_sha512="$(jq -er --arg component runtime --arg version "${DOTNET_VERSION}" \
        --arg name "dotnet-runtime-${rid}.tar.gz" -f release-file-hash.jq releases.json)" \
    && aspnetcore_sha512="$(jq -er --arg component aspnetcore-runtime --arg version "${DOTNET_VERSION}" \
        --arg name "aspnetcore-runtime-${rid}.tar.gz" -f release-file-hash.jq releases.json)" \
    && curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors \
        "${base_url}/Runtime/${DOTNET_VERSION}/dotnet-runtime-${DOTNET_VERSION}-${rid}.tar.gz" -o runtime.tar.gz \
    && curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors \
        "${base_url}/aspnetcore/Runtime/${DOTNET_VERSION}/aspnetcore-runtime-${DOTNET_VERSION}-${rid}.tar.gz" -o aspnetcore.tar.gz \
    && printf '%s  %s\n' "${runtime_sha512}" runtime.tar.gz "${aspnetcore_sha512}" aspnetcore.tar.gz | sha512sum -c - \
    && mkdir runtime aspnetcore \
    && tar xzf runtime.tar.gz -C runtime ./shared/Microsoft.NETCore.App ./host/fxr \
    && tar xzf aspnetcore.tar.gz -C aspnetcore ./shared/Microsoft.AspNetCore.App \
    && netcore="runtime/shared/Microsoft.NETCore.App/${DOTNET_VERSION}" \
    && aspnetcore="aspnetcore/shared/Microsoft.AspNetCore.App/${DOTNET_VERSION}" \
    && for deps in app/*.deps.json; do \
        jq -e --arg old "${old_version}" --arg new "${DOTNET_VERSION}" \
            --slurpfile netcore "${netcore}/Microsoft.NETCore.App.deps.json" \
            --slurpfile aspnetcore "${aspnetcore}/Microsoft.AspNetCore.App.deps.json" \
            -f bump-runtime-pack.jq "${deps}" > "/out/${deps#app/}" || exit 1; \
    done \
    && jq -e --arg new "${DOTNET_VERSION}" '.runtimeOptions.includedFrameworks[].version = $new' \
        app/Prowlarr.runtimeconfig.json > /out/Prowlarr.runtimeconfig.json \
    && find "${netcore}" "${aspnetcore}" -maxdepth 1 -type f \
        ! -name '*.deps.json' ! -name '*.runtimeconfig.json' ! -name '*.txt' \
        -exec cp -p {} /out/ \; \
    && cp -p "runtime/host/fxr/${DOTNET_VERSION}/libhostfxr.so" /out/ \
    && jq -er '.targets[.runtimeTarget.name] | to_entries[] | select(.key | startswith("runtimepack.")) | .value | (.runtime // {}), (.native // {}) | keys[]' /out/*.deps.json > assets.txt \
    && while read -r asset; do \
        [ -f "/out/${asset}" ] || { echo "Runtime pack asset not overlaid: ${asset}" >&2; exit 1; }; \
    done < assets.txt

FROM upstream

USER root

RUN apk upgrade --no-cache

COPY --from=dotnet --chown=root:root /out/ /app/bin/

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["curl", "--fail", "--silent", "--output", "/dev/null", "http://127.0.0.1:9696/ping"]

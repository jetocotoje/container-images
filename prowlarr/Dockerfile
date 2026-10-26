# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG PROWLARR_VERSION=2.6.5.5623@sha256:0e2e6e9a2a16683a160ff1c6830d8192231a0502ab0d605b416023b2ca225ff9

FROM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION} AS upstream

FROM --platform=$BUILDPLATFORM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION} AS dotnet

# Hashes from https://builds.dotnet.microsoft.com/dotnet/release-metadata/8.0/releases.json
ARG DOTNET_VERSION=8.0.33
ARG DOTNET_RUNTIME_SHA512_X64=70d8a4f126a57459102b837233e03e68e345efdad5b8e5a37ff500b0e5ecfcfa49d465c890a4d974ca7df7e0d30bd0ede1976c21ede239ce704b0c6c8d931c46
ARG DOTNET_RUNTIME_SHA512_ARM64=4a19f344d147804d6261d67cf484c214dfdf470ff9097522b87a8f684b1593fbbd3c7ee4989936d0d8d62b40deb8d53710f946d54a3430ed721be592fa453ca4
ARG ASPNETCORE_RUNTIME_SHA512_X64=b6496baf29a19e8576299fe6e2888eb9406857b7f52697412435c630771a93d0871e76e31c56a74aa8dd728c8047a722861befb18307fe44fdbf59a1ded3e4ce
ARG ASPNETCORE_RUNTIME_SHA512_ARM64=6b85b2b70a0a5cd0dea139ce7b21c99f08c46fc7f323f7c20e98fd923545c51a53debd127291ad47152f8aa8df5d95aead7c1ed1719ac70a522086873304fb58
ARG TARGETARCH

USER root
WORKDIR /work

COPY --from=upstream /app/bin/*.deps.json /app/bin/Prowlarr.runtimeconfig.json /work/app/
COPY bump-runtime-pack.jq /work/

RUN case "${TARGETARCH}" in \
        amd64) rid='linux-musl-x64'; runtime_sha512="${DOTNET_RUNTIME_SHA512_X64}"; aspnetcore_sha512="${ASPNETCORE_RUNTIME_SHA512_X64}" ;; \
        arm64) rid='linux-musl-arm64'; runtime_sha512="${DOTNET_RUNTIME_SHA512_ARM64}"; aspnetcore_sha512="${ASPNETCORE_RUNTIME_SHA512_ARM64}" ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && old_version="$(jq -er '.runtimeOptions.includedFrameworks[] | select(.name == "Microsoft.NETCore.App") | .version' app/Prowlarr.runtimeconfig.json)" \
    && if [ "$(printf '%s\n' "${old_version}" "${DOTNET_VERSION}" | sort -V | tail -n 1)" = "${old_version}" ]; then \
        echo "Upstream already bundles .NET ${old_version} (>= ${DOTNET_VERSION}); switch back to the upstream image" >&2; exit 1; \
    fi \
    && base_url="https://builds.dotnet.microsoft.com/dotnet" \
    && curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors \
        "${base_url}/Runtime/${DOTNET_VERSION}/dotnet-runtime-${DOTNET_VERSION}-${rid}.tar.gz" -o runtime.tar.gz \
    && curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors \
        "${base_url}/aspnetcore/Runtime/${DOTNET_VERSION}/aspnetcore-runtime-${DOTNET_VERSION}-${rid}.tar.gz" -o aspnetcore.tar.gz \
    && printf '%s  %s\n' "${runtime_sha512}" runtime.tar.gz "${aspnetcore_sha512}" aspnetcore.tar.gz | sha512sum -c - \
    && mkdir runtime aspnetcore /out \
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
    && jq -r '.targets[.runtimeTarget.name] | to_entries[] | select(.key | startswith("runtimepack.")) | .value | (.runtime // {}), (.native // {}) | keys[]' /out/*.deps.json \
        | while read -r asset; do \
            [ -f "/out/${asset}" ] || { echo "Runtime pack asset not overlaid: ${asset}" >&2; exit 1; }; \
        done

FROM upstream

USER root

RUN apk upgrade --no-cache

COPY --from=dotnet --chown=root:root /out/ /app/bin/

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["curl", "--fail", "--silent", "--output", "/dev/null", "http://127.0.0.1:9696/ping"]

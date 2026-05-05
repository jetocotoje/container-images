# renovate: datasource=github-releases depName=Ombi-app/Ombi extractVersion="^v(?<version>.*)$"
ARG OMBI_VERSION=4.53.5
ARG TARGETARCH

FROM --platform=$BUILDPLATFORM ubuntu:resolute@sha256:f3d28607ddd78734bb7f71f117f3c6706c666b8b76cbff7c9ff6e5718d46ff64 AS download

ARG OMBI_VERSION
ARG TARGETARCH

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl tar \
    && rm -rf /var/lib/apt/lists/*

RUN case "$TARGETARCH" in \
        amd64) ombi_arch='x64' ;; \
        arm64) ombi_arch='arm64' ;; \
        *) echo "Unsupported TARGETARCH: $TARGETARCH" >&2; exit 1 ;; \
    esac \
    && curl --fail --silent --show-error --location \
        --output /tmp/ombi.tar.gz \
        "https://github.com/Ombi-app/Ombi/releases/download/v${OMBI_VERSION}/linux-${ombi_arch}.tar.gz" \
    && mkdir -p /opt/ombi \
    && tar -xzf /tmp/ombi.tar.gz -C /opt/ombi \
    && rm /tmp/ombi.tar.gz

FROM ubuntu:resolute@sha256:f3d28607ddd78734bb7f71f117f3c6706c666b8b76cbff7c9ff6e5718d46ff64

ARG UID=10001
ARG GID=10001

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates libicu74 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid "$GID" ombi \
    && useradd --uid "$UID" --gid "$GID" --create-home --home-dir /config --shell /usr/sbin/nologin ombi \
    && mkdir -p /app/ombi /config \
    && chmod 700 /config \
    && chown ombi:ombi /config

COPY --from=download /opt/ombi/ /app/ombi/

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN mkdir -p /app/ombi-dist-template \
    && cp -R /app/ombi/ClientApp/dist/. /app/ombi-dist-template/ \
    && chown -R ombi:ombi /app/ombi/ClientApp/dist \
    && chmod 755 /usr/local/bin/docker-entrypoint.sh

WORKDIR /app/ombi

ENV HOME=/config \
    DOTNET_EnableDiagnostics=0

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["/bin/bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/5000 || exit 1; printf 'GET / HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n' >&3; IFS= read -r status <&3 || exit 1; [[ \"$status\" == *' 200 '* ]] || exit 1"]

USER ombi

VOLUME ["/config"]

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["--storage", "/config", "--host", "http://*:5000"]

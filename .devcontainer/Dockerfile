FROM mcr.microsoft.com/devcontainers/base:bookworm

ARG DEBIAN_FRONTEND=noninteractive

# libicu72 is required by the CWTools .NET language server.
# imagemagick + python3-pil cover the DDS/PNG asset pipeline Stellaris uses.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-pil \
        python3-yaml \
        imagemagick \
        fonts-dejavu-core \
        libicu72 \
        make \
        ripgrep \
        jq \
        zip \
        unzip \
        less \
        file \
    && rm -rf /var/lib/apt/lists/*

# Stellaris ships textures as DDS. ImageMagick's stock policy on Debian is
# permissive for DDS, but raise the resource limits so large 4k atlases convert.
RUN sed -i 's/name="memory" value="[^"]*"/name="memory" value="2GiB"/; s/name="disk" value="[^"]*"/name="disk" value="4GiB"/' \
        /etc/ImageMagick-6/policy.xml || true

# Persisted Claude state and the deploy target are bind-mounted at runtime;
# create the mount points up front so ownership is correct even if empty.
RUN mkdir -p /home/vscode/.claude /paradox/stellaris /stellaris \
    && chown -R vscode:vscode /home/vscode/.claude

USER vscode

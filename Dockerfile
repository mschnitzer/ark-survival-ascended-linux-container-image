#######################
# Stage 1: Builder
#######################
FROM ubuntu:24.04@sha256:66460d557b25769b102175144d538d88219c077c678a49af4afca6fbfc1b5252 AS builder

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Package versions for reproducible builds
# renovate: suite=noble depName=python3
ARG PYTHON3_VERSION="3.12.3-0ubuntu2"

# Install minimal build dependencies with pinned versions
RUN apt-get update && apt-get install -y \
    python3=${PYTHON3_VERSION} \
    && rm -rf /var/lib/apt/lists/*

# Install uv - the fast Python package installer (pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv

# Copy only the Python package source code
COPY root/usr/share/asa-ctrl /usr/share/asa-ctrl

# Install the asa-ctrl package using uv (creates entry points automatically)
WORKDIR /usr/share/asa-ctrl
RUN uv pip install --system --break-system-packages --no-cache .

#######################
# Stage 2: Runtime
#######################
FROM ubuntu:24.04@sha256:66460d557b25769b102175144d538d88219c077c678a49af4afca6fbfc1b5252

# Build arguments for dynamic metadata
ARG VERSION=dev
ARG BUILD_DATE=unknown
ARG VCS_REF=unknown

# OCI standard labels
LABEL org.opencontainers.image.title="ARK: Survival Ascended - Dedicated Linux Server"
LABEL org.opencontainers.image.description="Docker container for running ARK: Survival Ascended dedicated servers on Linux using Proton"
LABEL org.opencontainers.image.authors="github@mschnitzer.de"
LABEL org.opencontainers.image.url="https://github.com/jdogwilly/ark-survival-ascended-linux-container-image"
LABEL org.opencontainers.image.source="https://github.com/jdogwilly/ark-survival-ascended-linux-container-image"
LABEL org.opencontainers.image.documentation="https://github.com/jdogwilly/ark-survival-ascended-linux-container-image/blob/main/README.md"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="Community"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Package versions for reproducible builds
# renovate: suite=noble depName=lib32gcc-s1
ARG LIB32GCC_VERSION="14.2.0-4ubuntu2~24.04"
# renovate: suite=noble depName=python3
ARG PYTHON3_VERSION="3.12.3-0ubuntu2"
# renovate: suite=noble depName=wget
ARG WGET_VERSION="1.21.4-1ubuntu4.1"
# renovate: suite=noble depName=tar
ARG TAR_VERSION="1.35+dfsg-3build1"
# renovate: suite=noble depName=unzip
ARG UNZIP_VERSION="6.0-28ubuntu4.1"
# renovate: suite=noble depName=ca-certificates
ARG CA_CERTS_VERSION="20240203"
# renovate: suite=noble depName=libfreetype6
ARG LIBFREETYPE6_VERSION="2.13.2+dfsg-1build3"
# renovate: suite=noble depName=procps
ARG PROCPS_VERSION="2:4.0.4-4ubuntu3.2"

# Install runtime packages only with pinned versions (optimized layer ordering - rarely changes)
RUN apt-get update && apt-get install -y \
    # 32-bit library support for Steam/Proton
    lib32gcc-s1=${LIB32GCC_VERSION} \
    # Core utilities
    python3=${PYTHON3_VERSION} \
    wget=${WGET_VERSION} \
    tar=${TAR_VERSION} \
    unzip=${UNZIP_VERSION} \
    ca-certificates=${CA_CERTS_VERSION} \
    # ASA dependencies
    libfreetype6=${LIBFREETYPE6_VERSION} \
    # Health check utilities
    procps=${PROCPS_VERSION} \
    && rm -rf /var/lib/apt/lists/*

# Create gameserver user and group with specific UID/GID (rarely changes)
RUN groupadd -g 25000 gameserver && \
    useradd -u 25000 -g 25000 -m -d /home/gameserver -s /bin/bash gameserver

# Copy installed Python package from builder (includes asa_ctrl module)
# Note: uv installs to dist-packages on Ubuntu (not site-packages)
RUN mkdir -p /usr/local/lib/python3.12/dist-packages
COPY --from=builder /usr/local/lib/python3.12/dist-packages/asa_ctrl /usr/local/lib/python3.12/dist-packages/asa_ctrl
COPY --from=builder /usr/local/lib/python3.12/dist-packages/asa_ctrl-*.dist-info /usr/local/lib/python3.12/dist-packages/

# Copy entry point executables from builder
COPY --from=builder /usr/local/bin/asa-ctrl /usr/local/bin/asa-ctrl
COPY --from=builder /usr/local/bin/cli-asa-mods /usr/local/bin/cli-asa-mods

# Copy non-Python application files directly from source
COPY root/usr/bin/start_server /usr/bin/start_server
COPY root/usr/bin/healthcheck-liveness /usr/bin/healthcheck-liveness
COPY root/usr/bin/healthcheck-readiness /usr/bin/healthcheck-readiness
COPY root/usr/share/proton /usr/share/proton

# Set permissions for scripts
RUN chmod 0755 /usr/bin/start_server /usr/bin/healthcheck-liveness /usr/bin/healthcheck-readiness

# Switch to gameserver user
USER gameserver
WORKDIR /home/gameserver

# Health check configuration
# - Checks every 30s if the server process is running
# - Allows 10m for initial downloads (SteamCMD + server files + Proton)
# - Requires 3 consecutive failures before marking unhealthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=10m --retries=3 \
    CMD /usr/bin/healthcheck-liveness

# Default entrypoint
ENTRYPOINT ["/usr/bin/start_server"]

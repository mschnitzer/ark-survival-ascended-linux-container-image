#######################
# Stage 1: Builder
#######################
FROM ubuntu:24.04 AS builder

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Install uv - the fast Python package installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy only the Python package source code
COPY root/usr/share/asa-ctrl /usr/share/asa-ctrl

# Install the asa-ctrl package using uv (creates entry points automatically)
WORKDIR /usr/share/asa-ctrl
RUN uv pip install --system --break-system-packages --no-cache .

#######################
# Stage 2: Runtime
#######################
FROM ubuntu:24.04

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

# Install runtime packages only (optimized layer ordering - rarely changes)
RUN apt-get update && apt-get install -y \
    # 32-bit library support for Steam/Proton
    lib32gcc-s1 \
    # Core utilities
    python3 \
    wget \
    tar \
    unzip \
    ca-certificates \
    # ASA dependencies
    libfreetype6 \
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
COPY root/usr/share/proton /usr/share/proton

# Set permissions for start_server script
RUN chmod 0755 /usr/bin/start_server

# Switch to gameserver user
USER gameserver
WORKDIR /home/gameserver

# Default entrypoint
ENTRYPOINT ["/usr/bin/start_server"]

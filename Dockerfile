FROM ubuntu:24.04

LABEL org.opencontainers.image.title="ARK: Survival Ascended - Dedicated Linux Server"
LABEL org.opencontainers.image.description="Docker container for running ARK: Survival Ascended dedicated servers on Linux using Proton"
LABEL org.opencontainers.image.authors="github@mschnitzer.de"
LABEL org.opencontainers.image.source="https://github.com/jdogwilly/ark-survival-ascended-linux-container-image"
LABEL org.opencontainers.image.version="1.5.0"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
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
    # Ruby and development tools
    ruby \
    ruby-dev \
    bundler \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create gameserver user and group with specific UID/GID
RUN groupadd -g 25000 gameserver && \
    useradd -u 25000 -g 25000 -m -d /home/gameserver -s /bin/bash gameserver

# Copy application files
COPY root/usr /usr

# Install Ruby gems
WORKDIR /usr/share/asa-ctrl
RUN bundle install

# Set up permissions and symlinks
RUN chmod 0755 /usr/bin/start_server && \
    chmod 0755 /usr/bin/cli-asa-mods && \
    chmod 0755 /usr/share/asa-ctrl/main.rb && \
    ln -sf /usr/share/asa-ctrl/main.rb /usr/bin/asa-ctrl

# Switch to gameserver user
USER gameserver
WORKDIR /home/gameserver

# Default entrypoint
ENTRYPOINT ["/usr/bin/start_server"]

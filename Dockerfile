# Base image with Ubuntu
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PATH="/root/.local/bin:$PATH"

# Update and install essential tools
RUN apt-get update 
RUN apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    nano \
    python3 \
    python3-pip \
    nodejs \
    npm \
    docker.io \
    docker-compose \
    ssh \
    unzip \
    zip \
    && apt-get clean
    # Install Angular CLI globally
RUN npm install -g @angular/cli \
    && apt-get update && apt-get install -y python3-venv python3-pip \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install virtualenv \
    && mkdir -p /workspace

# Update package lists and install the latest version of OpenJDK
RUN  apt-get install -y openjdk-11-jdk && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /workspace
EXPOSE 3000
EXPOSE 8080
# Default entrypoint
CMD ["bash"]

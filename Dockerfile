# Start from the Ubuntu base image
FROM ubuntu:22.04

# Switch to root user
USER root

# add a non-root user called openfoam
RUN useradd -ms /bin/bash openfoam

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ make cmake wget ca-certificates \
    openmpi-bin libopenmpi-dev flex bison zlib1g-dev \
    && apt-get clean

# Create necessary directories and set ownership to openfoam user
RUN mkdir -p /opt/OpenFOAM && chown -R openfoam:openfoam /opt/OpenFOAM

# Install necessary dependencies and extract OpenFOAM
RUN apt-get update && apt-get install -y wget ca-certificates && apt-get clean \
    && wget -O /tmp/OpenFOAM-v2406.tgz https://dl.openfoam.com/source/v2406/OpenFOAM-v2406.tgz \
    && tar -xzf /tmp/OpenFOAM-v2406.tgz -C /opt/OpenFOAM \
    && rm /tmp/OpenFOAM-v2406.tgz

# Set environment variables for OpenFOAM
RUN echo "source /opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc" >> ~/.bashrc

# Compile OpenFOAM with detailed output
RUN /bin/bash -c "source /opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc && cd /opt/OpenFOAM/OpenFOAM-v2406 && ./Allwmake -j $(nproc) 2>&1 | tee /opt/OpenFOAM/build.log"

# Verify the installation by listing the binaries, if they exist
RUN /bin/bash -c "if [ -d /opt/OpenFOAM/OpenFOAM-v2406/platforms/linuxARM64GccDPInt32Opt/bin ]; then ls /opt/OpenFOAM/OpenFOAM-v2406/platforms/linuxARM64GccDPInt32Opt/bin; else echo 'Build failed, see /opt/OpenFOAM/build.log for details'; fi"

# Switch to a non-root user if necessary
USER openfoam

# Set the working directory
WORKDIR /home/openfoam

# Copy the local directory to the container
COPY . /home/openfoam/case

# Set entrypoint to bash
ENTRYPOINT ["/bin/bash"]

# Optional: Verify the installation by listing the binaries
RUN /bin/bash -c "source /opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc && ls \$FOAM_APPBIN"
# Use the official OpenFOAM Docker image as the base image
FROM openfoam/openfoam10-paraview56

# Ensure we are running as root
USER root

# Run any root-level commands, such as installing packages
RUN apt-get update && apt-get install -y python3-pip

# Set the working directory
WORKDIR /home/openfoam

# Source the OpenFOAM environment
RUN echo "source /opt/openfoam10/etc/bashrc" >> ~/.bashrc

# Copy the local directory to the container
# COPY case /home/openfoam/case


# USER openfoam

RUN pip install pandas

# Set the entrypoint to bash
ENTRYPOINT ["/bin/bash"]

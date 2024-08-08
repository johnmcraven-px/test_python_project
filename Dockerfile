# Use the official OpenFOAM Docker image as the base image
FROM openfoam/openfoam10-paraview56

# Set the working directory
WORKDIR /home/openfoam

# Source the OpenFOAM environment
RUN echo "source /opt/openfoam10/etc/bashrc" >> ~/.bashrc

# Copy the local directory to the container
COPY case /home/openfoam/case

# Set the entrypoint to bash
ENTRYPOINT ["/bin/bash"]

# Use the official OpenFOAM Docker image as the base image
FROM openfoam/openfoam-dev-paraview510

# Set the working directory
WORKDIR /home/openfoam

# Source the OpenFOAM environment
RUN echo "source /opt/openfoam-dev/etc/bashrc" >> ~/.bashrc

# Copy the local directory to the container
COPY . /home/openfoam/case

# Set the entrypoint to bash
ENTRYPOINT ["/bin/bash"]

import subprocess
import os
import pandas as pd
import openfoam_functions as of

# Define the Docker container name
DOCKER_CONTAINER_NAME = "openfoam_container_new2"

def main():
    # Set the number processors 
    num_processors = 4
    
    write_files = True
    
    build_mesh = True
    mesh_par = True
    
    sim_par = True
    run_sim = True


    # Set the case directory inside Docker
    case_dir = "/home/openfoam/case/"  # Directory inside Docker container]
    forces_file = 'case/postProcessing/forces/0/force.dat'


    if write_files:
        # clean up files 
        of.run_command(f"cd {case_dir} && rm -R ./*", DOCKER_CONTAINER_NAME)

        # create directory structure
        of.create_directory_structure_in_container(case_dir, DOCKER_CONTAINER_NAME)

        # move the stl files to the right location
        stl_files_source = os.path.expanduser("./output/geometry_new/")  # STL file on the host
        stl_files_container_location = os.path.join(case_dir, "constant/triSurface/")

    
        # run_command(f"cd {case_dir} && mkdir {stl_files_container_location}")
        of.copy_file_to_container(stl_files_source + "AMI.stl", stl_files_container_location, DOCKER_CONTAINER_NAME)
        of.copy_file_to_container(stl_files_source + "desk.stl", stl_files_container_location, DOCKER_CONTAINER_NAME)
        of.copy_file_to_container(stl_files_source + "door.stl", stl_files_container_location, DOCKER_CONTAINER_NAME)
        of.copy_file_to_container(stl_files_source + "fan.stl", stl_files_container_location, DOCKER_CONTAINER_NAME)
        of.copy_file_to_container(stl_files_source + "outlet.stl", stl_files_container_location, DOCKER_CONTAINER_NAME)
        of.copy_file_to_container(stl_files_source + "room.stl", stl_files_container_location, DOCKER_CONTAINER_NAME)


        # Setup the OpenFOAM case
        of.create_openfoam_case(case_dir, number_of_subdomains=num_processors, docker_container_name=DOCKER_CONTAINER_NAME)

    if build_mesh:
        # set up the openfoam simualtion
        of.run_command(f"cd {case_dir} && touch open.foam", DOCKER_CONTAINER_NAME)
        of.run_command(f"cd {case_dir} && surfaceFeatureExtract", DOCKER_CONTAINER_NAME)
        of.run_command(f"cd {case_dir} && blockMesh", DOCKER_CONTAINER_NAME)
    
        if mesh_par: 
            of.run_command(f"cd {case_dir} && decomposePar -force", DOCKER_CONTAINER_NAME) # decompose mesh
            of.run_command(f'cd {case_dir} && mpirun -np {num_processors} snappyHexMesh -parallel -overwrite', DOCKER_CONTAINER_NAME)
            of.run_command(f'cd {case_dir} && reconstructParMesh -constant', DOCKER_CONTAINER_NAME)
        else:
            of.run_command(f"cd {case_dir} && snappyHexMesh -overwrite", DOCKER_CONTAINER_NAME)
    
    
        of.run_command(f"cd {case_dir} && rm -rf 0", DOCKER_CONTAINER_NAME)
        of.run_command(f"cd {case_dir} && renumberMesh -overwrite", DOCKER_CONTAINER_NAME)
        of.run_command(f"cd {case_dir} && createPatch -overwrite", DOCKER_CONTAINER_NAME)

    if write_files:
        of.create_openfoam_initial_conditions(case_dir, DOCKER_CONTAINER_NAME)

    # Run the simulation in parallel (note already decomposed)
    if run_sim:
        if sim_par:
            of.run_command(f"cd {case_dir} && decomposePar -force", DOCKER_CONTAINER_NAME) # decompose mesh
            of.run_command(f'cd {case_dir} && mpirun -np {num_processors} pimpleFoam -parallel > log.pimpleFoam', DOCKER_CONTAINER_NAME)
            of.run_command(f'cd {case_dir} && reconstructPar', DOCKER_CONTAINER_NAME)
        else:
            of.run_command(f'cd {case_dir} && pimpleFoam > log.pimpleFoam', DOCKER_CONTAINER_NAME)
        
        # generate VTK files and post process 
        of.run_command(f'cd {case_dir} && foamToVTK', DOCKER_CONTAINER_NAME)
    
    # Extract forces data
    forces_data = of.extract_forces_data(forces_file)
    print(forces_data.head())

if __name__ == "__main__":
    main()
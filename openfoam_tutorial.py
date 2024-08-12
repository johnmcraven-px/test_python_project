import os
import subprocess
import shutil

# Docker container name
DOCKER_CONTAINER_NAME = "openfoam_container_new2"

def run_command(command, check_output=True):
    """Run a shell command and log its output."""
    source_openfoam = "source /opt/openfoam10/etc/bashrc"
    docker_command = f"docker exec -it {DOCKER_CONTAINER_NAME} bash -c \"{source_openfoam} && {command}\""
    result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
    print(f"Command: {command}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    if check_output:
        result.check_returncode()
    return result

def copy_file_to_container(local_path, container_path):
    """Copy a file from the host to the Docker container."""
    docker_copy_command = f"docker cp '{local_path}' '{DOCKER_CONTAINER_NAME}:{container_path}'"
    result = subprocess.run(docker_copy_command, shell=True, capture_output=True, text=True)
    print(f"Copy Command: {docker_copy_command}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    result.check_returncode()

def copy_files(src, dst):
    """Copy files from src to dst on the local machine."""
    if os.path.exists(dst):
        shutil.rmtree(dst)  # Remove destination folder if it already exists
    shutil.copytree(src, dst)
    print(f"Copied files from {src} to {dst}")

def check_and_fix_dynamic_mesh_dict_path(file_path):
    """Check and fix the path to 'dynamicMeshDict' in the specified file inside the container."""
    dynamic_mesh_dict_path = "/home/openfoam/case/constant/dynamicMeshDict"
    command = f"docker exec {DOCKER_CONTAINER_NAME} [ -f {dynamic_mesh_dict_path} ]"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {dynamic_mesh_dict_path} does not exist.")
        return

    command = f"sed -i 's#<constant>#constant#g' {file_path}"
    run_command(command)
    print(f"Checked and fixed path to 'dynamicMeshDict' in {file_path} inside the Docker container.")

def replace_sinclude_with_include_in_container(file_path):
    """Replace 'sinclude' with 'include' in the specified file inside the Docker container."""
    command = f"sed -i 's/sinclude/include/g' {file_path}"
    run_command(command)
    print(f"Replaced 'sinclude' with 'include' in {file_path} inside the Docker container.")

def main():
    # Step 1: Define the repository and paths
    repo_url = "https://develop.openfoam.com/Development/openfoam.git"
    case_path = "tutorials/incompressible/pimpleFoam/RAS/rotatingFanInRoom"
    geometry_path = "tutorials/resources/geometry/rotatingFanInRoom"
    local_case_directory = "./openfoam_tutorial_case"
    container_case_directory = "/home/openfoam/case"

    # Step 2: Clone the repository
    if not os.path.exists("OpenFOAM_repo"):
        print(f"Cloning repository from {repo_url}...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, "OpenFOAM_repo"], check=True)
        print("Repository cloned.")

    # Step 3: Copy the necessary case and geometry files to the local destination directory
    case_directory = os.path.join("OpenFOAM_repo", case_path)
    geometry_directory = os.path.join("OpenFOAM_repo", geometry_path)
    
    # Ensure the 'case' directory is created within 'openfoam_tutorial_case'
    os.makedirs(local_case_directory, exist_ok=True)
    
    # Copy the case files and geometry files into the correct directories on the local machine
    copy_files(case_directory, local_case_directory)
    copy_files(geometry_directory, os.path.join(local_case_directory, "geometry"))

    # Step 4: Copy the case files into the Docker container
    copy_file_to_container(case_directory, os.path.join(container_case_directory, ''))
    print(os.path.join(container_case_directory, 'case'))

    # Step 5: Ensure the files in the container are writable
    run_command(f"chmod -R 777 {container_case_directory}/system")

    # Step 6: Replace 'sinclude' with 'include' and fix the path to 'dynamicMeshDict' in the 'relVelocity' file
    rel_velocity_file_path = f"{container_case_directory}/system/relVelocity"
    replace_sinclude_with_include_in_container(rel_velocity_file_path)
    check_and_fix_dynamic_mesh_dict_path(rel_velocity_file_path)

    # Step 7: Run the OpenFOAM meshing and simulation commands inside the Docker container
    print("Running blockMesh...")
    run_command(f"cd {container_case_directory} && blockMesh")

    print("Running surfaceFeatures...")
    run_command(f"cd {container_case_directory} && surfaceFeatures")

    print("Running snappyHexMesh...")
    run_command(f"cd {container_case_directory} && snappyHexMesh -overwrite")

    # Step 8: Set up and run the simulation
    print("Running potentialFoam...")
    run_command(f"cd {container_case_directory} && potentialFoam -init -writephi")

    print("Running the simulation with pimpleDyMFoam...")
    run_command(f"cd {container_case_directory} && pimpleDyMFoam")

    # Step 9: Post-process the results
    print("Running post-processing...")
    run_command(f"cd {container_case_directory} && foamToVTK")

    # Print completion message
    print("Simulation setup and run completed successfully.")

if __name__ == "__main__":
    main()

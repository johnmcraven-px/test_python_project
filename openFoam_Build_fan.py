import subprocess
import os
import pandas as pd
import openfoam_functions as of
import traceback

def main():
    # Set the number processors 
    num_processors = 4
    
    write_files = True
    
    build_mesh = True
    mesh_par = True
    
    sim_par = True
    run_sim = True


    # Set the case directory
    base_dir = "/home/openfoam/"
    case_dir = base_dir + "case/"
    forces_file = 'case/postProcessing/forces/0/force.dat'

    if write_files:
        # clean up files 
        # of.run_command(f"cd {case_dir} && rm -R ./*")

        # create directory structure
        of.create_directory_structure(case_dir)

        # move the stl files to the right location
        stl_files_source = os.path.expanduser("./output/geometry_new/")  # STL file on the host
        stl_files_container_location = os.path.join(case_dir, "constant/triSurface/")

    
        # run_command(f"cd {case_dir} && mkdir {stl_files_container_location}")
        of.copy_file(stl_files_source + "AMI.stl", stl_files_container_location)
        of.copy_file(stl_files_source + "desk.stl", stl_files_container_location)
        of.copy_file(stl_files_source + "door.stl", stl_files_container_location)
        of.copy_file(stl_files_source + "fan.stl", stl_files_container_location)
        of.copy_file(stl_files_source + "outlet.stl", stl_files_container_location)
        of.copy_file(stl_files_source + "room.stl", stl_files_container_location)


        # Setup the OpenFOAM case
        sim_end_time = 1 # time in seconds
        fine_mesh_level = 3
        course_mesh_level = 1
        rotation_speed = 10 # radians per second
        time_step = 0.0002 # recommended setting is 0.0002
        write_interval = 0.02 # recommended setting is 0.02
        center_of_rotation = "(-3 2 2.6)"
        of.create_openfoam_case(case_dir, number_of_subdomains=num_processors, 
                                sim_end_time=sim_end_time, fine_mesh_level=fine_mesh_level, course_mesh_level=course_mesh_level, 
                                rotation_speed= rotation_speed, time_step=time_step, write_interval=write_interval, 
                                center_of_rotation=center_of_rotation)

    if build_mesh:
        # set up the openfoam simualtion
        of.run_command(f"cd {case_dir} && touch open.foam")
        of.run_command(f"cd {case_dir} && surfaceFeatureExtract")
        of.run_command(f"cd {case_dir} && blockMesh")
    
        if mesh_par: 
            of.run_command(f"cd {case_dir} && decomposePar -force") # decompose mesh
            of.run_command(f'cd {case_dir} && mpirun -np {num_processors} snappyHexMesh -parallel -overwrite')
            of.run_command(f'cd {case_dir} && reconstructParMesh -constant')
        else:
            of.run_command(f"cd {case_dir} && snappyHexMesh -overwrite")
    
    
        of.run_command(f"cd {case_dir} && rm -rf 0")
        of.run_command(f"cd {case_dir} && renumberMesh -overwrite")
        of.run_command(f"cd {case_dir} && createPatch -overwrite")

    if write_files:
        of.create_openfoam_initial_conditions(case_dir)

    # Run the simulation in parallel (note already decomposed)
    if run_sim:
        if sim_par:
            of.run_command(f"cd {case_dir} && decomposePar -force") # decompose mesh
            of.run_command(f'cd {case_dir} && mpirun -np {num_processors} pimpleFoam -parallel > log.pimpleFoam', run_as_root = False)
            of.run_command(f'cd {case_dir} && reconstructPar')
        else:
            of.run_command(f'cd {case_dir} && pimpleFoam > log.pimpleFoam', run_as_root=False)
        
        # generate VTK files and post process 
        of.run_command(f'cd {case_dir} && foamToVTK')
    
    # Extract forces data
    forces_data = of.extract_forces_data(forces_file)
    print(forces_data.head())


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        error_message = traceback.format_exc()
        print(f"An error occurred1:\n{error_message}")
    except OSError as e:
        error_message = traceback.format_exc()
        print(f"An error occurred2:\n{error_message}")
    except BaseException as e:
        error_message = traceback.format_exc()
        print(f"An error occurred3:\n{error_message}")
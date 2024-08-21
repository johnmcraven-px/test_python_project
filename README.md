# demo

This is a demo

## Installation



## Usage
to run the blender file use: 
''' bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python blender_build_fan.py
''' 

/Applications/Blender.app/Contents/MacOS/Blender --background --python blender_export_properties.py -- ./openfoam_tutorial_case/geometry/fan.blend ./openfoam_tutorial_case/geometry/output.txt


docker run -it --name openfoam_container_new --cpus=4 -v $(pwd):/home/openfoam/case my_openfoam_image

note - this has to match with the parallel compute setting; it is multithreaded so 8 cores with 4 CPUs

## Contributing

xxx

## License


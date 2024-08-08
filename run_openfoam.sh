# rm -rf case
# mkdir case
rm -rf output
cp -r ../data/output output
# docker build -t my_openfoam_image .
# apt-get update && apt-get install -y tmux && apt-get install -y docker.io
# docker rm -f openfoam_container_new
# cd case
# tmux new-session -d -s container_session "bash -c 'docker run -it --name openfoam_container_new -v $(pwd):/home/openfoam/case my_openfoam_image'"
# cd ..

pip install pandas
python openfoam_test.py "$@"
rm -rf ../data/case
mkdir ../data/case
cp -r /Volumes/git/test_root/test_python_project/case/* ../data/case/
python convert_vtk.py
# docker rm -f openfoam_container_new

# rm -rf case
# mkdir case
rm -rf output
cp -r ../data/output output
# docker build -t my_openfoam_image .
# apt-get update && apt-get install -y tmux && apt-get install -y docker.io
# docker rm -f openfoam_container_new
# cd case
# tmux new-session -d -s container_session "bash -c 'docker run -it --name openfoam_container_new -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):/home/openfoam/case my_openfoam_image'"
# cd ..

# pip install pandas
python openfoam_test.py
# docker rm -f openfoam_container_new

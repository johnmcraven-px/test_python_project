cp -r ../data/output output
apt-get update && apt-get install -y python3-pip
pip install pandas
su - openfoam
cd /git
echo "source /opt/openfoam10/etc/bashrc" >> ~/.bashrc
mkdir case
mkdir ../data/case

python openfoam_test.py "$@"
mv case/* ../data/case/

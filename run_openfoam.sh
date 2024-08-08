apt-get update && apt-get install -y python3-pip
su - openfoam <<EOF
cp -r ../data/output output
whoami
pip install pandas
cd /git
echo "source /opt/openfoam10/etc/bashrc" >> ~/.bashrc
mkdir case
mkdir ../data/case

python3 openfoam_test.py "$@"
mv case/* ../data/case/
EOF
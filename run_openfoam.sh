apt-get update && apt-get install -y python3-pip
chown -R openfoam /data/
chown -R openfoam /git/
su - openfoam <<EOF
cd /git
cp -r ../data/output output
whoami
pip install pandas
echo "source /opt/openfoam10/etc/bashrc" >> ~/.bashrc
mkdir case
mkdir ../data/case

echo "TEST0"
python3 openfoam_test.py "$@";
EOF

su - openfoam <<EOF
cd /git
echo "TEST1"
ls case
mv case/* ../data/case/
echo "TEST2"
ls ../data/case
EOF
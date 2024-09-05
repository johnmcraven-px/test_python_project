# Switch to root user
su - <<EOF
chown -R openfoam:openfoam /data/
chown -R openfoam:openfoam /git/

apt-get update && apt-get install -y python3-pip
EOF

# Switch to a non-root user if necessary
su - openfoam <<EOF
# Set the working directory
cd /home/openfoam
mkdir case

cp -r /git/* .
mv /data/output output
mkdir /data/case

pip install pandas

echo "TEST0"
python3 openFoam_Build_fan.py "$@";

mv case/* /data/case/
echo "Contents of /data/case:"
ls /data/case
EOF
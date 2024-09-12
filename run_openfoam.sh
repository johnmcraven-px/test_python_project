# Switch to root user
su - <<EOF
# chown -R openfoam:openfoam /data/
# chown -R openfoam:openfoam /git/
# EOF

# Switch to a non-root user if necessary
# Set the working directory
cd /home/openfoam
rm -R -f case/
mkdir -m 766 case

cp -r /git/* .
mv /data/output output
mkdir /data/case

pip install pandas

echo "TEST0"
pwd
ls -l

echo "TEST1"
ls -l case

echo "TEST2"
whoami

su - openfoam <<EOF
python3 openFoam_Build_fan.py "$@" || true;

echo "TEST3"
ls
echo "TEST3A"
ls case
echo "TEST3B"
ls case/dynamicCode
echo "TEST3C"
ls case/dynamicCode/platforms
echo "TEST3D"

# mv case/* /data/case/
# echo "Contents of /data/case:"
# ls /data/case
EOF
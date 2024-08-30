# Switch to root user
sudo su -

# Add a non-root user called openfoam
useradd -ms /bin/bash openfoam

# Install necessary dependencies
apt-get update && apt-get install -y \
    gcc g++ make cmake wget ca-certificates \
    openmpi-bin libopenmpi-dev flex bison zlib1g-dev \
    && apt-get clean

# Create necessary directories and set ownership to openfoam user
mkdir -p /opt/OpenFOAM && chown -R openfoam:openfoam /opt/OpenFOAM

# Install necessary dependencies and extract OpenFOAM
apt-get update && apt-get install -y wget ca-certificates && apt-get clean
wget -O /tmp/OpenFOAM-v2406.tgz https://dl.openfoam.com/source/v2406/OpenFOAM-v2406.tgz
tar -xzf /tmp/OpenFOAM-v2406.tgz -C /opt/OpenFOAM
rm /tmp/OpenFOAM-v2406.tgz

apt-get update && apt-get install -y python3-pip

# Set environment variables for OpenFOAM
echo "source /opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc" >> ~/.bashrc

# Compile OpenFOAM with detailed output
source /opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc
cd /opt/OpenFOAM/OpenFOAM-v2406
./Allwmake -j $(nproc) 2>&1 | tee /opt/OpenFOAM/build.log

# Verify the installation by listing the binaries, if they exist
if [ -d /opt/OpenFOAM/OpenFOAM-v2406/platforms/linuxARM64GccDPInt32Opt/bin ]; then
    ls /opt/OpenFOAM/OpenFOAM-v2406/platforms/linuxARM64GccDPInt32Opt/bin
else
    echo 'Build failed, see /opt/OpenFOAM/build.log for details'
fi

chown -R openfoam /data/
chown -R openfoam /git/

# Switch to a non-root user if necessary
su - openfoam

# Set the working directory
cd /home/openfoam

cd /git
cp -r . output /home/openfoam/case
# whoami
pip install pandas
mkdir /data/case

echo "TEST0"
python3 openfoam_test.py "$@";

mv case/* ../data/case/
echo "Contents of /data/case:"
ls /data/case
#!/bin/bash

# Create a virtual environment to store and isolate the dependencies to the system
virtualenv .venv/ 

# Install all the dependencies
. .venv/bin/activate && pip install -r requirements.txt

# Set up YOLOR
# ----------------------------------------------

# Incorporate YOLOR dependency project as submodule
git submodule update --init

# ./yolor/models/models.py
sed -i "1s/from *utils./from yolor.utils./1" "./yolor/models/models.py"
echo "1s/from *utils./from yolor.utils./1 > ./yolor/models/models.py"
sed -i "2s/from *utils./from yolor.utils./1" "./yolor/models/models.py"
echo "2s/from *utils./from yolor.utils./1 > ./yolor/models/models.py"
sed -i "3s/from *utils./from yolor.utils./1" "./yolor/models/models.py"
echo "3s/from *utils./from yolor.utils./1 > ./yolor/models/models.py"
sed -i "4s/from *utils/from yolor.utils/1" "./yolor/models/models.py"
echo "4s/from *utils/from yolor.utils/1 > ./yolor/models/models.py"

# ./yolor/utils/datasets.py
sed -i "26s/from *utils./from yolor.utils./1" "./yolor/utils/datasets.py"
echo "26s/from *utils./from yolor.utils./1 > ./yolor/utils/datasets.py"
sed -i "27s/from *utils./from yolor.utils./1" "./yolor/utils/datasets.py"
echo "27s/from *utils./from yolor.utils./1 > ./yolor/utils/datasets.py"

# ./yolor/utils/general.py
sed -i "20s/from *utils./from yolor.utils./1" "./yolor/utils/general.py"
echo "20s/from *utils./from yolor.utils./1 > ./yolor/utils/general.py"
sed -i "21s/from *utils./from yolor.utils./1" "./yolor/utils/general.py"
echo "21s/from *utils./from yolor.utils./1 > ./yolor/utils/general.py"
sed -i "22s/from *utils./from yolor.utils./1" "./yolor/utils/general.py"
echo "22s/from *utils./from yolor.utils./1 > ./yolor/utils/general.py"

# ./yolor/utils/layers.py
sed -i "3s/from *utils./from yolor.utils./1" "./yolor/utils/layers.py"
echo "3s/from *utils./from yolor.utils./1 > ./yolor/utils/layers.py"

# ./yolor/utils/loss.py
sed -i "6s/from *utils./from yolor.utils./1" "./yolor/utils/loss.py"
echo "6s/from *utils./from yolor.utils./1 > ./yolor/utils/loss.py"
sed -i "7s/from *utils./from yolor.utils./1" "./yolor/utils/loss.py"
echo "7s/from *utils./from yolor.utils./1 > ./yolor/utils/loss.py"

# ./yolor/utils/plots.py
sed -i "19s/from *utils./from yolor.utils./1" "./yolor/utils/plots.py"
echo "19s/from *utils./from yolor.utils./1 > ./yolor/utils/plots.py"
sed -i "20s/from *utils./from yolor.utils./1" "./yolor/utils/plots.py"
echo "20s/from *utils./from yolor.utils./1 > ./yolor/utils/plots.py"

# ----------------------------------------------

# Create a copy of sample configuration files for MQTT clients
cp "cfg/client/mqtt/sample.cfg" "cfg/client/mqtt/notif.cfg"
cp "cfg/client/mqtt/sample.cfg" "cfg/client/mqtt/set.cfg"
cp "cfg/client/sftp/sample.cfg" "cfg/client/sftp/data.cfg"

# Create ssh keys for SFTP
ssh-keygen -f "data/ssh_keys/rpi-camera" -t rsa -N "" -b 4096

# Generate documentation of the source file of this project
# If you don't want it to be included, you can comment it out
pdoc --html --force src

read -p "Press enter to exit..."

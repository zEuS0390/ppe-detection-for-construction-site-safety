#!/bin/bash

python -m venv .venv/ 

. .venv/bin/activate && pip install -r requirements.txt

# Clone YOLOR repository
git clone "https://github.com/WongKinYiu/yolor.git"
rm -rf "./yolor/.git"

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

# read -p "Press enter to exit..."

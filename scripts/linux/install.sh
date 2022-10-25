# Clone YOLOR repository
git clone "https://github.com/WongKinYiu/yolor.git"
rm -rf "./yolor/.git"

# Install project dependencies
pipenv install

# Install YOLOR dependencies
pipenv run pip install Cython
pipenv run pip install matplotlib
pipenv run pip install numpy
pipenv run pip install opencv-python
pipenv run pip install Pillow
pipenv run pip install PyYAML
pipenv run pip install scipy
pipenv run pip install tensorboard
pipenv run pip install torch
pipenv run pip install torchvision
pipenv run pip install tqdm
pipenv run pip install seaborn
pipenv run pip install pandas
pipenv run pip install thop
pipenv run pip install pycocotools

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

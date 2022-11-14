mkdir -p './data/sample'
mkdir -p './data/sample/images'
mkdir -p './data/sample/output'
python ./yolor/detect.py --source './data/sample/images' --output './data/sample/output' --names './cfg/detection/data_custom.names' --cfg './cfg/detection/yolor_csp_custom.cfg' --weights './data/weights/version_4.3.pt' --img-size 640 --device 0
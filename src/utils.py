import cv2, base64, os, gdown, glob, time, subprocess
from csv import DictReader

def imageToBinary(image):
    """
    Convert a numpy array image to binary data.

    Arg:
        image: numpy.ndarray

    Returns the encoded bytes in string
    """
    _, buffer = cv2.imencode(".jpg", image)
    binary_string = base64.b64encode(buffer)
    return binary_string.decode()

def getElapsedTime(func, *args, **kwargs):
    """
    Get the elapsed time of a given function.

    Args:
        func: A function that will be measured in time
        *args: Required arguments in the func parameter
        *kwargs: Key-worded arguments in the func parameter

    Returns the encapsulated tuple of the function result and the elapsed time
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return (result, elapsed_time)

def checkLatestWeights():
    """
    Checks the latest weights file
    """
    current_version_file = "data/weights/current_version.txt"
    if not os.path.exists(current_version_file):
        current_id = 0
        with open(current_version_file, "w") as data:
            data.write(str(current_id))
    else:
        with open(current_version_file, "r") as data:
            current_id = int(data.readline())
    with open("data/weights/versions.csv", newline="") as csvfile:
        reader = DictReader(csvfile)
        max = {}
        for row in reader:
            id = int(row["id"])
            if id > 0:
                max = row
        try:
            id = max["id"]
            if int(id) != current_id:
                weights_files = glob.glob("data/weights/*.pt")
                for weights_file in weights_files:
                    os.remove(weights_file)
                gdown.download(id=max["gdrive_id"], output=os.path.join("data/weights/", ".".join([max["name"], "pt"])))
                with open(current_version_file, "w") as data:
                    data.write(str(id))
        except Exception as e:
            print(e)

def getIPAddress():
    ip_addr = subprocess.check_output(['hostname', '-I']).split()[0].decode()
    return ip_addr

def parsePlainConfig(filepath: str):
    if not os.path.exists(filepath):
        raise Exception(f"'{filepath}' does not exist.")
    try:
        with open(filepath, "r") as file:
            cfg = dict([line.strip().replace(" ", "").split(":") for line in file.readlines()])
            return cfg
    except Exception as e:
        raise e
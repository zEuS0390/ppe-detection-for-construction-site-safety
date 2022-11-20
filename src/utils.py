import cv2, base64, os, gdown, glob, time, subprocess
from csv import DictReader
import paramiko

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
    # Checks the latest weights file
    current_version_file = "data/detection/current_version.txt"
    if not os.path.exists(current_version_file):
        current_id = 0
        with open(current_version_file, "w") as data:
            data.write(str(current_id))
    else:
        with open(current_version_file, "r") as data:
            current_id = int(data.readline())
    with open("data/detection/versions.csv", newline="") as csvfile:
        reader = DictReader(csvfile)
        max = {}
        for row in reader:
            id = int(row["id"])
            if id > 0:
                max = row
        try:
            id = max["id"]
            if int(id) != current_id:
                weights_files = glob.glob("data/detection/*.pt")
                for weights_file in weights_files:
                    os.remove(weights_file)
                gdown.download(id=max["gdrive_id"], output=os.path.join("data/detection/", ".".join([max["name"], "pt"])))
                with open(current_version_file, "w") as data:
                    data.write(str(id))
        except Exception as e:
            print(e)

def getDetectionModel(cfg):
    weights_dir = cfg.get("yolor", "weights")
    versions = sorted(os.listdir(weights_dir))
    if len(versions) > 0:
        latest_name = versions.pop()
        latest_dir = os.path.join(weights_dir, latest_name)
        files = os.listdir(latest_dir)
        for file in files:
            if file.endswith(".pt"):
                return os.path.join(latest_dir, file)

def getRecognitionData(cfg):
    recognition_model_dir = cfg.get("face_recognition", "model")
    versions = sorted(os.listdir(recognition_model_dir))
    if len(versions) > 0:
        latest_name = versions.pop()
        latest_dir = os.path.join(recognition_model_dir, latest_name)
        files = os.listdir(latest_dir)
        result = {}
        for file in files:
            if file.endswith(".clf"):
                result["model"] = os.path.join(latest_dir, file)
            if file.endswith(".csv"):
                result["info"] = os.path.join(latest_dir, file)
        return result

def getIPAddress():
    ip_addr = subprocess.check_output(['hostname', '-I']).split()[0].decode()
    return ip_addr

def parsePlainConfig(filepath: str):
    if not os.path.exists(filepath):
        raise Exception(f"'{filepath}' does not exist.")
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
            cfg = {}
            for line in lines:
                separator_index = line.find(":")
                key = line[:separator_index]
                value = line[separator_index+1:].strip()
                cfg[key] = value
            return cfg
    except Exception as e:
        raise e

def getLatestFiles(cfg_name, target_names: list):
    print("Getting the latest data files of {0}".format(cfg_name))
    cfg_file = f"cfg/client/sftp/{cfg_name}.cfg"
    cfg = parsePlainConfig(cfg_file)
    hostname = cfg["hostname"]
    port = int(cfg["port"])
    source_dir = cfg["source_dir"]
    destination_dir = cfg["destination_dir"]
    username = cfg["username"]
    private_key_file = cfg["private_key_file"]

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    RSAPKey = paramiko.RSAKey.from_private_key_file(private_key_file)
    
    try:
        ssh_client.connect(
            hostname=hostname,
            username=username,
            pkey=RSAPKey,
            allow_agent=False,
            look_for_keys=False
        )
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(f"{e}\nCheck if SSH server is online.")
        return
    except paramiko.ssh_exception.AuthenticationException as e:
        print(f"{e}\nCheck if SSH server creredentials are correct.")
        return

    sftp_client = ssh_client.open_sftp()
    files = []
    try:
        files = sftp_client.listdir(source_dir)
    except FileNotFoundError as e:
        print(f"{e}\nCheck if the source directory exists.")
        return
            
    if len(files) > 0:
        for target_name in target_names:
            try:
                index = files.index(target_name)
            except ValueError as e:
                print(f"{e}")
                continue
            try:
                target_dir = sftp_client.listdir(os.path.join(source_dir, target_name))
            except FileNotFoundError as e:
                print(f"{e}")
                continue
            if len(target_dir) > 0:
                latest = target_dir.pop()
                if latest in os.listdir(os.path.join(destination_dir, target_name)):
                    print(f"Download '{latest}' [ALREADY EXIST]")
                    continue
                print(f"Download '{latest}'")
                latest_files = sftp_client.listdir(os.path.join(source_dir, target_name, latest))
                for file in latest_files:
                    source_latest_dir = os.path.join(source_dir, target_name, latest)
                    destination_latest_dir = os.path.join(destination_dir, target_name, latest) 
                    source_file = os.path.normpath(os.path.join(source_latest_dir, file))
                    destination_file = os.path.join(destination_latest_dir, file)
                    if not os.path.exists(destination_latest_dir):
                        os.mkdir(destination_latest_dir)
                    sftp_client.get(source_file, destination_file)
                    print(f"\t* [DOWNLOADED] {file}")
        sftp_client.close()
        ssh_client.close()
    else:
        sftp_client.close()
        ssh_client.close()
        print("Files not found.")

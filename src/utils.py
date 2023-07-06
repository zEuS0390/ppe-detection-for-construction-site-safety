import cv2, base64, os, time, subprocess, paramiko, socket, logging
import numpy as np

"""
    Functions:
        - imageToBinary         (image)
        - getElapsedTime        (func, *args, **kwargs)
        - getDetectionModel     (cfg)
        - getRecognitionData    (cfg)
        - getIPAddress          ()
        - parsePlainConfig      (filepath)
        - getLatestFiles        (cfg_name, target_names)
"""

def binaryToImage(binary):
    buffer = base64.b64decode(binary)
    npimg = np.frombuffer(buffer, dtype=np.uint8)
    img = cv2.imdecode(npimg, 1)
    frame = cv2.resize(img, (640, 640), interpolation=cv2.INTER_AREA)
    return frame
    
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

def getDetectionModel(cfg):
    """
    Gets the latest detection model file
    """
    weights_dir = cfg.get("yolor", "weights_dir")
    versions = sorted(os.listdir(weights_dir))
    if len(versions) > 0:
        latest_name = versions.pop()
        latest_dir = os.path.join(weights_dir, latest_name)
        files = os.listdir(latest_dir)
        for file in files:
            if file.endswith(".pt"):
                return os.path.join(latest_dir, file)

def getRecognitionData(cfg):
    """
    Gets the latest recognition model file
    """
    recognition_model_dir = cfg.get("face_recognition", "models_dir")
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
    """
    Gets the current IP address of the machine.
    
    Returns a string of IP address
    """
    ip_addr = subprocess.check_output(['hostname', '-I']).split()[0].decode()
    return ip_addr

def parsePlainConfig(filepath: str):
    """
    Parse the custom configuration file
    """
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
    logger = logging.getLogger()
    logger.info("Getting the latest data files of {0}".format(cfg_name))
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
            look_for_keys=False,
            timeout=10
        )
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        logger.error(f"{e}. Check if SSH server is online.")
        return
    except paramiko.ssh_exception.AuthenticationException as e:
        logger.error(f"{e}. Check if SSH server creredentials are correct.")
        return
    except socket.timeout as e:
        logger.error(f"{e}. Check if SSH server is online.")
        return
    except OSError as e:
        logger.error(f"{e}")
        return

    sftp_client = ssh_client.open_sftp()
    files = []
    try:
        files = sftp_client.listdir(source_dir)
    except FileNotFoundError as e:
        logger.error(f"{e}. Check if the source directory exists.")
        return
            
    if len(files) > 0:
        for target_name in target_names:
            if not os.path.exists(os.path.join(destination_dir, target_name)):
                os.mkdir(os.path.join(destination_dir, target_name))
            try:
                index = files.index(target_name)
            except ValueError as e:
                logger.error(f"{e}")
                continue
            try:
                target_dir = sftp_client.listdir(os.path.join(source_dir, target_name))
            except FileNotFoundError as e:
                logger.error(f"{e}")
                continue
            if len(target_dir) > 0:
                latest = target_dir.pop()
                destination_versions = os.listdir(os.path.join(destination_dir, target_name))
                if latest in destination_versions:
                    logger.error(f"Download '{latest}' [ALREADY EXIST]")
                    continue
                logger.error(f"Download '{latest}'")
                latest_files = sftp_client.listdir(os.path.join(source_dir, target_name, latest))
                for file in latest_files:
                    source_latest_dir = os.path.join(source_dir, target_name, latest)
                    destination_latest_dir = os.path.join(destination_dir, target_name, latest) 
                    source_file = os.path.normpath(os.path.join(source_latest_dir, file))
                    destination_file = os.path.join(destination_latest_dir, file)
                    if not os.path.exists(destination_latest_dir):
                        os.mkdir(destination_latest_dir)
                    sftp_client.get(source_file, destination_file)
                    logger.error(f"\t* [DOWNLOADED] {file}")
                for version in destination_versions:
                    os.rmdir(version)
        sftp_client.close()
        ssh_client.close()
    else:
        sftp_client.close()
        ssh_client.close()
        logger.error("Files not found.")

from csv import DictReader
import cv2, base64, os, gdown, glob

# Convert an image to binary data
def imageToBinary(image):
    _, buffer = cv2.imencode(".jpg", image)
    binary_string = base64.b64encode(buffer)
    return binary_string.decode()

def checkLatestWeights():
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
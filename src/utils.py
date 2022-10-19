import cv2, base64

# Convert an image to binary data
def imageToBinary(image):
    _, buffer = cv2.imencode(".jpg", image)
    binary_string = base64.b64encode(buffer)
    return binary_string.decode()
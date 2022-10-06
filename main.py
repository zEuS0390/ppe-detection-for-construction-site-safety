import cv2

cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
out = cv2.VideoWriter('sample.mp4', fourcc, 20.0, (640, 480))

while True:
	_, frame = cap.read()
	cv2.imshow("frame", frame)
	out.write(frame)
	if cv2.waitKey(30) == 27:
		break

cap.release()
cv2.destroyAllWindows()

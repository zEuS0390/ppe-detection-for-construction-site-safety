import pickle, face_recognition
from configparser import ConfigParser
import time

class Recognition:

    isRunning = True

    def __init__(self, cfg: ConfigParser):
        self.cfg = cfg
        self.load_model()

    def load_model(self):
        with open(self.cfg.get("face_recognition", "model"), "rb") as file:
            self.knn_clf = pickle.load(file)

    def predict(self, frame, distance_threshold=0.6):
        start_time = time.time()
        # Load image file and find face locations
        X_img = frame
        X_face_locations = face_recognition.face_locations(X_img)
        # If no faces are found in the image, return an empty result.
        if len(X_face_locations) == 0:
            return []
        # Find encodings for faces in the test iamge
        faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)
        # Use the KNN model to find the best matches for the test face
        closest_distances = self.knn_clf.kneighbors(faces_encodings, n_neighbors=1)
        are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]
        predictions = self.knn_clf.predict(faces_encodings)
        elapsed_time = time.time() - start_time
        print(f"Face recognition time: {elapsed_time:.2f}s")
        # Predict classes and remove classifications that aren't within the threshold
        return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(predictions, X_face_locations, are_matches)]
    

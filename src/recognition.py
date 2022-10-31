import pickle, face_recognition, cv2
from src.camera import Camera

class Recognition:

    isRunning = True

    @staticmethod
    def predict(frame, knn_clf=None, model_path=None, distance_threshold=0.6):
        if knn_clf is None and model_path is None:
            raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")
        # Load a trained KNN model (if one was passed in)
        if knn_clf is None:
            with open(model_path, 'rb') as f:
                knn_clf = pickle.load(f)
        # Load image file and find face locations
        X_img = frame
        X_face_locations = face_recognition.face_locations(X_img)
        # If no faces are found in the image, return an empty result.
        if len(X_face_locations) == 0:
            return []
        # Find encodings for faces in the test iamge
        faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)
        # Use the KNN model to find the best matches for the test face
        closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
        are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]
        # Predict classes and remove classifications that aren't within the threshold
        return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

    @staticmethod
    def start(cam: Camera):
        while Recognition.isRunning == True:
            try:
                if cam.frame is not None:
                    rgb_frame = cam.frame.copy()
                    rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2RGB)
                    predictions = Recognition.predict(
                        rgb_frame, 
                        model_path="trained_knn_model.clf", 
                        distance_threshold=0.60
                    )
                    print(predictions)
            except Exception as e:
                print(e)
                break

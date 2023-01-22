from face_recognition.face_recognition_cli import image_files_in_folder
import os, math, pickle, face_recognition, logging
from configparser import ConfigParser
from src.utils import getRecognitionData
from src.singleton import Singleton
from sklearn import neighbors

class Recognition(metaclass=Singleton):

    """
    Methods:
        - load_model        ()
        - predict           (frame, 
                             distance_threshold: float = 0.4)
        - train             (train_dir: str, 
                             model_save_path: any = None,
                             knn_algo: str = 'ball tree',
                             verbose: bool = False)
    """

    def __init__(self, cfg: ConfigParser):
        self.logger = logging.getLogger()
        self.logger.info("Initializing recognition")
        self.cfg = cfg
        self.load_model()
        self.logger.info("Recognition initialized")

    def load_model(self):
        # Get the latest face recognition model
        recognition_data = getRecognitionData(self.cfg)
        if "model" in recognition_data:
            with open(recognition_data["model"], "rb") as file:
                self.knn_clf = pickle.load(file)

    def predict(self, frame, distance_threshold=0.4):
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
        # Predict classes and remove classifications that aren't within the threshold
        return [(pred, loc) if rec else (-1, loc) for pred, loc, rec in zip(predictions, X_face_locations, are_matches)]
    
    def train(train_dir, model_save_path=None, knn_algo='ball_tree', verbose=False):
        X = []
        y = []
        for class_dir in os.listdir(train_dir):
            if not os.path.isdir(os.path.join(train_dir, class_dir)):
                continue
            for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
                image = face_recognition.load_image_file(img_path)
                face_bounding_boxes = face_recognition.face_locations(image, model="cnn")
                if len(face_bounding_boxes) != 1:
                    if verbose:
                        self.logger.info("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
                else:
                    X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                    y.append(class_dir)
                    if verbose:
                      self.logger.info("Image {}: Found face".format(img_path))
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            self.logger.info("Chose n_neighbors automatically: {}".format(n_neighbors))
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit(X, y)
        # Save the trained KNN classifier
        if model_save_path is not None:
            with open(model_save_path, 'wb') as f:
                pickle.dump(knn_clf, f)
        return knn_clf

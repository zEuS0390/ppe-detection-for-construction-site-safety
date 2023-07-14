from .database import DatabaseHandler
from .tables import (
    PPEClass, 
    Violator, 
    DetectedPPEClass,
    ViolationDetails,
    DeviceDetails
)
from datetime import datetime
import csv

class DatabaseCRUD(DatabaseHandler):
    
    """
    Methods:
        - insertPPEClasses          (filepath: str)                                                             -> None
        - getPPEClasses             ()                                                                          -> dict
        - insertViolator            (violationdetails_id: int, 
                                     topleft: tuple, 
                                     bottomright: tuple, 
                                     detectedppeclasses: list, 
                                     verbose: bool = False, 
                                     commit: bool = True)                                                       -> bool
        - getAllViolationDetails    (from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"),
                                     to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59"))      -> list
    """

    def __init__(self, 
                 cfg = None, 
                 db_URL = None, 
                 echo = False):
        super(DatabaseCRUD, self).__init__(cfg, db_URL, echo)
        self.to_be_commited = []

    # Load the PPE classes that will be used for detection in PPE violations
    def insertPPEClasses(self, 
                         filepath: str) -> None:
        # Declare an empty list for names
        ppeclass_names = []
        # Read the file and add them to the list
        with open(filepath, "r") as file:
            ppeclass_names = [line.strip() for line in file.readlines()]
        # Loop and create a row for PPEClass table through each name
        for class_name in ppeclass_names:
            # Check if the current PPE class already exist in the table
            exist = self.session.query(PPEClass).filter_by(class_name=class_name).first()
            if exist is None:
                ppeclass = PPEClass(class_name=class_name)
                self.session.add(ppeclass)
            else:
                pass
                # print(f"{name} already exist!")
        self.session.commit()
        self.session.close()

    def getPPEClasses(self) -> dict:
        """
        Get all the PPE class labels defined from the database.
        """
        row = self.session.query(PPEClass).all()
        ppeclasses = {}
        for col in row:
            ppeclass = {}
            for column in col.__table__.columns:
                ppeclass[column.name] = getattr(col, column.name)
            ppeclasses[ppeclass["id"]] = ppeclass
            del ppeclass["id"]
        return ppeclasses

    def getAllDeviceDetails(self) -> list:
        return self.session.query(DeviceDetails).all()

    def insertDeviceDetails(
            self, 
            kvs_name: str,
            uuid: str, 
            password: str, 
            pub_topic: str, 
            set_topic: str, 
        ) -> int:
        devicedetails_id = -1
        devicedetails = DeviceDetails()
        devicedetails.kvs_name = kvs_name
        devicedetails.uuid = uuid
        devicedetails.password = password
        devicedetails.pub_topic = pub_topic
        devicedetails.set_topic = set_topic 
        self.session.add(devicedetails)
        self.session.flush()
        devicedetails_id = devicedetails.id
        self.session.commit() 
        self.session.close()
        return devicedetails_id

    def insertViolationDetails(
            self, 
            image=None, 
            timestamp=None
        ) -> int:
        violationdetails_id = -1
        violationdetails = ViolationDetails()
        if image is not None:
            violationdetails.image = image
        if timestamp is not None:
            violationdetails.timestamp = timestamp
        self.session.add(violationdetails)
        self.session.flush()
        violationdetails_id = violationdetails.id
        self.session.commit()
        self.session.close()
        return violationdetails_id

    def insertViolationDetailsToDeviceDetails(
            self,
            devicedetails_id: int,
            violationdetails_id: int
        ) -> bool:
        devicedetails = self.session.query(DeviceDetails).filter_by(id=devicedetails_id).scalar()
        violationdetails = self.session.query(ViolationDetails).filter_by(id=violationdetails_id).scalar()
        if devicedetails is not None and violationdetails is not None:
            devicedetails.violationdetails.append(violationdetails)
            self.session.commit()
            self.session.close()
            return True
        return False

    def insertViolator(
            self, 
            violationdetails_id: int, 
            bbox_id: int,
            topleft: tuple, 
            bottomright: tuple, 
            detectedppe: list, 
            verbose: bool = False, 
            commit: bool = True
        ) -> bool:

        violationdetails = self.session.query(ViolationDetails).filter_by(id=violationdetails_id).first()

        if violationdetails is not None:

            # A list of DetectedPPEClass items and their bbox overlaps
            to_be_added = []

            for ppeitem in detectedppe:
                ppe_bbox_id = ppeitem["bbox_id"]
                ppeclass_name = ppeitem["class_name"]
                confidence = ppeitem["confidence"]
                bbox_overlaps = ppeitem["bbox_overlaps"]
                ppeclass = self.session.query(PPEClass).filter_by(class_name=ppeclass_name).first()
                if ppeclass is not None:
                    """
                    detectedppeclass = DetectedPPEClass(
                        bbox_id=ppe_bbox_id,
                        confidence=confidence
                    )
                    detectedppeclass.ppeclasses.append(ppeclass)
                    self.session.add(detectedppeclass)
                    """
                    to_be_added.append(
                        {
                            # "detectedppeclass": detectedppeclass,
                            "ppeclass": ppeclass,
                            "confidence": confidence,
                            "bbox_id": ppe_bbox_id,
                            "bbox_overlaps": bbox_overlaps
                        } 
                    )
                else:
                    if verbose:
                        print(f"{ppeclass_name} does not exist in the db! Skipping..")
                    return False

            # Insert a violator
            violator = Violator(
                bbox_id = bbox_id,
                x1 = topleft[0],
                y1 = topleft[1],
                x2 = bottomright[0],
                y2 = bottomright[1],
                violationdetails = violationdetails,
            )

            self.session.add(violator)

            # -------------- Assign Detected PPE Classes to Violator/s --------------

            # Assign the bbox overlaps to the violators matching with their bbox ids

            for item in to_be_added:

                bbox_id = item["bbox_id"]
                ppeclass = item["ppeclass"]
                bbox_overlaps = item["bbox_overlaps"]
                confidence = item["confidence"]
                 
                detectedppeclass = DetectedPPEClass(
                    bbox_id=bbox_id,
                    confidence=confidence
                )

                ppeclass.detectedppeclasses.append(detectedppeclass)
                # detectedppeclass.ppeclasses.append(ppeclass)
                self.session.add(detectedppeclass)

                for bbox_id in bbox_overlaps:
                    
                    violators = self.session.query(Violator).filter_by(bbox_id=bbox_id).all()

                    for violator in violators:

                        # detectedppeclass.violators.append(violator)
                        violator.detectedppeclasses.append(detectedppeclass)

            if commit:
                if verbose:
                    print(f"Added {violator}")
                self.session.commit()
                self.session.close()

        return True

    def deleteViolator(self,
            violator_id: int,
            commit: bool = True) -> bool:
        violator = self.session.query(Violator).filter_by(id=violator_id).scalar()
        if violator is not None: 
            self.session.delete(violator)
            if commit:
                self.session.commit()
                self.session.close()
            return True
        return False

    def getAllViolationDetails(
            self, 
            devicedetails_uuid: str,
            from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"), 
            to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59")
        ) -> list:
        all_violation_details = self.session.query(ViolationDetails).\
            join(DeviceDetails).\
            filter(
                ViolationDetails.timestamp.between(
                    from_datetime, 
                    to_datetime)
                ).\
            filter(
                DeviceDetails.uuid==devicedetails_uuid
        ).all()
        serializable_all_violation_details = []
        for violation_details in all_violation_details:
            serializable_violation_details = {
                "uuid": devicedetails_uuid,
                "image": "",
                "total_violators": 0,
                "total_violations": 0,
                "timestamp": "11/21/22 12:19:53",
                "violators": []
            }
            for violator in violation_details.violators:
                serializable_violation_details["total_violators"] += 1
                serializable_violator = {
                    "id": 2,
                    "violations": []
                }
                for detectedppeclass in violator.detectedppeclasses:
                    serializable_violation_details["total_violations"] += 1
                    serializable_violations = {
                        "id": detectedppeclass.bbox_id,
                        "confidence": detectedppeclass.confidence,
                        "class_name": detectedppeclass.ppeclass.class_name
                    }
                    serializable_violator["violations"].append(serializable_violations)
                serializable_violation_details["violators"].append(serializable_violator)
            serializable_all_violation_details.append(serializable_violation_details)
        return serializable_all_violation_details

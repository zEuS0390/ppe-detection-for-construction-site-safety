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

    # Load the PPE classes that will be used for detection in PPE violations
    def insertPPEClasses(self, 
                         filepath: str) -> None:
        # Declare an empty list for names
        ppeclass_names = []
        # Read the file and add them to the list
        with open(filepath, "r") as file:
            ppeclass_names = [line.strip() for line in file.readlines()]
        # Loop and create a row for PPEClass table through each name
        for name in ppeclass_names:
            # Check if the current PPE class already exist in the table
            exist = self.session.query(PPEClass).filter_by(name=name).first()
            if exist is None:
                ppeclass = PPEClass(name=name)
                self.session.add(ppeclass)
            else:
                pass
                # print(f"{name} already exist!")
        self.session.commit()
        self.session.close()

    def insertDeviceDetails(
            self, 
            uuid: str, 
            password: str, 
            pub_topic: str, 
            sub_topic: str, 
            name: str, 
            description: str
        ) -> int:
        devicedetails_id = -1
        devicedetails = DeviceDetails()
        devicedetails.uuid = uuid
        devicedetails.password = password
        devicedetails.pub_topic = pub_topic
        devicedetails.sub_topic = sub_topic 
        devicedetails.name = name
        devicedetails.description = description
        self.session.add(devicedetails)
        self.session.flush()
        devicedetails_id = devicedetails.id
        self.session.commit() 
        self.session.close()
        return devicedetails_id

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

    def insertViolationDetailsToDeviceDetails(self, 
                               devicedetails_id: int,
                               violationdetails_id: int):
        devicedetails = self.session.query(DeviceDetails).filter_by(id=devicedetails_id).first()
        violationdetails = self.session.query(ViolationDetails).filter_by(id=violationdetails_id).first()
        if devicedetails is not None and violationdetails is not None:
            devicedetails.violationdetails.append(violationdetails)
            self.session.commit()
            self.session.close()
            return True
        return False

    def insertViolator(self, 
                       violationdetails_id: int, 
                       topleft: tuple, 
                       bottomright: tuple, 
                       detectedppe: list, 
                       verbose: bool = False, 
                       commit: bool = True) -> bool:

        violator_id = None 
        violationdetails = self.session.query(ViolationDetails).filter_by(id=violationdetails_id).first()

        if violationdetails is not None:

            detectedppe_to_be_added = []

            for ppeitem in detectedppe:
                ppeclass_name = ppeitem["class_name"]
                confidence = ppeitem["confidence"]
                ppeclass = self.session.query(PPEClass).filter_by(name=ppeclass_name).first()
                if ppeclass is not None:
                    detectedppe_to_be_added.append((ppeclass, confidence))
                else:
                    if verbose:
                        print(f"{ppeclass_name} does not exist!")
                    return None

            violator = Violator()
            violator.x1 = topleft[0]
            violator.y1 = topleft[1]
            violator.x2 = bottomright[0]
            violator.y2 = bottomright[1]
            violator.violationdetails = violationdetails

            while len(detectedppe_to_be_added) > 0:
                detected, confidence = detectedppe_to_be_added.pop(0)
                detectedppeclass = DetectedPPEClass()
                detectedppeclass.confidence = confidence
                violator.detectedppeclasses.append(detectedppeclass)
                detected.detectedppeclasses.append(detectedppeclass)

            self.session.add(violator)

            violator_id = violator.id

            if commit:
                if verbose:
                    print(f"Added {violator}")
                self.session.commit()
                self.session.close()

        return violator_id

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

    def getAllViolationDetails(self, 
                               from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"), 
                               to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59")) -> list:
        violation_details = self.session.query(ViolationDetails).filter(ViolationDetails.timestamp.between(from_datetime, to_datetime)).all()
        formatted_violation_details = []
        for violation_detail in violation_details:
            image = violation_detail.image
            timestamp = violation_detail.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            violators = []
            for violator in violation_details.violators:
                detected_ppe_classes = {
                        "no helmet": False,
                        "no glasses": False,
                        "no vest": False,
                        "no gloves": False,
                        "no boots": False,
                        "helmet": False,
                        "glasses": False,
                        "vest": False,
                        "gloves": False,
                        "boots": False
                }
                for item in violator.detectedppeclasses:
                    ppe_class_name = item.ppeclass.name
                    if ppe_class_name in detected_ppe_classes:
                        detected_ppe_classes[ppe_class_name] = True
                violators.append({
                    "detected_ppe_classes": detected_ppe_classes
                })
            formatted_violation_details.append({
                "image": image,
                "timestamp": timestamp,
                "violators": violators
            })
        return formatted_violation_details

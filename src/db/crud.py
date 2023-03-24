from .database import DatabaseHandler
from .tables import (
    PPEClass, 
    Violator, 
    DetectedPPEClass,
    Person,
    ViolationDetails
)
from datetime import datetime
import csv

class DatabaseCRUD(DatabaseHandler):
    
    """
    Methods:
        - insertPPEClasses          (filepath: str)
        - insertPersons             (filepath: str, 
                                     verbose=False)
        - getPPEClasses             ()
        - getPersons                ()
        - updatePerson              (person_id: int, 
                                     first_name: str = "", 
                                     middle_name: str = "", 
                                     last_name: str = "", 
                                     job_title: str = "")
        - deletePerson              (person_id: int)
        - insertViolator            (violationdetails_id: int, 
                                     person_id: int, 
                                     topleft: tuple, 
                                     bottomright: tuple, 
                                     detectedppeclasses: list, 
                                     verbose: bool = False, 
                                     commit: bool = True)
        - deleteViolator            (person_id: int, 
                                     commit: bool = True)
        - getAllViolationDetails    (from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"),
                                     to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59"))
    """

    def __init__(self, cfg=None, db_URL=None, echo=False):
        super(DatabaseCRUD, self).__init__(cfg, db_URL, echo)

    # Load the PPE classes that will be used for detection in PPE violations
    def insertPPEClasses(self, filepath: str):
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

    def insertPersons(self, filepath: str, verbose=False):
        persons = []
        with open(filepath, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                persons.append(row)
        for person_data in persons:
            exist = self.session.query(Person).filter_by(
                first_name=person_data["first_name"],
                middle_name=person_data["middle_name"],
                last_name=person_data["last_name"]
            ).first()
            if exist is None:
                person = Person(**person_data)
                self.session.add(person)
            else:
                if verbose:
                    print(f"{person_data['first_name']} {person_data['middle_name']} {person_data['last_name']} already exist!")
        self.session.commit()
        self.session.close()

    def getPPEClasses(self):
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

    def getPersons(self):
        """
        Get all persons from the database.
        """
        row = self.session.query(Person).all()
        persons = {}
        for col in row:
            person = {}
            for column in col.__table__.columns:
                person[column.name] = getattr(col, column.name)
            persons[person["id"]] = person # Use id from the database as key
            del person["id"] # Delete the id from the database because it is not necessary to be included in MQTT JSON data
        return persons

    def updatePerson(self, person_id: int, first_name: str="", middle_name: str="", last_name: str="", job_title: str=""):
        person = self.session.query(Person).filter_by(person_id=person_id).first()
        if person is not None:
            if len(first_name)>0: person.first_name = first_name
            if len(middle_name)>0: person.middle_name = middle_name
            if len(last_name)>0: person.last_name = last_name
            if len(job_title)>0: person.job_title = job_title
            self.session.commit()
            self.session.close()
            return True
        return False

    def deletePerson(self, person_id: int):
        person = self.session.query(Person).filter_by(person_id=person_id).first()
        if person is not None:
            self.session.delete(person)
            self.session.commit()
            return True
        return False

    def insertViolator(self, violationdetails_id: int, person_id: int, topleft: tuple, bottomright: tuple, detectedppeclasses: list, verbose=False, commit=True):
        violationdetails = self.session.query(ViolationDetails).filter_by(id=violationdetails_id).first()
        person = self.session.query(Person).filter_by(person_id=person_id).first()
        if person is not None and violationdetails is not None:
            violator = Violator()
            person.people.append(violator)
            violator.x1 = topleft[0]
            violator.y1 = topleft[1]
            violator.x2 = bottomright[0]
            violator.y2 = bottomright[1]
            violator.violationdetails = violationdetails
            for ppeclass_name in detectedppeclasses:
                ppeclass = self.session.query(PPEClass).filter_by(name=ppeclass_name).first()
                if ppeclass is not None:
                    detected = DetectedPPEClass()
                    violator.detectedppeclasses.append(detected)
                    ppeclass.detectedppeclasses.append(detected)
                else:
                    if verbose:
                        print(f"{ppeclass_name} does not exist!")
            self.session.add(violator)
            if commit:
                if verbose:
                    print(f"Added {violator}")
                self.session.commit()
                self.session.close()
        else:
            return False
        return True

    def deleteViolator(self, person_id: int, commit=True):
        person = self.session.query(Person).filter_by(person_id=person_id).all()
        if len(person) > 0:
            for same in person:
                self.session.delete(same)
            if commit:
                self.session.commit()
                self.session.close()
            return True
        return False

    def getAllViolationDetails(self, 
                               from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"), 
                               to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59")):
        violation_details = self.session.query(ViolationDetails).filter(ViolationDetails.timestamp.between(from_datetime, to_datetime)).all()
        print(violation_details)
        formatted_violation_details = []
        for violation_detail in violation_details:
            image = violation_detail.image
            timestamp = violation_detail.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            violators = []
            for violator in violation_detail.violators:
                recognized_persons = []
                first_name = violator.person.first_name
                middle_name = violator.person.middle_name
                last_name = violator.person.last_name
                recognized_persons.append(" ".join([first_name, middle_name, last_name]))
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
                    "recognized_persons": recognized_persons,
                    "detected_ppe_classes": detected_ppe_classes
                })
            formatted_violation_details.append({
                "image": image,
                "timestamp": timestamp,
                "violators": violators
            })
        return formatted_violation_details

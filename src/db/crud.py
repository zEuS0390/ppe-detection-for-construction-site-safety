from .database import DatabaseHandler
from .tables import (
    PPEClass, 
    Violator, 
    DetectedPPEClass,
    Person
)
import csv

# Load the PPE classes that will be used for detection in PPE violations
def loadPPEClasses(db: DatabaseHandler, filepath: str):
    # Declare an empty list for names
    ppeclass_names = []
    # Read the file and add them to the list
    with open(filepath, "r") as file:
        ppeclass_names = [line.strip() for line in file.readlines()]
    # Loop and create a row for PPEClass table through each name
    for name in ppeclass_names:
        # Check if the current PPE class already exist in the table
        exist = db.session.query(PPEClass).filter_by(name=name).first()
        if exist is None:
            ppeclass = PPEClass(name=name)
            db.session.add(ppeclass)
        else:
            pass
            # print(f"{name} already exist!")
    db.session.commit()
    db.session.close()

def insertPersons(db: DatabaseHandler, filepath: str):
    persons = []
    with open(filepath, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            persons.append(row)
    for person_data in persons:
        exist = db.session.query(Person).filter_by(
            first_name=person_data["first_name"],
            middle_name=person_data["middle_name"],
            last_name=person_data["last_name"]
        ).first()
        if exist is None:
            person = Person(**person_data)
            db.session.add(person)
        else:
            print(f"{person_data['first_name']} {person_data['middle_name']} {person_data['last_name']} already exist!")
    db.session.commit()
    db.session.close()

def loadPersons(db: DatabaseHandler):
    row = db.session.query(Person).all()
    persons = {}
    for col in row:
        person = {}
        for column in col.__table__.columns:
            person[column.name] = getattr(col, column.name)
        persons[person["id"]] = person
    return persons

def updatePerson(db: DatabaseHandler, person_id: int, first_name: str="", middle_name: str="", last_name: str="", job_title: str=""):
    person = db.session.query(Person).filter_by(person_id=person_id).first()
    if person is not None:
        if len(first_name)>0: person.first_name = first_name
        if len(middle_name)>0: person.middle_name = middle_name
        if len(last_name)>0: person.last_name = last_name
        if len(job_title)>0: person.job_title = job_title
        db.session.commit()
        db.session.close()
        return True
    return False

def deletePerson(db: DatabaseHandler, person_id: int):
    person = db.session.query(Person).filter_by(person_id=person_id).first()
    if person is not None:
        db.session.delete(person)
        db.session.commit()
        return True
    return False

def insertViolator(db: DatabaseHandler, person_id: int, coordinates: str, detectedppeclasses: list):
    person = db.session.query(Person).filter_by(person_id=person_id).first()
    if person is not None:
        violator = Violator()
        violator.person = person
        violator.coordinates = coordinates
        for ppeclass_name in detectedppeclasses:
            ppeclass = db.session.query(PPEClass).filter_by(name=ppeclass_name).first()
            detected = DetectedPPEClass()
            detected.ppeclass = ppeclass
            detected.violator = violator
        db.session.add(violator)
        db.session.commit()
        db.session.close()
    else:
        return False
    return True

def deleteViolator(db: DatabaseHandler, person_id: int):
    person = db.session.query(Person).filter_by(person_id=person_id).all()
    if len(person) > 0:
        for same in person:
            db.session.delete(same)
        db.session.commit()
        db.session.close()
        return True
    return False
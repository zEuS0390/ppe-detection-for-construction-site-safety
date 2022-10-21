from .database import DatabaseHandler
from .tables import PPEClass, Violator, DetectedPPEClass

def loadPPEClasses(db: DatabaseHandler, filepath: str):
    ppeclass_names = []
    with open(filepath, "r") as file:
        ppeclass_names = [line.strip() for line in file.readlines()]
    for name in ppeclass_names:
        exist = db.session.query(PPEClass).filter_by(name=name).first()
        if exist is None:
            ppeclass = PPEClass(name=name)
            db.session.add(ppeclass)
        else:
            print(f"{name} already exist!")
    db.session.commit()
    db.session.close()

def insertViolator(db: DatabaseHandler, name: str, position: str, detectedppeclasses: list):
    # Number of added detected classes
    violator = db.session.query(Violator).filter_by(name=name).first()
    if violator is None:
        violator = Violator()
        violator.name = name
        violator.position = position
        # Check the existence of each name from detectedppeclasses
        for ppeclass_name in detectedppeclasses:
            exist = db.session.query(PPEClass).filter_by(name=ppeclass_name).first()
            if exist is None:
                return False
        # Create and add detected ppe classes to violator
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

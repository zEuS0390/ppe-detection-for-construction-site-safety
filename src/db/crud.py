from .database import DatabaseHandler
from .tables import (
    PPEClass, 
    Violator, 
    DetectedPPEClass,
    User
)

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

def insertUser(db: DatabaseHandler, username: str, password: str):
    user =  db.session.query(User).filter_by(username=username).first()
    if user is None:
        user = User()
        user.username = username
        user.password = password
        user.online = False
        db.session.add(user)
        db.session.commit()
        db.session.close()
        return True
    return False

def logIn(db: DatabaseHandler, username: str, password: str):
    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        user.online = True
        return True
    return False

def logOut(db: DatabaseHandler, username: str):
    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        if user.online:
            user.online = False
            return True
    return False
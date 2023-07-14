import sys, os, random
sys.path.append(os.path.abspath("."))
from src.db.crud import DatabaseCRUD
from src.db.tables import *
from datetime import datetime

if __name__=="__main__":

    url = "mysql+mysqldb://{username}:{password}@{hostname}:{port}/{dbname}".format(
        hostname=os.environ.get("RDS_DB_HOSTNAME"),
        port=int(os.environ.get("RDS_DB_PORT")),
        username=os.environ.get("RDS_DB_USERNAME"),
        password=os.environ.get("RDS_DB_PASSWORD"),
        dbname=os.environ.get("RDS_DB_DBNAME")
    )
    
    db = DatabaseCRUD(
        db_URL=url
    )

    db.insertDeviceDetails(
        kvs_name="ppedetection-videostream",
        uuid="ZMCI1",
        password="pass123",
        pub_topic="ZMCI/test/notif",
        set_topic="ZMCI/test/set"
    )
    db.insertPPEClasses("cfg/detection/data_custom.names")

    ppeclasses = db.getPPEClasses()

    devicedetails = 1

    now = datetime.now()

    hours = 0
    minutes = 0

    for _ in range(50):

        if minutes > 30:
            hours += 1
            minutes = 0
        else:
            minutes += 1

        if hours > 23:
            print("[DATETIME]: Done")
            hours = 0
            break
        
        new = datetime(year=now.year, month=now.month, day=now.day, hour=hours, minute=minutes, second=0)

        violationdetails_id = db.insertViolationDetails(timestamp=new)

        result = db.insertViolationDetailsToDeviceDetails(1, violationdetails_id)

        if result:

            detectedppeclasses = [ppeclasses[random.randint(1, len(ppeclasses)-1)] for _ in range(random.randint(10, 12))]

            n = 0
            for detectedppe in detectedppeclasses:
                detectedppe["id"] = n
                detectedppe["confidence"] = random.randint(89, 99)
                detectedppe["bbox_overlaps"] = [random.randint(1, 50) for _ in range(random.randint(3, 5))]
                n += 1

            topleft = (random.randint(0, 640), random.randint(0, 480))
            bottomright = (random.randint(0, 640), random.randint(0, 480))

            result = db.insertViolator(violationdetails_id, 1, topleft, bottomright, detectedppeclasses, commit=False)

            if result:
                print(f"[{result}]: Successfully saved to the database.\n")
            else:
                print(f"[{result}]: Failed saving to the database.\n")

    db.session.commit()
    db.session.close()

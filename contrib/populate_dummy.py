import sys, os, random
sys.path.append(os.path.abspath("."))
from src.db.crud import DatabaseCRUD
from src.db.tables import *

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
        uuid="ZMCI01",
        password="pass123",
        pub_topic="ZMCI/test/notif",
        set_topic="ZMCI/test/set"
    )
    db.insertPPEClasses("cfg/detection/data_custom.names")

    ppeclasses = db.getPPEClasses()

    devicedetails = 1

    for _ in range(10):

        violationdetails_id = db.insertViolationDetails()
        result = db.insertViolationDetailsToDeviceDetails(1, violationdetails_id)

        if result:
            detectedppeclasses = [ppeclasses[random.randint(1, len(ppeclasses)-1)] for _ in range(random.randint(10, 12))]

            for detectedppe in detectedppeclasses:
                detectedppe["confidence"] = random.randint(89, 99)

            topleft = (random.randint(0, 640), random.randint(0, 480))
            bottomright = (random.randint(0, 640), random.randint(0, 480))

            result = db.insertViolator(violationdetails_id, topleft, bottomright, detectedppeclasses, commit=False)

            if result:
                sys.stdout.write(f"[{result}]: Successfully saved to the database.\n")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"[{result}]: Failed saving to the database.\n")
                sys.stdout.flush()

    db.session.commit()
    db.session.close()

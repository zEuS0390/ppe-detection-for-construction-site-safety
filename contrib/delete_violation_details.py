import os, sys
sys.path.append(os.path.abspath("."))
from src.db.crud import DatabaseCRUD
from src.db.tables import *

if __name__=="__main__":
    
    db = DatabaseCRUD(
        db_URL="mysql+mysqldb://{username}:{password}@{hostname}:{port}/{dbname}".format(
            hostname=os.environ.get("RDS_DB_HOSTNAME"),
            port=int(os.environ.get("RDS_DB_PORT")),
            username=os.environ.get("RDS_DB_USERNAME"),
            password=os.environ.get("RDS_DB_PASSWORD"),
            dbname=os.environ.get("RDS_DB_DBNAME")
        )
    )

    s3storage = S3Storage(
        aws_access_key_id=os.environ.get("AWS_S3_STORAGE_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_S3_STORAGE_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_S3_STORAGE_REGION")
    )

    allviolationdetails = db.session.query(ViolationDetails)

    for violationdetails in allviolationdetails:
        db.session.delete(violationdetails)
        db.session.commit()
    
    db.session.close()

    print("[SUCCESS]: Records have successfully been deleted. ")
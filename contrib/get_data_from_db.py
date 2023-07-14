import sys, os, json
sys.path.append(os.path.abspath("."))
from src.db.crud import DatabaseCRUD

url = "mysql+pymysql://{username}:{password}@{hostname}:{port}/{dbname}".format(
    hostname=os.environ.get("RDS_DB_HOSTNAME"),
    port=int(os.environ.get("RDS_DB_PORT")),
    username=os.environ.get("RDS_DB_USERNAME"),
    password=os.environ.get("RDS_DB_PASSWORD"),
    dbname=os.environ.get("RDS_DB_DBNAME")
)

db = DatabaseCRUD(db_URL=url)

print(json.dumps(db.getAllViolationDetails(devicedetails_uuid="ZMCI1"), indent=4))

from src.db.crud import DatabaseCRUD
from configparser import ConfigParser
from datetime import datetime
from openpyxl import Workbook
import os

def exportAsXLSX(cfg: ConfigParser,
                 path_to_directory: str = "data/export", 
                 from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"), 
                 to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59")):
    db = DatabaseCRUD.getInstance()
    list_of_violation_details = db.getAllViolationDetails(from_datetime, to_datetime)
    wb = Workbook()
    ws = wb.active
    with open(cfg.get("yolor", "classes")) as f:
        names = f.read().split('\n')
    names.remove("person")
    compliance = []
    noncompliance = []
    for name in names:
        if "no" in name:
            noncompliance.append(name)
        else:
            compliance.append(name)
    headers = ["timestamp", "person"] + compliance + noncompliance 
    ws.append(headers)
    filename = os.path.join(path_to_directory, from_datetime.replace(" ", "_").replace(":", "-")+"_TO_"+to_datetime.replace(" ", "_").replace(":", "-")+".xlsx")
    wb.save(filename)

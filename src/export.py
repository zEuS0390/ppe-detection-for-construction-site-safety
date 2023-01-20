from src.db.crud import DatabaseCRUD
from datetime import datetime
from openpyxl import Workbook
import os

def exportAsXLSX(path_to_directory: str = "data/export", 
                 from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"), 
                 to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59")):
    db = DatabaseCRUD.getInstance()
    list_of_violation_details = db.getAllViolationDetails(from_datetime, to_datetime)
    wb = Workbook()
    ws = wb.active
    headers = ["person", "no helmet", "no glasses", "no vest", "no gloves", "no boots", "helmet", "glasses", "vest", "gloves", "boots"]
    ws.append(headers)
    filename = os.path.join(path_to_directory, from_datetime.replace(" ", "_").replace(":", "-")+"_TO_"+to_datetime.replace(" ", "_").replace(":", "-")+".xlsx")
    wb.save(filename)

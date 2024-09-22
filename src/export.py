from src.db.crud import DatabaseCRUD
from configparser import ConfigParser
from datetime import datetime
from openpyxl import Workbook
import os

def exportAsXLSX(cfg: ConfigParser,
                 path_to_directory: str
                 from_datetime: datetime = datetime.now().strftime("%Y-%m-%d 00:00:00"),
                 to_datetime: datetime = datetime.now().strftime("%Y-%m-%d 23:59:59")):
  """
  Generate and export the requested data from the database to XLSX file.
  """
    db = DatabaseCRUD.getInstance()
    list_of_violation_details = db.getAllViolationDetails(from_datetime, to_datetime)
    wb = Workbook()
    ws = wb.active
    for violation_detail in list_of_violation_details:
        timestamp = violation_detail["timestamp"]
        for violator in violation_detail["violators"]:
            recognized_persons = "\n".join(violator["recognized_persons"])
            detected_ppe_classes = [violator["detected_ppe_classes"][ppe_class] for ppe_class in violator["detected_ppe_classes"]]
            ws.append([timestamp, recognized_persons] + detected_ppe_classes)
    filename = os.path.join(path_to_directory, from_datetime.replace(" ", "_").replace(":", "-")+"_TO_"+to_datetime.replace(" ", "_").replace(":", "-")+".xlsx")
    wb.save(filename)

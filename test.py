import unittest, configparser, os
from src.db.database import DatabaseHandler
from src.db.tables import PPEClass, Violator
from src.db.crud import insertViolator, loadPPEClasses
from sqlalchemy import select

# Test the Configuration File Contents
class TestConfigFiles(unittest.TestCase):

    def setUp(self):
        self.configparser = configparser.ConfigParser()
        self.configfile = "./cfg/config.ini"
    
    def test_read_config(self):
        self.assertTrue(os.path.exists(self.configfile), f"{self.configfile} file does not exist.")
        self.configparser.read(self.configfile)

    def test_yolor_filepaths(self):
        options = [
            "classes",
            "cfg"
        ]
        self.configparser.read(self.configfile)
        for option in options:
            filepath = self.configparser.get("yolor", option)
            self.assertTrue(os.path.exists(filepath), f"{filepath} file does not exist.")

    def test_device(self):
        self.configparser.read(self.configfile)
        device = self.configparser.get("yolor", "device")
        self.assertEqual(device, "cpu")

# Test Database CRUD Functions
class TestDatabaseCRUD(unittest.TestCase):

    def setUp(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read("./cfg/config.ini")
        self.db = DatabaseHandler("sqlite:///:memory:")

    def test_load_ppe_classes(self):
        loadPPEClasses(self.db, self.cfg.get("yolor", "classes"))
        self.db.session.execute(select(PPEClass)).all()

    def test_insert_violator(self):
        loadPPEClasses(self.db, self.cfg.get("yolor", "classes"))

        name = "John Smith"
        detected = ["no helmet", "no glasses", "no gloves", "no boots"]
        result = insertViolator(self.db, name, "(0, 0, 100, 400)", detected)
        self.assertTrue(result)

        # Insert violator entry with the same name
        name = "John Smith"
        detected = ["no helmet", "no glasses", "no gloves", "no boots"]
        result = insertViolator(self.db, name, "(0, 0, 100, 400)", detected)
        self.assertFalse(result)

        violator = self.db.session.query(Violator).filter_by(name=name).first()
        self.assertIsInstance(violator, Violator)

        # Insert with invalid class names
        name = "Nick Anderson"
        detected = ["no helmet", "pencil", "cap"]
        result = insertViolator(self.db, name, "(0, 0, 100, 400)", detected)
        self.assertFalse(result)

        violator = self.db.session.query(Violator).filter_by(name=name).first()
        self.assertIsNone(violator)

if __name__=="__main__":
    unittest.main()

import unittest, configparser, os
from src.db.database import DatabaseHandler
from src.db.tables import Person, Violator
from src.db.crud import deleteViolator, insertViolator, loadPPEClasses, loadPeople
from sqlalchemy import func
from faker import Faker
from csv import DictWriter

# Test the Configuration File Contents
class TestConfigFiles(unittest.TestCase):

    def setUp(self):
        self.configparser = configparser.ConfigParser()
        self.configfile = "./cfg/config.ini"
    
    def test_step_1_read_config(self):
        self.assertTrue(os.path.exists(self.configfile), f"{self.configfile} file does not exist.")
        self.configparser.read(self.configfile)

    def test_step_2_yolor_filepaths(self):
        options = [
            "classes",
            "cfg"
        ]
        self.configparser.read(self.configfile)
        for option in options:
            filepath = self.configparser.get("yolor", option)
            self.assertTrue(os.path.exists(filepath), f"{filepath} file does not exist.")

    def test_step_3_device(self):
        self.configparser.read(self.configfile)
        device = self.configparser.get("yolor", "device")
        self.assertEqual(device, "cpu")

# Test Database CRUD Functions
class TestDatabaseCRUD(unittest.TestCase):

    def setUp(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read("./cfg/config.ini")
        db_file = "data/testing.sqlite"
        self.db = DatabaseHandler(f"sqlite:///{db_file}")
        loadPPEClasses(self.db, self.cfg.get("yolor", "classes"))
        faker = Faker()
        with open(self.cfg.get("face_recognition", "people"), "w", newline="") as csv_file:
            fieldnames = ["person_id", "first_name", "middle_name", "last_name", "job_title"]
            writer = DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            number_of_people = 100
            people_ids = [i+1 for i in range(number_of_people)]
            people = [
                {
                    "person_id": people_ids.pop(0), 
                    "first_name": faker.unique.first_name(), 
                    "middle_name": faker.unique.last_name(), 
                    "last_name": faker.unique.last_name(),
                    "job_title": faker.unique.job()
                } for _ in range(number_of_people)
            ]
            writer.writerows(people)
        loadPeople(self.db, self.cfg.get("face_recognition", "people"))

    def test_step_1_insert_violator(self):
        # Insert violator entry with the correct inputs
        person_id = int("1")
        detected = ["no helmet", "no glasses", "no gloves", "no boots"]
        result = insertViolator(self.db, person_id, "(0, 0, 100, 400)", detected)
        self.assertTrue(result)

        # Insert violator entry with the same name (NOTE: This case is possible when there are multiple recognized faces)
        person_id = int("1")
        detected = ["no helmet", "no glasses", "no gloves", "no boots"]
        result = insertViolator(self.db, person_id, "(0, 0, 100, 400)", detected)
        self.assertTrue(result)

        # Check the number of rows in the Violator. The result should be 2, because insertion is performed twice
        count = self.db.session.query(func.count(Violator.id)).scalar()
        self.assertEqual(count, 2)

        # The person of violator should obtain the selected person_id 
        person_id = "1"
        person = self.db.session.query(Person).join(Violator).filter(Person.person_id==person_id).first()
        self.assertIsInstance(person, Person)
        
        # Insert violator entry with non existing person_id and unknown ppe classes
        person_id = "-1"
        detected = ["no helmet", "pencil", "cap"]
        result = insertViolator(self.db, person_id, "(0, 0, 100, 400)", detected)
        self.assertFalse(result)

    def test_step_2_delete_violator(self):
        # Delete violator with correct inputs
        result = deleteViolator(self.db, "1")
        self.assertTrue(result)

        # Delete the same violator once again
        result = deleteViolator(self.db, "1")
        self.assertFalse(result)

        count = self.db.session.query(func.count(Violator.id)).scalar()
        self.assertEqual(count, 0)

if __name__=="__main__":
    unittest.main()

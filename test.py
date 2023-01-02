import unittest, configparser, os
from src.db.tables import Person, Violator, ViolationDetails
from src.db.crud import DatabaseCRUD
from sqlalchemy import func
from faker import Faker
from csv import DictWriter

CONFIG_FILE = "./cfg/app.cfg"
DB_FILE = "data/test_db.sqlite"
PERSONS_FILE = "data/test_persons.csv"

# Test the Configuration File Contents
class TestConfigFiles(unittest.TestCase):

    def setUp(self):
        self.configparser = configparser.ConfigParser()
        self.configparser.read(CONFIG_FILE)

    def test_step_2_yolor_filepaths(self):
        options = [
            "classes",
            "cfg"
        ]
        for option in options:
            filepath = self.configparser.get("yolor", option)
            self.assertTrue(os.path.exists(filepath), f"{filepath} file does not exist.")

    def test_step_3_device(self):
        device = self.configparser.get("yolor", "device")
        self.assertEqual(device, "cpu")

# Test Local Database CRUD Functions
class TestDatabaseCRUD(unittest.TestCase):

    cfg = configparser.ConfigParser()
    db = DatabaseCRUD(db_URL=f"sqlite:///{DB_FILE}")
    faker = Faker()

    def setUp(self):
        self.cfg.read(CONFIG_FILE)

    @classmethod
    def tearDownClass(cls):
        cls.db.session.close()
        os.remove(PERSONS_FILE)
        os.remove(DB_FILE)

    def test_step_1_load_data(self):
        self.db.insertPPEClasses(self.cfg.get("yolor", "classes"))
        with open(PERSONS_FILE, "w", newline="") as csv_file:
            fieldnames = ["person_id", "first_name", "middle_name", "last_name", "job_title"]
            writer = DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            number_of_persons = 100
            persons_ids = [i+1 for i in range(number_of_persons)]
            persons = [
                {
                    "person_id": persons_ids.pop(0), 
                    "first_name": self.faker.unique.first_name(), 
                    "middle_name": self.faker.unique.last_name(), 
                    "last_name": self.faker.unique.last_name(),
                    "job_title": self.faker.unique.job()
                } for _ in range(number_of_persons)
            ]
            writer.writerows(persons)
        self.db.insertPersons(PERSONS_FILE)

    def test_step_2_insert_violation_details_with_violators(self):

        # Create violation details
        violationdetails = ViolationDetails()
        self.db.session.add(violationdetails)
        self.db.session.flush()
        violationdetails_id = violationdetails.id
        self.db.session.commit()
        self.db.session.close()

        # Insert violator entry with the correct inputs
        person_id = int("1")
        detected = ["no helmet", "no glasses", "no gloves", "no boots"]
        result = self.db.insertViolator(violationdetails_id, person_id, "(0, 0, 100, 400)", detected)
        self.assertTrue(result)

        # Insert violator entry with the same name (NOTE: This case is possible when there are multiple recognized faces)
        person_id = int("4")
        detected = ["no helmet", "no glasses", "no gloves", "no boots"]
        result = self.db.insertViolator(violationdetails_id, person_id, "(0, 0, 100, 400)", detected)
        self.assertTrue(result)

        # # Check the number of rows in the Violator. The result should be 2, because insertion is performed twice
        count = self.db.session.query(func.count(Violator.id)).scalar()
        self.assertEqual(count, 2)

        # # The person of violator should obtain the selected person_id 
        person_id = "1"
        person = self.db.session.query(Person).join(Violator).filter(Person.person_id==person_id).first()
        self.assertIsInstance(person, Person)

        # Insert violator entry with non existing person_id and unknown ppe classes
        person_id = "-1"
        detected = ["no helmet", "pencil", "cap"]
        result = self.db.insertViolator(violationdetails_id, person_id, "(0, 0, 100, 400)", detected)
        self.assertFalse(result)

    def test_step_3_update_person(self):
        person_id = int("2")
        result = self.db.updatePerson(
            
            person_id=person_id, 
            first_name=self.faker.unique.first_name(), 
            middle_name=self.faker.unique.last_name(), 
            last_name=self.faker.unique.last_name()
        )
        self.assertTrue(result)

    def test_step_4_delete_person(self):
        person_id = int("2")
        result = self.db.deletePerson(person_id=person_id)
        self.assertTrue(result)

    def test_step_5_delete_violator(self):
        # Delete violator with correct inputs
        result = self.db.deleteViolator("1")
        self.assertTrue(result)

        result = self.db.deleteViolator("4")
        self.assertTrue(result)

        # Delete the same violator once again
        result = self.db.deleteViolator("1")
        self.assertFalse(result)

        result = self.db.deleteViolator("4")
        self.assertFalse(result)

        count = self.db.session.query(func.count(Violator.id)).scalar()
        self.assertEqual(count, 0)

if __name__=="__main__":
    unittest.main()

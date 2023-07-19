import unittest, configparser, os
from src.db.tables import Violator, ViolationDetails, DeviceDetails
from src.db.crud import DatabaseCRUD
from sqlalchemy import func, and_
from faker import Faker
from csv import DictWriter
import time

CONFIG_FILE = "./cfg/app.cfg"
DB_FILE = "data/test_db.sqlite"

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

    violators = []
    cfg = configparser.ConfigParser()
    db = DatabaseCRUD(db_URL=f"sqlite:///{DB_FILE}")
    faker = Faker()

    def setUp(self):
        self.cfg.read(CONFIG_FILE)

    @classmethod
    def tearDownClass(cls):
        cls.db.session.close()
        cls.db.engine.dispose()
        os.remove(DB_FILE)

    def test_step_1_load_data(self):
        self.db.insertPPEClasses(self.cfg.get("yolor", "classes"))
        ppe_classes = self.db.getPPEClasses()
        self.assertGreater(len(ppe_classes), 0)
    
    def test_step_3_insert_violation_details_with_violators(self):

        ####################### FIRST DEVICEDETAILS #######################
        
        # Insert row in devicedetails table
        devicedetails_id = self.db.insertDeviceDetails(
            kvs_name="ppedetection_video_stream_test",
            bucket_name="ppedetection_s3_bucket_test",
            uuid="ppedetection_uuid_test",
            password="ppedetection_test_pass",
            pub_topic="ppedetection_pub_topic_test",
            set_topic="ppedetection_set_topic_test"
        )

        # Insert row in violationdetails table
        violationdetails_id = self.db.insertViolationDetails()

        # Connect row of violationdetails table to the row of devicedetails table
        self.db.insertViolationDetailsToDeviceDetails(
            devicedetails_id=devicedetails_id,
            violationdetails_id=violationdetails_id
        )

        violators = [
            {
                "id": 1,
                "x1": 0,
                "y1": 0,
                "x2": 0,
                "y2": 0,
                "violations": [
                    {"id": 1, "class_name": "no helmet", "confidence": 0.75, "overlaps": [1, 2]}, 
                    {"id": 2, "class_name": "no glasses", "confidence": 0.80, "overlaps": [1,]}, 
                    {"id": 8, "class_name": "no boots", "confidence": 0.90, "overlaps": [1,2]},
                    {"id": 4, "class_name": "no gloves", "confidence": 0.9, "overlaps": [1,]}
                ]
            },
            {
                "id": 2,
                "x1": 0,
                "y1": 0,
                "x2": 0,
                "y2": 0,
                "violations": [
                    {"id": 1, "class_name": "no helmet", "confidence": 0.75, "overlaps": [1, 2]}, 
                    {"id": 6, "class_name": "no glasses", "confidence": 0.98, "overlaps": [2,]}, 
                    {"id": 7, "class_name": "no gloves", "confidence": 0.91, "overlaps": [2,]}, 
                    {"id": 8, "class_name": "no boots", "confidence": 0.90, "overlaps": [2,1]}
                ]
            }
        ]

        self.db.insertViolators(
            violationdetails_id, 
            violators
        )
        
        count = self.db.session.query(func.count(Violator.id)).select_from(Violator).\
                join(ViolationDetails).\
                join(DeviceDetails).\
                filter(DeviceDetails.uuid=="ppedetection_uuid_test").scalar()

        self.assertEqual(count, 2)
        
        ####################### SECOND DEVICEDETAILS #######################

        # Insert row in devicedetails table
        devicedetails_id = self.db.insertDeviceDetails(
            kvs_name="ppedetection_video_stream_test_2",
            bucket_name="ppedetection_s3_bucket_test_2",
            uuid="ppedetection_uuid_test_2",
            password="ppedetection_test_pass_2",
            pub_topic="ppedetection_pub_topic_test_2",
            set_topic="ppedetection_set_topic_test_2"
        )

        # Insert row in violationdetails table
        violationdetails_id = self.db.insertViolationDetails()

        # Connect row of violationdetails table to the row of devicedetails table
        self.db.insertViolationDetailsToDeviceDetails(
            devicedetails_id=devicedetails_id,
            violationdetails_id=violationdetails_id
        )

        violators = [
            {
                "id": 1,
                "x1": 0,
                "y1": 0,
                "x2": 0,
                "y2": 0,
                "violations": [
                    {"id": 1, "class_name": "no helmet", "confidence": 0.75, "overlaps": [1, 2]}, 
                    {"id": 2, "class_name": "no glasses", "confidence": 0.80, "overlaps": [1,]}, 
                    {"id": 8, "class_name": "no boots", "confidence": 0.90, "overlaps": [1,2]},
                    {"id": 4, "class_name": "no gloves", "confidence": 0.9, "overlaps": [1,]}
                ]
            },
            {
                "id": 2,
                "x1": 0,
                "y1": 0,
                "x2": 0,
                "y2": 0,
                "violations": [
                    {"id": 1, "class_name": "no helmet", "confidence": 0.75, "overlaps": [1, 2]}, 
                    {"id": 6, "class_name": "no glasses", "confidence": 0.98, "overlaps": [2,]}, 
                    {"id": 10, "class_name": "no glasses", "confidence": 0.98, "overlaps": [2,3]}, 
                    {"id": 7, "class_name": "no gloves", "confidence": 0.91, "overlaps": [2,]}, 
                    {"id": 8, "class_name": "no boots", "confidence": 0.90, "overlaps": [2,1]}
                ]
            },
            {
                "id": 3,
                "x1": 0,
                "y1": 0,
                "x2": 0,
                "y2": 0,
                "violations": [
                    {"id": 9, "class_name": "no helmet", "confidence": 0.75, "overlaps": [3]}, 
                    {"id": 10, "class_name": "no glasses", "confidence": 0.98, "overlaps": [3]}, 
                    {"id": 11, "class_name": "no gloves", "confidence": 0.91, "overlaps": [3]}, 
                    {"id": 12, "class_name": "no boots", "confidence": 0.90, "overlaps": [3]}
                ]
            }
        ]

        self.db.insertViolators(
            violationdetails_id, 
            violators
        )

        count = self.db.session.query(func.count(Violator.id)).select_from(Violator).\
                join(ViolationDetails).\
                join(DeviceDetails).\
                filter(DeviceDetails.uuid=="ppedetection_uuid_test_2").scalar()

        self.assertEqual(count, 3)

    def test_step_5_query_violators(self):

        # Check the number of overlappingviolators in the detectedppeclasses of the violator with bbox_id and violationdetails's id
        violator = self.db.session.query(Violator).join(ViolationDetails).filter(and_(Violator.bbox_id==1, ViolationDetails.id==1)).scalar()
        
        for detectedppeclass in violator.detectedppeclasses:
            class_name = detectedppeclass.ppeclass.class_name
            number_of_violators = len(detectedppeclass.violators)
            if class_name in ["no helmet", "no boots"]:
                self.assertEqual(number_of_violators, 2)

        # Check the number of overlappingviolators in the detectedppeclasses of the violator with bbox_id and violationdetails's id
        violator = self.db.session.query(Violator).join(ViolationDetails).filter(and_(Violator.bbox_id==2, ViolationDetails.id==2)).scalar()
        
        for detectedppeclass in violator.detectedppeclasses:
            class_name = detectedppeclass.ppeclass.class_name
            number_of_violators = len(detectedppeclass.violators)
            if class_name in ["no helmet", "no boots"]:
                self.assertEqual(number_of_violators, 2)
            elif class_name in ["no glasses"]:
                try:
                    self.assertEqual(number_of_violators, 1)
                except:
                    self.assertEqual(number_of_violators, 2)
                

    def test_step_6_delete_violator(self):
        # Delete violator with correct inputs

        # Check the number of violators
        count = self.db.session.query(func.count(Violator.id)).\
                select_from(Violator).\
                join(ViolationDetails).\
                filter(ViolationDetails.id==1)\
                .scalar()
        self.assertEqual(count, 2)

        # Get the instance of the violator
        violator = self.db.session.query(Violator).\
                join(ViolationDetails).\
                filter(and_(
                    Violator.id==1, 
                    ViolationDetails.id==1
                )).scalar()

        # Deleting the first violator
        self.db.session.delete(violator)

        # Check the number of violators
        count = self.db.session.query(func.count(Violator.id)).\
                select_from(Violator).\
                join(ViolationDetails).\
                filter(ViolationDetails.id==1)\
                .scalar()

        self.assertEqual(count, 1)

        # Get the instance of the violator
        violator = self.db.session.query(Violator).\
                join(ViolationDetails).\
                filter(and_(
                    Violator.id==2, 
                    ViolationDetails.id==1
                )).scalar()

        # Deleting the second violator
        self.db.session.delete(violator)

        # Check the number of violators
        count = self.db.session.query(func.count(Violator.id)).\
                select_from(Violator).\
                join(ViolationDetails).\
                filter(ViolationDetails.id==1)\
                .scalar()

        self.assertEqual(count, 0)

    def test_step_7_update_device_details_status(self):
        result = self.db.setDeviceDetailsStatus("doesnotexist", False)
        self.assertFalse(result)

if __name__=="__main__":
    unittest.main()

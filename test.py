import unittest, configparser, os

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
            "cfg",
            "weights"
        ]
        self.configparser.read(self.configfile)
        for option in options:
            filepath = self.configparser.get("yolor", option)
            self.assertTrue(os.path.exists(filepath), f"{filepath} file does not exist.")

    def test_device(self):
        self.configparser.read(self.configfile)
        device = self.configparser.get("yolor", "device")
        self.assertEqual(device, "cpu")

if __name__=="__main__":
    unittest.main()
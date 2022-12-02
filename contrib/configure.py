from configparser import ConfigParser
import os

APP_CFG_FILENAME = "cfg/app.cfg"
DETECTION_CFG_FILENAME = "cfg/detection/config.cfg"

app_cfg = ConfigParser()
app_cfg.read(APP_CFG_FILENAME)
detection_cfg = ConfigParser()
detection_cfg.read(DETECTION_CFG_FILENAME)

def clear():
    os.system("clear")

def parsePlainConfig(filepath: str):
    if not os.path.exists(filepath):
        raise Exception(f"'{filepath}' does not exist.")
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
            cfg = {}
            for line in lines:
                separator_index = line.find(":")
                key = line[:separator_index]
                value = line[separator_index+1:].strip()
                cfg[key] = value
            return cfg
    except Exception as e:
        raise e

class Configure:

    def __init__(self):
        self.selectOption()

    def executeSelectedOption(self, options):
        optionLength = len(options)
        selected = input(f"Select 1-{optionLength} [0 to cancel]: ")
        while not selected.isdigit():
            selected = input(f"Select 1-{optionLength} [0 to cancel]: ")
        while int(selected) < 0 or int(selected) > optionLength:
            selected = input(f"Select 1-{optionLength} [0 to cancel]: ")
            while not selected.isdigit():
                selected = input(f"Select 1-{optionLength} [0 to cancel]: ")
        if int(selected) == 0:
            return
        options[int(selected)-1][1]()

    def displayOptions(self, title, options):
        buffer = f"{title} Options:\n"
        for index, option in enumerate(options):
            buffer += f"{index+1}. {option[0].title()}\n"
        print(buffer, end="")

    def configureCameraDetails(self):
        clear()
        def setName():
            name = input("Enter name: ")
            app_cfg.set("camera", "name", name)
            with open(APP_CFG_FILENAME, "w") as cfgfile:
                app_cfg.write(cfgfile)
        def setDescription():
            desc = input("Enter description: ")
            app_cfg.set("camera", "description", desc)
            with open(APP_CFG_FILENAME, "w") as cfgfile:
                app_cfg.write(cfgfile)
        options = [
            ("name", setName), 
            ("description", setDescription)
        ]
        self.displayOptions("Camera Details", options)
        self.executeSelectedOption(options)
        self.selectOption()

    def configureFaceRecognition(self):
        pass

    def configureDetection(self):
        clear()
        def setPPEPreferenceState(ppe_item):
            state = input("Select state [on/off/cancel]: ")
            while state not in ["on", "off", "cancel"]:
                state = input("Select state [on/off/cancel]: ")
            if state == "cancel":
                return
            detection_cfg.set("ppe_preferences", ppe_item, state)
            with open(DETECTION_CFG_FILENAME, "w") as cfgfile:
                detection_cfg.write(cfgfile)
        options = [
            ("Helmet", lambda: setPPEPreferenceState("helmet")),
            ("No Helmet", lambda: setPPEPreferenceState("no helmet")),
            ("Glasses", lambda: setPPEPreferenceState("glasses")),
            ("No Glasses", lambda: setPPEPreferenceState("no glasses")),
            ("Vest", lambda: setPPEPreferenceState("vest")),
            ("No Vest", lambda: setPPEPreferenceState("no vest")),
            ("Gloves", lambda: setPPEPreferenceState("gloves")),
            ("No Gloves", lambda: setPPEPreferenceState("no gloves")),
            ("Boots", lambda: setPPEPreferenceState("boots")),
            ("No Boots", lambda: setPPEPreferenceState("no boots")),
        ]
        self.displayOptions("PPE Preference", options)
        self.executeSelectedOption(options)
        self.selectOption()

    def configureMQTTConnection(self):
        pass

    def configureSFTPConnection(self):
        pass

    def selectOption(self):
        clear()
        configuration_options = [
            ("camera details", self.configureCameraDetails),
            ("face recognition", self.configureFaceRecognition),
            ("detection", self.configureDetection),
            ("mqtt connection", self.configureMQTTConnection),
            ("sftp connection", self.configureSFTPConnection)
        ]
        self.displayOptions("Application", configuration_options)
        self.executeSelectedOption(configuration_options)

if __name__=="__main__":
    setconfig = Configure()
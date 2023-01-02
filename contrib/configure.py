from configparser import ConfigParser
from getpass import getpass
import os, sys

APP_CFG_FILENAME = "cfg/app.cfg"
DETECTION_CFG_FILENAME = "cfg/detection/config.cfg"
MQTT_CLIENT_NOTIF_FILENAME = "cfg/client/mqtt/notif.cfg"
MQTT_CLIENT_SET_FILENAME = "cfg/client/mqtt/set.cfg"

app_cfg = ConfigParser()
app_cfg.read(APP_CFG_FILENAME)
detection_cfg = ConfigParser()
detection_cfg.read(DETECTION_CFG_FILENAME)

def clear():
    if sys.platform == "linux":
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")

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

def setPlainConfig(filepath, target_key, new_value):
    if not os.path.exists(filepath):
        raise Exception(f"'{filepath}' does not exist.")
    try:
        cfg = {}
        with open(filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                separator_index = line.find(":")
                key = line[:separator_index]
                value = line[separator_index+1:].strip()
                cfg[key] = value
        if target_key in cfg:
            cfg[target_key] = new_value
            with open(filepath, "w") as file:
                content = ""
                for key, value in cfg.items():
                    content += ": ".join([key, value]) + "\n"
                file.write(content)
    except Exception as e:
        raise e

def getPlainConfig(filepath, target_key):
    if not os.path.exists(filepath):
        raise Exception(f"'{filepath}' does not exist.")
    try:
        cfg = {}
        with open(filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                separator_index = line.find(":")
                key = line[:separator_index]
                value = line[separator_index+1:].strip()
                cfg[key] = value
        return cfg
    except Exception as e:
        raise e

class Configure:

    def executeSelectedOption(self, options):
        optionLength = len(options)
        selected = input(f"\n\tSelect 1-{optionLength} [0 to cancel]: ")
        while not selected.isdigit():
            selected = input(f"\tSelect 1-{optionLength} [0 to cancel]: ")
        while int(selected) < 0 or int(selected) > optionLength:
            selected = input(f"\tSelect 1-{optionLength} [0 to cancel]: ")
            while not selected.isdigit():
                selected = input(f"\tSelect 1-{optionLength} [0 to cancel]: ")
        if int(selected) == 0:
            return
        options[int(selected)-1][1]()

    def displayOptions(self,options):
        buffer = "\n\tOptions:\n"
        for index, option in enumerate(options):
            buffer += f"\t{index+1}. {option[0].title()}\n"
        print(buffer, end="")

    def configureCameraDetails(self):
        clear()
        def setName():
            name = input("\tEnter name: ")
            app_cfg.set("camera", "name", name)
            with open(APP_CFG_FILENAME, "w") as cfgfile:
                app_cfg.write(cfgfile)
        def setDescription():
            desc = input("\tEnter description: ")
            app_cfg.set("camera", "description", desc)
            with open(APP_CFG_FILENAME, "w") as cfgfile:
                app_cfg.write(cfgfile)
        options = [
            ("name", setName), 
            ("description", setDescription)
        ]
        print("\n\tCamera Details")
        print("\n\tCurrent Values:")
        print("\tNAME:", app_cfg.get("camera", "name"))
        print("\tDESCRIPTION:", app_cfg.get("camera", "description"))
        self.displayOptions(options)
        self.executeSelectedOption(options)
        self.selectOption()

    def configureFaceRecognition(self):
        clear()
        def setModelsDir():
            modelsdir = input("\tEnter Directory: ")
            app_cfg.set("face_recognition", "models_dir", modelsdir)
            with open(APP_CFG_FILENAME, "w") as cfgfile:
                app_cfg.write(cfgfile)
        options = [
            ("Models Directory", setModelsDir)
        ]
        print("\n\tFace Recognition")
        print("\n\tCurrent Values:")
        print("\tMODELS DIRECTORY:", app_cfg.get("face_recognition", "models_dir"))
        self.displayOptions(options)
        self.executeSelectedOption(options)
        self.selectOption()

    def configureDetection(self):
        clear()
        def setPPEPreferenceState(ppe_item):
            state = input("\tSelect state [on/off/cancel]: ")
            while state not in ["on", "off", "cancel"]:
                state = input("\tSelect state [on/off/cancel]: ")
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
        print("\n\tPPE Preference")
        print("\n\tCurrent Values:")
        for index in range(len(options)):
            ppe_item = options[index][0].lower().replace(" ", "_")
            status = "on" if detection_cfg.getboolean("ppe_preferences", ppe_item) else "off"
            print(f"\t{options[index][0].upper()} = {status}")
        self.displayOptions(options)
        self.executeSelectedOption(options)
        self.selectOption()

    def configureMQTTConnection(self):
        clear()
        def setClientName():
            client_name = input("\tEnter client name: ")
            client_name.replace(" ", "-")
            setPlainConfig(MQTT_CLIENT_NOTIF_FILENAME, "client_id_name", client_name+"-notif")
            setPlainConfig(MQTT_CLIENT_SET_FILENAME, "client_id_name", client_name+"-set")
            setPlainConfig(MQTT_CLIENT_NOTIF_FILENAME, "topic_name", client_name+"/notif")
            setPlainConfig(MQTT_CLIENT_SET_FILENAME, "topic_name", client_name+"/set")
        def setHostName():
            ipaddr = input("\tEnter broker ip: ")
            setPlainConfig(MQTT_CLIENT_NOTIF_FILENAME, "broker_ip", ipaddr)
            setPlainConfig(MQTT_CLIENT_SET_FILENAME, "broker_ip", ipaddr)
        def setUserName():
            username = input("\tEnter user name: ")
            setPlainConfig(MQTT_CLIENT_NOTIF_FILENAME, "username", username)
            setPlainConfig(MQTT_CLIENT_SET_FILENAME, "username", username)
        def setPassword():
            password = getpass("\tEnter password: ")
            setPlainConfig(MQTT_CLIENT_NOTIF_FILENAME, "password", password)
            setPlainConfig(MQTT_CLIENT_SET_FILENAME, "password", password)
        options = [
            ("client id name", setClientName),
            ("broker ip", setHostName),
            ("username", setUserName),
            ("password", setPassword)
        ]
        print("\n\tMQTT Connection")
        print("\n\tCurrent Values:")
        current_values = getPlainConfig(MQTT_CLIENT_NOTIF_FILENAME, "client_id_name")
        client_id_name_last_index = current_values["client_id_name"].find("-notif")
        current_values["client_id_name"] = current_values["client_id_name"][:client_id_name_last_index] if client_id_name_last_index != -1 else "None"
        current_values["password"] = len(current_values["password"])*"*"
        for index in range(len(options)):
            item = options[index][0].lower().replace(" ", "_")
            print(f"\t{options[index][0].upper()} = {current_values[item]}")
        self.displayOptions(options)
        self.executeSelectedOption(options)
        self.selectOption()

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
        print("\n\tApplication")
        self.displayOptions(configuration_options)
        self.executeSelectedOption(configuration_options)

if __name__=="__main__":
    Configure().selectOption()
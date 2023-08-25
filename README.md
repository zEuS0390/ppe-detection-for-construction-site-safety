[![](https://img.shields.io/badge/TIP-Quezon%20City-yellow)](https://tip.edu.ph/)
[![.github/workflows/app_server.yml](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml/badge.svg?event=push)](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml)

<!-- Background image by pikisuperstar: https://www.freepik.com/free-vector/geometric-abstract-green-background_6189913.htm#query=black%20green%20polygon&position=24&from_view=search&track=ais -->
![Untitled-1](https://github.com/cpe-pd/ppe-for-construction-detection/assets/39390245/53f0fdc5-fc15-4667-8d9b-bc875c31d87c)

## 📓 About
This is the official repository of our PPE detection application for construction safety which is part of the whole system in our capstone project. It analyzes the detected PPE from the camera stream and evaluates the violations of each person present. When obtaining the output from the detection, it will be consolidated as a payload for the clients to be received via the lightweight messaging protocol called [MQTT](https://en.wikipedia.org/wiki/MQTT). These clients are safety officers because they are the people who have the authority and responsibility within the area regarding the safety of the people.

## 🤝 Team Members
<div align="center">
  <table>
    <tbody>
      <tr height=200>
        <!-- zEuS0390 -->
        <td align="center">
          <a href="https://github.com/zEuS0390">
            <img src="https://avatars2.githubusercontent.com/u/39390245" width=150 height=150 alt="zEuS0390">
            <br>
            <b>Zeus James Baltazar</b>
          </a>
          <br>
          <sub><b>Intelligent Systems</b></sub>
        </td>
        <!-- mahteenbash -->
        <td align="center">
          <a href="https://github.com/mahteenbash">
            <img src="https://avatars2.githubusercontent.com/u/79791506" width=150 height=150 alt="mahteenbash">
            <br>
            <b>Martin Lorenzo Basbacio</b>
          </a>
          <br>
          <sub><b>Data Science</b></sub>
        </td>
        <!-- clarencelarrosa -->
        <td align="center">
          <a href="https://github.com/clarencelarrosa">
            <img src="https://avatars2.githubusercontent.com/u/89871460" width=150 height=150 alt="clarencelarrosa">
            <br>
            <b>Clarence Gail Larrosa</b>
          </a>
          <br>
          <sub><b>Intelligent Systems</b></sub>
        </td>
        <!-- ianmarquez1129 -->
        <td align="center">
          <a href="https://github.com/ianmarquez1129">
            <img src="https://avatars2.githubusercontent.com/u/51940497" width=150 height=150 alt="ianmarquez1129">
            <br>
            <b>Ian Gabriel Marquez</b>
          </a>
          <br>
          <sub><b>System Administration</b></sub>
        </td>
      </tr>
    </tbody>
  </table>
</div>

- <b>Zeus James Baltazar (zEuS0390)</b> - He is the lead developer and focuses mostly on the utilization of ideas brought on by the team.
- <b>Martin Lorenzo Basbacio (mahteenbash)</b> - He facilitates the methods regarding data science concepts such as object detection.
- <b>Clarece Gail Larrosa (clarencelarrosa)</b> - She mostly manages and maintains the documentation of the project.
- <b>Ian Gabriel Marquez (ianmarquez1129)</b> - He handles the development of the mobile application and its UI/UX design.

## ✔️ Features
- Can be used in a cloud or local environment
- Detects 5 basic PPE for construction safety and without wearing them
- Detects a human person to determine worker violations
- Delivers real-time reports for the mobile application

## System Flowchart
<p align="center">
  <img src="https://user-images.githubusercontent.com/39390245/226389227-8c31513f-9587-465d-b0f2-0c762376fca3.png" width=640 height=720 alt="System Flowchart">
</p>

## ⚙️ Hardware Design
We used a Raspberry Pi 4 Model B and an OKdo camera module in this project. Additionally, we included some minor components to help the user determine the status of the device and physically turn it off. These components are: an RGB LED light, a piezo buzzer, and a tactile switch. A tripod can also be attached and detached to the bottom of the enclosure to adjust the angle of the camera, which aids the mobility of the device. Ventilation also plays a vital role in every hardware. Therefore, in the enclosure, the exhausts are found at the top, right, and left.

<details>
  <summary>Raspberry Pi Specifications</summary>
  <br>
  <table>
    <tbody>
      <tr>
        <td align="center">CPU</td>
        <td align="center">BCM2835 ARM Quad-Core 64-bit @ 1.8GHz</td>
      </tr>
      <tr>
        <td align="center">OS</td>
        <td align="center">Debian GNU/Linux 11 (bullseye) aarch64</td>
      </tr>
      <tr>
        <td align="center">RAM</td>
        <td align="center">8 GB</td>
      </tr>
    </tbody>
  </table>
</details>

<details>
  <summary>OKdo Camera Module Specifications</summary>
  <br>
  <table>
    <tbody>
      <tr>
        <td align="center">Sensor</td>
        <td align="center">5MP OV5647</td>
      </tr>
      <tr>
        <td align="center">Resolution</td>
        <td align="center">1080p</td>
      </tr>
      <tr>
        <td align="center">FPS</td>
        <td align="center">30</td>
      </tr>
    </tbody>
  </table>
</details>

<br>

<p align="center">
  <img src="https://github.com/cpe-pd/ppe-for-construction-detection/assets/39390245/a2b2c684-8e8b-4dfc-8ccd-4327aa1bb156" width=640 height=480 alt="hardware-design-1">
  <br>
  <img src="https://github.com/cpe-pd/ppe-for-construction-detection/assets/39390245/60148172-3349-4ee7-8db2-3c5212fde6b4" width=640 height=480 alt="hardware-design-2">
  <br>
  <img src="https://github.com/cpe-pd/ppe-for-construction-detection/assets/39390245/7409e33a-18db-450e-8ccb-a4faa04a0a98" width=640 height=480 alt="hardware-design-3">
</p>

## 🔍 Model Classes
The trained model covers eleven classes. It can detect compliant and noncompliant PPE for construction, it can also detect persons which aids the application to determine particular violations.
<ul>
  <li>Helmet</li>
  <li>No Helmet</li>
  <li>Glasses</li>
  <li>No Glasses</li>
  <li>Vest</li>
  <li>No Vest</li>
  <li>Gloves</li>
  <li>No Gloves</li>
  <li>Boots</li>
  <li>No Boots</li>
  <li>Person</li>
</ul>

## 📊 Datasets
The trained model was trained using these datasets with different image augmentation. The custom dataset used in this project were pre-processed and thoroughly scanned and labeled following the classes mentioned above. Images were resized to 640x640 and provided with different augmentations. The final datasets are split into three different sets 70% Training Set, 20% Validation Set, and 10% Testing Set.

The datasets are available in these links:
<ul>
  <li>
    Part 1:   
    <a href="https://universe.roboflow.com/pd2/ppev5">
        <img src="https://app.roboflow.com/images/download-dataset-badge.svg"></img>
    </a>
  </li>
  <li>
    Part 2:   
    <a href="https://universe.roboflow.com/pd2v2/ppev5_v2">
        <img src="https://app.roboflow.com/images/download-dataset-badge.svg"></img>
    </a>
  </li>
</ul>

## 🚀 Installation
To get started, install the required dependencies. It is highly recommended to use virtual environment ([Pipenv](https://pypi.org/project/pipenv/), [Virtualenv](https://pypi.org/project/virtualenv/)) to isolate them to the system. 

There are some external dependencies that are not included in the script. Download and install them first before continuing to the next step. 

After that, just run this script and it will handle the installation.
```bash
./scripts/linux/install.sh
```

Download and install mosquitto from https://mosquitto.org/download/. Make sure to set it as a service to automatically start itself during system startup. There should be username and password set up in the configuration by creating a password file (e.g. `passwd_file`):
```bash
# Uncomment the following values in this configuration file: mosquitto.conf

listener 1883
password_file passwd_file
allow_anonymous false
```
To create a username and password, enter this command:
```bash
# Note: `admin` is a username, you can change it if you want
# After entering this command, it will prompt for a password
mosquitto_passwd passwd_file admin
```
This is optional, but if you want to run the broker manually instead of a service, then run this command:
```
mosquitto -c mosquitto.conf -v
```

## 🎦 Demonstration
We are currently doing some tests on various construction sites to determine the quality of the system and draw conclusions about the accomplished objectives, particularly the accuracy of detection.
<ul>
  <li><a href="https://youtu.be/9GrYwxQUfOI">PPE for Construction Detection Test #1</a></li>
  <li><a href="https://youtu.be/NdW77oMXwo8">PPE for Construction Detection Test #2</a></li>
  <li><a href="https://youtu.be/BJzhbw56-tE">PPE for Construction Detection Test #3</a></li>
  <li><a href="https://youtu.be/ogvOjIQox6o">PPE for Construction Detection Test #4</a></li>
  <li><a href="https://youtu.be/HjcbnA7a1iU">PPE for Construction Detection Test #5</a></li>
</ul>

## Acknowledgments
- https://github.com/aws-samples/amazon-kinesis-video-streams-consumer-library-for-python/
- https://en.wikipedia.org/wiki/Representational_state_transfer/
- https://en.wikipedia.org/wiki/Light-emitting_diode/
- https://en.wikipedia.org/wiki/Bounding_volume/
- https://learn.microsoft.com/en-us/powershell/
- https://en.wikipedia.org/wiki/Push-button/
- https://www.django-rest-framework.org/
- https://github.com/WongKinYiu/yolor/
- https://en.wikipedia.org/wiki/Base64/
- https://en.wikipedia.org/wiki/Buzzer/
- https://www.gnu.org/software/bash/
- https://en.wikipedia.org/wiki/Linux/
- https://gstreamer.freedesktop.org/
- https://en.wikipedia.org/wiki/API/
- https://www.raspberrypi.com/
- https://www.sqlalchemy.org/
- https://www.virtualbox.org/
- https://www.paramiko.org/
- https://www.openssh.com/
- https://aws.amazon.com/
- https://www.python.org/
- https://www.sqlite.org/
- https://mosquitto.org/
- https://colab.google/
- https://git-scm.com/
- https://opencv.org/
- https://mqtt.org/

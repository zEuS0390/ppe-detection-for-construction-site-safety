[![](https://img.shields.io/badge/TIP-Quezon%20City-yellow)](https://tip.edu.ph/)
[![.github/workflows/app_server.yml](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml/badge.svg?event=push)](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml)

<!-- Background image by pikisuperstar: https://www.freepik.com/free-vector/geometric-abstract-green-background_6189913.htm#query=black%20green%20polygon&position=24&from_view=search&track=ais -->
![banner-image](https://github.com/zEuS0390/ppe-for-construction-safety-detection/assets/39390245/dba51548-d7f9-4db0-818e-682265c281c8)

## 📓 About
This is the official repository of our PPE detection application for construction safety which is part of the whole system in our capstone project. It analyzes the detected PPE from the camera stream and evaluates the violations of each person present using an object detection algorithm called [YOLOR](https://github.com/WongKinYiu/yolor). When obtaining the output from the detection, it will be consolidated as a payload for the clients to be received via the lightweight messaging protocol called [MQTT](https://en.wikipedia.org/wiki/MQTT). These clients are safety officers because they are the people who have the authority and responsibility within the area regarding the safety of the people.

## 🤝 Team Members
Our team is a dynamic group, encompassing a wide range of skills, expertise, and backgrounds that collectively drive our project forward. The dedication of each member to their designated role results in great productivity and a remarkable team.

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
- Mainly cloud-based but can be utilized into a local-based by configuration
- Detects 5 basic PPE for construction safety and another 5 without wearing them
- Detects a human person to determine worker violations
- Delivers real-time reports for the mobile application via MQTT
- Retains data in storage and database for future processing

## 📓 System Flowchart
The flowchart illustrates how the input flows throughout the system. It starts from capturing the video stream from the Raspberry Pi until receiving the outputs from the detection for the users.

<p align="center">
  <img src="https://github.com/zEuS0390/ppe-for-construction-safety-detection/assets/39390245/63166846-f42d-4dbe-ae83-dd3c646c982a" width=640 height=640 alt="System Flowchart">
</p>

## 📔 Data Flow Diagram
The diagram outlines the interactions between various entities for the mobile application. Basically, the hardware device captures the real-time video stream and sends it into a service provided by the Amazon Web Service (AWS) cloud platform. 
<p align="center">
  <img src="https://github.com/zEuS0390/ppe-for-construction-safety-detection/assets/39390245/9d3a1f27-1f4e-4331-874a-b6d3404945e0" width=640 height=640 alt="Data Flow Diagram">
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
  <img src="https://github.com/zEuS0390/ppe-for-construction-safety-detection/assets/39390245/e2374d34-2f7d-48cd-9778-d72d6c502aa7" width=640 height=480 alt="hardware-design-1">
  <br>
  <img src="https://github.com/zEuS0390/ppe-for-construction-safety-detection/assets/39390245/7a1c1573-a6d3-4bb3-9562-e09a050a0de8" width=640 height=480 alt="hardware-design-2">
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
The model was trained using these datasets with different image augmentation. The custom datasets used in this project were pre-processed and thoroughly scanned and labeled following the classes mentioned above. Images were resized to 640x640 and provided with different augmentations. The final datasets are split into three different sets: 70% training Set, 20% validation set, and 10% testing set.

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
**NOTE:** Disregard this section if the application is set to the cloud environment. This is only applicable to the local environment as it uses LAN-based broker to communicate with other devices.

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
After conducting tests at various construction sites to evaluate the system's quality, we have successfully achieved all of our objectives, especially in terms of detection accuracy.

<ul>
  <li><a href="https://youtu.be/9GrYwxQUfOI">Multiple PPE for Construction Safety Monitoring System Test (Local-based) #1</a></li>
  <li><a href="https://youtu.be/NdW77oMXwo8">Multiple PPE for Construction Safety Monitoring System Test (Local-based) #2</a></li>
  <li><a href="https://youtu.be/BJzhbw56-tE">Multiple PPE for Construction Safety Monitoring System Test (Local-based) #3</a></li>
  <li><a href="https://youtu.be/ogvOjIQox6o">Multiple PPE for Construction Safety Monitoring System Test (Local-based) #4</a></li>
  <li><a href="https://youtu.be/HjcbnA7a1iU">Multiple PPE for Construction Safety Monitoring System Test (Local-based) #5</a></li>
  <li><a href="https://youtu.be/EVROnbGXeik">Multiple PPE for Construction Safety Monitoring System Demo (Cloud-based with AWS) #1</a></li>
  <li><a href="https://youtu.be/_-cMzedA5Qk">Multiple PPE for Construction Safety Monitoring System Demo (Cloud-based with AWS) #2</a></li>
  <li><a href="https://youtu.be/L9Klephq1J8">Multiple PPE for Construction Safety Monitoring System Demo (Cloud-based with AWS) #3</a></li>
</ul>

## 📎 Acknowledgments
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

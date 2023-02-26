[![](https://img.shields.io/badge/TIP-Quezon%20City-yellow)](https://tip.edu.ph/)
[![.github/workflows/app_server.yml](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml/badge.svg?event=push)](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml)

<h1 align="center">PPE Detection Application<br>for Construction Safety<br>in Raspberry Pi</h1>

## 📓 About
This is the official repository of our PPE detection application for construction which is part of the whole system in our capstone project. It analyzes the detected PPE from camera stream and evaluates the violations of each person. We also used an API that predicts their identities using [face_recognition](https://github.com/ageitgey/face_recognition). When obtaining the output from the detection, it will be wrapped up as a message to be published and sent as a payload which will then be received by multiple clients that are connected in the broker through lightweight messaging protocol called [MQTT](https://en.wikipedia.org/wiki/MQTT).

## 🤝 Team Members
- Zeus James Baltazar (Intelligent Systems) - Focuses mostly on utilization of ideas and their integration to the whole system.
- Martin Lorenzo Basbacio (Data Science) - Facilitates methods regarding detection and recognition.
- Clarece Gail Larrosa (Intelligent Systems) - Manages the document and provides assets to mobile application.
- Ian Gabriel Marquez (System Administration) - Handles mobile application development and its UI/UX design.

## ✔️ Features
- PPE detection for construction safety
- Human detection to determine worker violations
- Face recognition to predict the detected violator
- Mobile application reports and notifications

## ⚙️ Hardware
We used Rasperry Pi 4 Model B and OKdo Camera Module in this project. Additionally, we included some minor components to make the system more complete and at least somewhat helpful to the user, including RGB LED, piezo buzzer, and a tactile switch.

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

### Hardware Design
<p align="center">
  <img src="https://user-images.githubusercontent.com/39390245/221418865-82400ab6-caf6-484a-9d54-ca28c0866e41.png" width=640 height=480 alt="hardware-design-1">
  <br>
  <img src="https://user-images.githubusercontent.com/39390245/221419473-27658a5d-7759-404a-853e-e95269814909.png" width=640 height=480 alt="hardware-design-2">
  <br>
  <img src="https://user-images.githubusercontent.com/39390245/221419072-ac3a7018-7ec4-4521-84a1-b8b0446808b0.png" width=640 height=480 alt"hardware-design-3">
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

## 🚀 Installation
To get started, install the required dependencies. It is highly recommended to use virtual environment ([Pipenv](https://pypi.org/project/pipenv/), [Virtualenv](https://pypi.org/project/virtualenv/)) to isolate them to the system. 

There are some dependencies that are not included in the script. Download and install them first before continuing to the next step. 

After that, just run this script and it will handle the installation.
```
./scripts/linux/install.sh
```

Download and install mosquitto from https://mosquitto.org/download/. Make sure to run the broker as a service or as an independent program.

Set the target IP address of MQTT client to the broker's IP address by creating its configuration file in ```cfg/client``` folder.

## 🎦 Demonstration
We are currently doing some tests on various construction sites to determine the quality of the system and draw conclusions about the accomplished objectives, particularly the accuracy of detection. In the meantime, we are not going to be able to show you the demonstration.

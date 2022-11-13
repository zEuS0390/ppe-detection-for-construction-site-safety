[![](https://img.shields.io/badge/TIP-Quezon%20City-yellow)](https://tip.edu.ph/)
[![.github/workflows/app_server.yml](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml/badge.svg?event=push)](https://github.com/cpe-pd/rpi-camera/actions/workflows/app_server.yml)

<h1 align="center">PPE Detection Application for Construction Safety in Raspberry Pi</h1>
This is the official repository of our detection application, which is part of the whole system in our project design prototype. It analyzes the detected PPE from camera stream and evaluates the violations of each person. We used face recognition API to predict their identities, although there are some limitations. After obtaining the output, they will be published and sent as a payload which will then be received by multiple clients that are connected in the broker through lightweight messaging protocol called MQTT.

## Members
- Zeus James Baltazar (Intelligent Systems) - Focuses mostly on utilization of ideas and their integration to the whole system.
- Martin Lorenzo Basbacio (Data Science) - Facilitates methods regarding detection and recognition.
- Clarece Gail Larrosa (Intelligent Systems) - Manages prototype paper and provides assets for mobile application.
- Ian Gabriel Marquez (System Administration) - Handles mobile application development and its UI/UX design.

## Features
- PPE detection for construction safety
- Human detection to determine worker violations
- Face recognition to predict the detected violator
- Mobile application reports and notifications

## Hardware
| | Raspberry Pi |
| :-: | :-: |
| CPU | BCM2835 ARM Quad-Core 64-bit @ 1.8GHz |
| OS | Debian GNU/Linux 11 (bullseye) aarch64 |
| Memory | 8 GB |

| | OKdo Camera Module |
| :-: | :-: |
| Sensor | 5MP OV5647 |
| Resolution | 1080p |
| FPS | 30 |

## Classes
The trained model detects 5 basic PPE for construction with additional of 5 noncompliant cases and a person for determining violations.
- Helmet
- No helmet
- Glasses
- No glasses
- Vest
- No vest
- Gloves
- No gloves
- Boots
- No boots
- Person

## Installation
To get started, install the required dependencies. It is highly recommended to use virtual environment ([Pipenv](https://pypi.org/project/pipenv/), [Virtualenv](https://pypi.org/project/virtualenv/)) to isolate them to the system. 

There are some dependencies that are not included in the script. Download and install them first before continuing to the next step. 

After that, just run this script and it will handle the installation.
```
./scripts/linux/install.sh
```

Download and install mosquitto from https://mosquitto.org/download/. Make sure to run the broker as a service or as an independent program.

Set the target IP address of MQTT client to the broker's IP address by creating its configuration file in ```cfg/client``` folder.

## Demonstration
TBA

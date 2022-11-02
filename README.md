<h1 align="center"> Application Server with PPE Detection for Construction Safety in Raspberry Pi </h1>
This is the official repository of our application server, which is part of the whole system in our project design prototype. The server acts as the gateway for communication between the Raspberry Pi and mobile application. It provides information about the detected PPE worker violations and they could be obtained through lightweight messaging protocol called MQTT. 

## Members
- Zeus James Baltazar (Intelligent Systems) - Focuses mostly on utilization of ideas and their integration to the whole system.
- Martin Lorenzo Basbacio (Data Science) - Facilitates methods regarding detection, person tracking and recognition.
- Clarece Gail Larrosa (Intelligent Systems) - Manages prototype paper and provides assets for mobile application.
- Ian Gabriel Marquez (System Administration) - Handles mobile application development and its UI/UX design.

## Features
- PPE detection for construction safety
- Human detection to determine worker violations
- Face recognition to identify the detected violator
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
The trained model detects 5 basic PPE for construction with additional of 5 noncompliant cases.
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

## Installation
To get started, install the required dependencies. It is highly recommended to use virtual environment ([Pipenv](https://pypi.org/project/pipenv/), [Virtualenv](https://pypi.org/project/virtualenv/)) to isolate them to the system. 

Just run this script and it will handle the installation.
```
./scripts/linux/install.sh
```

Download and install mosquitto from https://mosquitto.org/download/. Make sure to run the broker as a service or as an independent program.

Set the IP address of MQTT clients to the broker's IP address by changing the app configuration file in ```cfg/config.ini```.

## Demonstration
TBA

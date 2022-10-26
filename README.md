<h1 align="center"> Application Server with PPE Detection for Construction Safety in Raspberry Pi </h1>
This is the official repository of our application server, which is part of the whole system in our project design prototype. The server acts as the gateway for communication between the Raspberry Pi and mobile application. It provides information about the detected PPE worker violations and they could be obtained through lightweight messaging protocol called MQTT. 

## Members
- Zeus James Baltazar (Intelligent Systems) - Focuses mostly on utilization of ideas and their integration to the whole system.
- Martin Lorenzo Basbacio (Data Science) - Facilitates methods regarding detection, person tracking and recognition.
- Clarece Gail Larrosa (Intelligent Systems) - Manages prototype paper and provides assets for mobile application.
- Ian Gabriel Marquez (System Administration) - Handles mobile application development and its UI/UX design.

## Hardware
| | Raspberry Pi |
| :-: | :-: |
| CPU | BCM2835 ARM Quad-Core 64-bit @ 1.8GHz |
| OS | Debian GNU/Linux 11 (bullseye) aarch64 |
| Memory | 8 GB |

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

## Trained Models
| version | weights |
| :-: | :-: |
| 1.0 | [trained_ppe_model_v1.pt](https://drive.google.com/file/d/1CW1DPajYIh-xkUhtGIJ0pkbyez_LC4z0/view?usp=sharing) |
| 2.0 | [trained_ppe_model_v2.pt](https://drive.google.com/file/d/14Q6iLv7_igK1761BUG3yBZ04N11YthVY/view?usp=sharing) |
| 2.1 | [trained_ppe_model_v2.1.pt](https://drive.google.com/file/d/1NS3boQlglUI2QaJV-mmzlZ0vLqsbIvxH/view?usp=sharing) |

## Installation
To get started, we need to install the required dependencies. It is highly recommended to use virtual environment ([Pipenv](https://pypi.org/project/pipenv/), [Virtualenv](https://pypi.org/project/virtualenv/)) to isolate them to the system. 

Just run this script and it will handle the installation of dependencies for you.
```
./scripts/linux/install.sh
```

After the installation, download the most recent trained model [here](#trained-models). Place it inside of the ```data/weights``` folder and name it as 'best_overall.pt'.

Set the IP address of MQTT clients to the broker's IP address by changing the app configuration file in ```cfg/config.ini```.

## Demonstration
TBA

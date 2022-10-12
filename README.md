# Web API Server with PPE Detection for Construction Safety in Raspberry Pi
This is the official repository of our web api server, whicih is part of the whole system in our prototype on project design. The server act as the gateway for communication between Raspberry Pi and mobile application. It provides information about the detected PPE worker violators and they could be requested by the mobile application through HTTP via RESTful API. 

## Members
- Zeus James Baltazar (Intelligent Systems)
- Martin Lorenzo Basbacio (Data Science)
- Clarece Gail Larrosa (Intelligent Systems)
- Ian Gabriel Marquez (System Administration)

## Raspberry Pi Information
- CPU: BCM2835 ARM Quad-Core 64-bit @ 1.8GHz<br>
- OS: Debian GNU/Linux 11 (bullseye) aarch64
- Memory: 8 GB<br>

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

Just run this script and it will handle all of them for you.
```
./scripts/linux/install.sh
```

## Demonstration
On going...

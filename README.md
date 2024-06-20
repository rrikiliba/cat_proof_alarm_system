# Cat Proof Alarm System - Embedded software for the internet of things

## Introduction

This project, developed by two students of the University of Trento, aims to create a comprehensive home security system.
The goal is to develop a system that enables users to utilize a motion-based security system within their homes, even in the presence of pets that might trigger the alarm. Our solution allows users to receive alerts upon motion detection, enabling them to view a captured image of the movement and decide whether to activate the alarm.

## Requirements
### Hardware
### Software

## Project layout
```
[cat_proof_alarm_system]
├── [esp_32]
│   ├── [firmware]
│   ├── [lib]
│   └── main.py
├── [orange_pi_zero_2w]
│   ├── app.py
│   ├── controller.py
│   ├── Dockerfile
│   ├── [images]
│   ├── [model]
│   │   └── yolov8n.pt
│   ├── [mosquitto]
│   └── [static]
│       ├── index.html
│       ├── script.js
│       └── style.css
├── [raspberry_pi_3_b]
│   └── [mosquitto]
└── [raspberry_pi_pico_w]
    ├── [firmware]
    ├── [lib]
    └── main.py
```
## How to run the project

Each of the three boards require a different setup in order to run the designated code

### Raspberry pi pico w

1. Connect the board via USB while holding the BOOTSEL button; your PC will recognize it as a generic mounted storage
1. Drag and drop the file provided in the [firmware folder](raspberry_pi_pico_w/firmware) inside the mounted storage
1. The device will reboot and you will successfully have flashed micropython
1. Using either the Thonny IDE or the rshell CLI as detailed in the [official documentation](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf), copy both `main.py` and the `lib` folder to the device
1. All set! now you can either simply power on the device and check output via serial communication, or execute it inside Thonny

### Esp32

1. Install [esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/installation.html), a CLI utility to flash the ESP family of boards, by following the provided instructions
1. Clear the flash by running the following:
	
	`esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash`
1. Flash the file provided in the [firmware folder](esp_32/firmware) by running the following:
	
	`esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 {path_to_firmware}`

1. Using either the Thonny IDE or the rshell CLI as above, copy both `main.py` and the `lib` folder to the device
1. All set! now you can either simply power on the device and check output via serial communication, or execute it inside Thonny

### Orange pi zero 2w

1. Download any compatible OS image. There exist an [Armbian](https://www.armbian.com/orange-pi-zero-2w/#) image, a [Dietpi](https://dietpi.com/#downloadinfo) image and a number of officially supported [images](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-Zero-2W.html) by the manufacturer itself. We used the official Debian Bookworm server [image](https://drive.google.com/drive/folders/1wjhR3YDvZzoBq7UiTYBgAUEWATIPNAjJ)
1. Flash the image to a TF / micro sd card using any of the many available flashing tools, such as [Balena Etcher](https://etcher.balena.io/)
1. Insert the flashed card into the device, power it on and either connect mouse, keyboard and monitor to it, or ssh to it
1. Make sure both [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/engine/install/) are installed. If not, follow the instructions to install them to the orange pi zero 2w
1. Clone this repo from the device itself via `git clone`
1. Place yourself inside the `orange_pi_zero_2w` folder and run

	`docker compose up`

1. Now the system is up and running!  

## User guide

## Links

1. [powerpoint]()
1. [presentation video]()

## Team members' contributions

Riccardo Libanora:

- Raspberry pi pico w code development
- Esp32 code development
- Orange pi zero 2w code development
- Mqtt broker and topics, network setup
- "How to run the project" section of documentation

Davide Zanolini: 

- Webapp graphic interface
- Webapp interface to mqtt via websockets 
- Documentation
- Presentation
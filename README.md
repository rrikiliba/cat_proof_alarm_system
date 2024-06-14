# Cat Proof Alarm System - Embedded software for the internet of things

### Developed by:

- Riccardo Libanora 
- Davide Zanolini

This project, developed by three students of the University of Trento, aims to create a comprehensive home security system. 
The goal is to develop a system that enables users to utilize a motion-based security system within their homes, even in the presence of pets that might trigger the alarm. Our solution allows users to receive alerts upon motion detection, enabling them to view a captured image of the movement and decide whether to activate the alarm

## Installation

Follow these steps to install the Cat Proof Alarm System:

1. **Hardware Setup**: 
2. **Software Setup**:
3. **Configuration**:
4. **Running the System**:

## Key Features:

- Motion Detector: monitors the environment for any movement. When it detects motion, it triggers the system to capture an image of the area and send an alert to the user
- Camera: it captures an image of the area where the motion was detected
- Alarm: activates when the system catches an intruder 
- Ai model: detects the presence of friendly pets that might inadvertently trigger the alarm inside the image, defusing the alarm 
- User Interface: provides the user with alerts when motion is detected, displays the captured image for user verification, and allows the user to activate or deactivate the alarm
- MQTT Broker: it facilitates the exchange of messages between the different components of the system

## Implementation

### Raspberry Pi Pico W

The Raspberry Pi Pico W board manages communication with a movement sensor that triggers the alarm, as well as a RFID sensor to defuse it.
Upon triggering, whether from motion detection or NFC interaction, the Raspberry Pi Pico W sends a message through the MQTT broker to inform other devices or systems of the event.

### ESP32-CAM

Upon receiving the trigger message, the ESP32-CAM activates its camera to take a snapshot. This photo is then transmitted back through the MQTT broker, making it accessible to other devices or systems connected to the network.

### Orange Pi Zero 2w

The Orange Pi Zero 2W runs a pre-trained YOLO model to examine the pictures taken when the alarm is triggered.
To manage communication within the IoT network, the Orange Pi Zero 2W hosts a webserver as well as both a MQTT client and the Mosquitto MQTT broker.
The board also manages General Purpose Input/Output (GPIO) pins using Python.

## How the system works
- When the ESP32-CAM captures a photo and sends it via MQTT, the Orange Pi Zero 2W receives this image. 
- It then processes the picture and disarms the system if a cat is detected, then also displays the photo on a web application
- This web app can be accessed remotely, allowing users to monitor and review images captured by the system from any location with internet access.
- The board also implements a countdown mechanism. Once triggered, it starts a countdown timer. If the system does not receive a disarm message within the      specified timeframe, it activates an alarm. 
- To prevent the alarm from triggering unnecessarily, the system listens for a disarm message. If this message is received before the countdown completes, it cancels the alarm.

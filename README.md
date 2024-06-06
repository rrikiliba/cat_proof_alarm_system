# Cat Proof Alarm System - Embedded software for the internet of things

### Developed by:

- Riccardo
- Marco
- Davide Zanolini

This project, developed by three students of the University of Trento, aims to create a comprehensive home security system. 
The goal is to develop a system that enables users to utilize a motion-based security system within their homes, even in the presence of pets that might trigger the alarm. Our solution allows users to receive alerts upon motion detection, enabling them to view a captured image of the movement and decide whether to activate the alarm

## Key Features:

- Motion Detector: monitors the environment for any movement. When it detects motion, it triggers the system to capture an image of the area and send an alert to the user
- Camera: it captures an image of the area where the motion was detected
- Alarm: activates when the system catches an intruder 
- User Interface: provides the user with alerts when motion is detected, displays the captured image for user verification, and allows the user to activate or deactivate the alarm
- MQTT Broker: it facilitates the exchange of messages between the different components of the system

## Implementation

### Raspberry Pi Pico W

The Raspberry Pi Pico W board serves as the central unit for interfacing with both a motion sensor and an NFC reader. This board has been programmed using MicroPython, a lightweight and efficient Python implementation designed for microcontrollers.
When either the motion sensor detects movement or the NFC reader scans a tag, the Raspberry Pi Pico W captures these events. To communicate these events, the board leverages an MQTT broker.
Upon triggering, whether from motion detection or NFC interaction, the Raspberry Pi Pico W sends a message through the MQTT broker to inform other devices or systems of the event.

### ESP32-CAM

Upon receiving the trigger message, the ESP32-CAM activates its camera to take a snapshot. This photo is then transmitted back through the MQTT broker, making it accessible to other devices or systems connected to the network. This seamless process allows the ESP32-CAM to function as a remote, automated imaging solution.

### Raspberry Orange Pi Zero 2w

The Orange Pi Zero 2W runs a Python implementation of YOLO, a state-of-the-art real-time object detection system. YOLO is renowned for its speed and accuracy, enabling the board to analyze incoming images swiftly and identify objects or threats in real-time.
To manage communication within the IoT network, the Orange Pi Zero 2W includes an MQTT client developed in Node.js. This client handles messages sent and received via the MQTT protocol.The board also manages General Purpose Input/Output (GPIO) pins using Python.
An MQTT broker running over WebSocket is another critical component hosted on the Orange Pi Zero 2W. This broker serves as the central hub for message distribution within the network. Using WebSocket provides a bidirectional communication channel over a single, long-lived connection, ensuring efficient and real-time message delivery between devices.
When the ESP32-CAM captures a photo and sends it via the MQTT broker, the Orange Pi Zero 2W receives this image. It then processes and displays the photo on a web application, providing users with real-time visual feedback. This web app can be accessed remotely, allowing users to monitor and review images captured by the system from any location with internet access.
The board also implements a countdown mechanism. Once triggered, it starts a countdown timer. If the system does not receive a disarm message within the specified timeframe, it activates an alarm. 
To prevent the alarm from triggering unnecessarily, the system listens for a disarm message. If this message is received before the countdown completes, it cancels the alarm.

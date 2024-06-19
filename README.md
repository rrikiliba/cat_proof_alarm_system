# Cat Proof Alarm System - Embedded software for the internet of things

### Introduction

This project, developed by two students of the University of Trento, aims to create a comprehensive home security system.
The goal is to develop a system that enables users to utilize a motion-based security system within their homes, even in the presence of pets that might trigger the alarm. Our solution allows users to receive alerts upon motion detection, enabling them to view a captured image of the movement and decide whether to activate the alarm.

## Requirements

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
## How to buid and run the project

## User guide

# Links

# Team members

- Riccardo Libanora: developed the code to operate the boards
- Davide Zanolini: developed the code to enable communication between the different boards and the web page, create the documentation
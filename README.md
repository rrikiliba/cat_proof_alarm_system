# Cat Proof Alarm System - Embedded software for the internet of things

### Introduction

This project, developed by two students of the University of Trento, aims to create a comprehensive home security system.
The goal is to develop a system that enables users to utilize a motion-based security system within their homes, even in the presence of pets that might trigger the alarm. Our solution allows users to receive alerts upon motion detection, enabling them to view a captured image of the movement and decide whether to activate the alarm.

## Requirements

## Project layout
[cat_proof_alarm_system]
├── [.git] (...)
├── .gitignore
├── [esp_32]
│   ├── [firmware]
│   │   └── micropython_camera_feeeb5ea3_esp32_idf4_4.bin
│   ├── [lib]
│   │   └── [umqtt]
│   │       └── simple.py
│   └── main.py
├── generate_secrets.sh
├── [orange_pi_zero_2w]
│   ├── .authfile
│   ├── .env
│   ├── app.py
│   ├── controller.py
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   ├── [images]
│   ├── [model]
│   │   └── yolov8n.pt
│   ├── [mosquitto]
│   │   ├── [data]
│   │   ├── [etc]
│   │   ├── [log]
│   │   └── [mosquitto.conf]
│   ├── requirements.txt
│   └── [static]
│       ├── index.html
│       ├── script.js
│       └── style.css
├── [raspberry_pi_3_b]
│   └── [mosquitto]
│       ├── [mosquitto.conf]
│       ├── [mosquitto_data]
│       │   └── mosquitto.db
│       ├── [mosquitto_etc]
│       └── [mosquitto_log]
└── [raspberry_pi_pico_w]
    ├── [firmware]
    │   └── RPI_PICO_W-20240222-v1.22.2.uf2
    ├── [lib]
    │   ├── mfrc522.py
    │   └── [umqtt]
    │       └── simple.py
    └── main.py

## How to buid and run the project

## User guide

# Links

# Team members

- Riccardo Libanora: developed the code to operate the boards
- Davide Zanolini: developed the code to enable communication between the different boards and the web page, create the documentation
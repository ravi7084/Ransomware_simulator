# Ransomware_simulator
✅ Project Introduction

Ransomware Simulator is a safe, controlled, and educational environment designed to demonstrate how ransomware behaves without harming real files.
This project showcases the full lifecycle of a ransomware-like event, including file encryption simulation, detection, alerts, recovery, and log tracking.
The simulator helps students and security learners understand core ransomware mechanisms without any real destructive impact.
All operations are performed only on isolated test data, ensuring a completely safe environment.

✅ Features Summary

Simulated file encryption using a reversible XOR-based algorithm.
Real-time ransomware detection powered by behavior monitoring.
Automatic backup and restore flow for quick recovery.
Interactive frontend dashboard built with HTML, CSS, and JavaScript.
Modular backend architecture implemented in Python (Flask).
Popup-style alerts to show how real ransomware notifies users.
Detailed activity logs for analysis and visualization.

✅ Architecture Description

The backend is fully modular with separate files for detection, encryption simulation, backup, restore, popup handling, and utilities.
The frontend communicates with the backend using REST APIs to start simulations, fetch logs, and trigger recovery actions.
Test data is isolated and copied into a working directory before simulation to ensure real data is never modified.
The frontend communicates with the backend using REST APIs to start simulations, fetch logs, and trigger recovery actions.

Test data is isolated and copied into a working directory before simulation to ensure real data is never modified.

# Tutorial: Big_defend_IA

BigDefend AI is a **fraud detection system** designed to analyze transactions using AI.
It features a **frontend dashboard** for different user roles (admin, analyst, client) to monitor transactions and fraud alerts in **real-time**.
A **backend API** handles data processing, communication with the **database**, runs the **AI fraud detection models**, and manages user access and alerts.
Data is handled carefully, using mock data for development and real data from a database in production, with a **logging system** to track events.


## Visual Overview

```mermaid
flowchart TD
    A0["Frontend Application Structure
"]
    A1["Authentication System
"]
    A2["Backend API (Communication Hub)
"]
    A3["Data Handling and Access
"]
    A4["Fraud Detection Core (AI Engine)
"]
    A5["Real-time Data Flow (WebSockets)
"]
    A6["Database Management
"]
    A7["User and Role Management
"]
    A8["Logging System
"]
    A9["Alert Management
"]
    A0 -- "Communicates with" --> A2
    A1 -- "Manages user access for" --> A0
    A0 -- "Adapts UI based on" --> A7
    A5 -- "Pushes updates to" --> A0
    A2 -- "Requests data from" --> A3
    A3 -- "Accesses data via" --> A6
    A2 -- "Sends transactions to" --> A4
    A4 -- "Triggers alerts in" --> A9
    A2 -- "Sends real-time data via" --> A5
    A2 -- "Records events in" --> A8
    A9 -- "Stores alerts in" --> A6
    A1 -- "Uses backend for" --> A2
    A7 -- "Defines permissions in" --> A2
```

## Chapters

1. [Backend API (Communication Hub)
](01_backend_api__communication_hub__.md)
2. [Authentication System
](02_authentication_system_.md)
3. [User and Role Management
](03_user_and_role_management_.md)
4. [Frontend Application Structure
](04_frontend_application_structure_.md)
5. [Fraud Detection Core (AI Engine)
](05_fraud_detection_core__ai_engine__.md)
6. [Alert Management
](06_alert_management_.md)
7. [Data Handling and Access
](07_data_handling_and_access_.md)
8. [Database Management
](08_database_management_.md)
9. [Real-time Data Flow (WebSockets)
](09_real_time_data_flow__websockets__.md)
10. [Logging System
](10_logging_system_.md)
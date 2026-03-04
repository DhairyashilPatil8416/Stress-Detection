# StressSense API - Backend

This is the backend API for the StressSense stress detection system. It provides role-based access to stress data, with separate views for managers and employees.

## Features

- Secure authentication with JWT tokens
- Role-based access control (Manager, Employee)
- Device-based stress submission with API keys
- Stress analytics for managers
- Personal stress data view for employees
- Commands queue for device control
- MongoDB data storage

## System Architecture

### Simple Architecture Overview
![Simple Architecture](../frontend/public/Simpl-arch.png)

### Detailed System Architecture
![System Architecture](../frontend/public/System-arch.svg)

## Prerequisites

- Python 3.8+
- MongoDB installed and running
- Python virtual environment (recommended)

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the backend directory with the following variables:

```
# MongoDB Configuration
MONGO_URI=mongodb://127.0.0.1:27017/
DB_NAME=stress_sense_db

# JWT Configuration
JWT_SECRET=create_a_very_secure_jwt_secret_key_for_production
JWT_EXPIRES_MINUTES=60

# Security Settings
PASSWORD_HASH_SCHEME=bcrypt
DEVICE_KEY_PEPPER=add_a_strong_device_key_pepper_for_production

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=DEBUG

# App Settings
API_V1_PREFIX=/api/v1
```

## Database Setup

1. Make sure MongoDB is running
2. Seed the database with initial data:

```bash
python seed_data.py
```

This will create:
- A manager account (username: `admin`, password: `adminpassword`)
- 5 employee accounts with corresponding user accounts
- 1 device per employee
- Sample stress records for the past 14 days

## Running the API

Start the API server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Endpoints

The API is structured with the following main endpoint groups:

- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/admin/*` - Administrator functions (manager only)
- `/api/v1/stress/*` - Stress data submission
- `/api/v1/device/*` - Device command endpoints
- `/api/v1/manager/*` - Manager analytics and dashboards
- `/api/v1/me/*` - Employee self-view
- `/api/v1/utils/*` - Utility endpoints

## Default Accounts

After running `seed_data.py`, you can use these accounts:

- Manager: username=`admin`, password=`adminpassword`
- Employees: username=`<first part of email>`, password=`password123`

Example: `john` with password `password123`

**IMPORTANT:** For production, change these default passwords!

## Device API Keys

Device API keys are generated when a device is created. The key is only shown once, so make sure to store it securely.

## Security Considerations

- Always use HTTPS in production
- Change the JWT_SECRET and DEVICE_KEY_PEPPER to strong random values
- Update all default passwords before going to production
- Consider setting up more restrictive CORS policies in production

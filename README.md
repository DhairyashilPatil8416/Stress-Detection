# StressSense - Real-Time Stress Detection System 


StressSense is a comprehensive stress detection and management platform that uses facial expression analysis to predict stress levels in real-time. It includes a web application interface and a background Windows agent for continuous monitoring.

## Components

### 1. Web Application
A responsive web interface for on-demand stress detection and management.

### 2. Backend API
A secure FastAPI backend with MongoDB integration, authentication, and analytics.

### 3. Windows Background Agent
A silent background application for Windows that periodically captures and analyzes stress levels.

## System Architecture

### Simple Architecture Overview
![Simple Architecture](frontend/public/Simpl-arch.png)

### Detailed System Architecture
![System Architecture](frontend/public/System-arch.svg)

## Features

- Real-time facial expression analysis
- Stress level classification (Low, Medium, High)
- Personalized stress management suggestions
- Clean and intuitive user interface
- Webcam integration
- Responsive design
- Secure API with role-based authentication
- Background monitoring with Windows agent
- Historical stress analytics

## Tech Stack

### Backend
- FastAPI
- MongoDB
- OpenCV
- DeepFace
- TensorFlow
- Python 3.8+
- JWT Authentication

### Frontend
- React.js
- React Webcam
- Axios
- TailwindCSS

### Windows Agent
- Python with PyWin32
- OpenCV
- DeepFace
- Windows DPAPI for secure credential storage
- Executable packaging with PyInstaller

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd backend
uvicorn app:app --reload
```

The backend server will run on `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

### Windows Agent Setup

1. Install dependencies:
```bash
cd windows_agent
pip install -r requirements.txt
```

2. Configure the agent:
```bash
python -m windows_agent --configure
```

3. Register the device:
```bash
python -m windows_agent --register EMPLOYEE_ID
```

4. Run the agent:
```bash
python -m windows_agent --run
```

Alternatively, use the provided setup.bat script for guided installation:
```bash
cd windows_agent
setup.bat
```

## Usage

### Web Application
1. Open the application in your web browser
2. Click "Start Stress Scan" to begin
3. Allow camera access when prompted
4. Click "Capture & Analyze" to analyze your current stress level
5. View your stress level and personalized suggestions
6. Click "Stop Scan" to end the session

### Windows Agent
The Windows agent runs silently in the background and can be:
- Configured to run at startup
- Installed as a Windows service
- Controlled through commands from the backend

## API Endpoints

- Authentication: `/api/v1/auth/login`, `/api/v1/auth/register`
- Users: `/api/v1/users/*`
- Devices: `/api/v1/devices/*`
- Stress: `/api/v1/stress/record`, `/api/v1/stress/analyze`
- Analytics: `/api/v1/analytics/*`

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

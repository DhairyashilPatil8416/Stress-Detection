# StressSense+ Windows Agent

This is a Windows desktop application for employee stress level detection. The application provides a user-friendly interface for device registration, service management, and stress monitoring.

## Features

- **Desktop GUI Application**: Tkinter-based interface with terms and conditions
- **User Authentication**: Login system for managers and employees
- **Device Registration**: Secure device registration with unique identification
- **Service Management**: Install, start, stop, and uninstall Windows service
- **Background Monitoring**: Automatic stress detection every 30 minutes
- **Local Processing**: AI analysis performed locally (no images sent to server)
- **Professional Installer**: NSIS-based Windows installer package (~420 MB)
- **Optimized Size**: Reduced from 1.2 GB to 420 MB through dependency exclusion and build optimization

## System Architecture

### Simple Architecture Overview
![Simple Architecture](../frontend/public/Simpl-arch.png)

### Detailed System Architecture
![System Architecture](../frontend/public/System-arch.svg)

## Installation

### Option 1: Using the Installer (Recommended)

1. Download `StressSense+_Installer.exe` (420 MB)
2. Run the installer with administrator privileges
3. Follow the installation wizard
4. Launch StressSense+ from the desktop shortcut

### Option 2: Manual Installation

1. **Clone or download** this project

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python stress_app.py
   ```

## Usage

### First Time Setup

1. **Accept Terms**: Read and accept the terms and conditions
2. **Login**: Enter your manager/employee credentials
3. **Register Device**: Provide employee ID and device name
4. **Install Service**: Install the background monitoring service

### Daily Operation

- The service runs automatically in the background
- Captures webcam images every 30 minutes
- Analyzes stress levels locally using AI
- Sends only stress data to the backend server

### Service Management

Use the GUI to:
- **Start/Stop Service**: Control the background monitoring
- **Test Detection**: Manually test stress detection
- **Re-register Device**: Change device association
- **Uninstall Service**: Remove the background service

## Building from Source

### Prerequisites
- Python 3.8+ with all dependencies installed
- PyInstaller: `pip install pyinstaller`
- NSIS (Nullsoft Scriptable Install System): Download from https://nsis.sourceforge.io/

### Build Process

1. **Build the executables:**
   ```bash
   build_exe.bat
   ```
   This creates:
   - `StressSense+.exe` - Main client application
   - `StressDetectionService.exe` - Background service
   - `install_service.exe` - Service installer utility

2. **Build the installer:**
   ```bash
   build_installer.bat
   ```
   This creates `StressSense+_Installer.exe`

### What the Production Installer Does

The professional installer provides:

- **Terms and Conditions**: Displays license agreement
- **Installation Path Selection**: Choose where to install
- **Progress Display**: Shows installation progress
- **Automatic Service Installation**: Installs and starts the background service
- **Desktop Shortcuts**: Creates shortcuts for easy access
- **Uninstaller**: Adds entry to Windows Add/Remove Programs

## Size Optimization

The installer size has been significantly reduced through several optimizations:

- **Dependency Exclusion**: Removed unnecessary ML libraries (matplotlib, scipy, sklearn, pandas) from client
- **Build Mode**: Changed from single-file (--onefile) to directory-based (--onedir) builds for better compression
- **Selective Bundling**: Service includes only required ML dependencies (TensorFlow, OpenCV, NumPy)

**Size Results:**
- Original installer: ~1.2 GB
- Optimized installer: ~420 MB (65% reduction)
- Client application: ~56 MB
- Service application: ~368 MB

## Production Usage

After installation:
1. Users run `StressSense+.exe` from desktop/start menu
2. First run: Device registration with employee ID
3. Service automatically starts and runs in background
4. No manual service management needed

## Configuration

Create a `.env` file in the windows directory (copy from the provided `.env` template) and update values for your environment:

- **Backend URL**: Configure `BACKEND_URL` (default: `http://localhost:8000`)
- **API Prefix**: Configure `API_PREFIX` (default: `/api/v1`)
- **Capture Interval**: Configure `CAPTURE_INTERVAL_MINUTES` (default: 30 minutes)
- **Auto Analysis Interval**: Configure `AUTO_ANALYSIS_INTERVAL_SECONDS` (default: 120 seconds, set to 0 to disable)
- **Service Check Interval**: Configure `SERVICE_CHECK_INTERVAL_SECONDS` (default: 60 seconds)
- **Request Timeout**: Configure `REQUEST_TIMEOUT_SECONDS` (default: 10 seconds)
- **Retry Settings**: Configure `MAX_CAPTURE_ATTEMPTS`, `CAPTURE_RETRY_DELAY_SECONDS`, `MAX_RETRY_ATTEMPTS`, `RETRY_DELAY_SECONDS`
- **Emotion Thresholds**: Configure individual emotion confidence thresholds (e.g., `EMOTION_SAD_MIN_CONFIDENCE`)

Example `.env` file:
```
BACKEND_URL=https://your-hosted-backend.com
API_PREFIX=/api/v1
CONFIG_FILE=device_config.json
CAPTURE_INTERVAL_MINUTES=30
AUTO_ANALYSIS_INTERVAL_SECONDS=120
REQUEST_TIMEOUT_SECONDS=10
MAX_CAPTURE_ATTEMPTS=3
EMOTION_SAD_MIN_CONFIDENCE=30
```

## System Requirements

- Windows 10/11
- Python 3.8+ (for development)
- Webcam
- Internet connection
- Administrator privileges for service installation

## Security & Privacy

- **No Image Transmission**: Images are processed locally and never sent to servers
- **Device Uniqueness**: Each device is uniquely registered to prevent data mixing
- **Local AI Processing**: Stress analysis uses TensorFlow locally
- **Secure Authentication**: API keys for backend communication
- **Data Minimization**: Only essential stress data is transmitted

## Troubleshooting

### Application Won't Start
- Ensure all dependencies are installed
- Check Python version (3.8+ required)
- Verify webcam permissions

### Service Installation Fails
- Run installer as administrator
- Check Windows Services for existing service
- Ensure no antivirus blocking installation

### Stress Detection Not Working
- Verify webcam is connected and functional
- Check lighting conditions
- Ensure face is clearly visible
- Test with "Test Detection" button

### Backend Connection Issues
- Verify backend server is running
- Check network connectivity
- Confirm backend URL configuration

## Uninstallation

### Using Installer
- Run the installer again and select "Remove"

### Manual Uninstallation
1. Stop the service: `python start_service.py stop`
2. Uninstall service: `python install_service.py uninstall`
3. Delete the installation folder

## Technical Details

- **GUI Framework**: Tkinter (built-in Python)
- **AI Model**: TensorFlow CNN for emotion recognition
- **Service Framework**: pywin32 Windows service
- **Bundling**: PyInstaller for executable creation
- **Installation**: NSIS for Windows installer

## Model Compatibility

**Important**: The included `stress_cnn_model.h5` was trained with an older version of TensorFlow/Keras. If loading fails due to compatibility issues, the application will automatically use a fallback model that provides basic functionality.

To use a properly trained model:
1. Retrain the model using TensorFlow 2.13.0+
2. Ensure the model uses compatible layer configurations
3. Replace the `stress_cnn_model.h5` file

The fallback model ensures the application doesn't crash and provides basic emotion detection capabilities.

## License

This software is licensed under the terms specified in `license.txt`.

## Support

For technical support, contact your IT department or system administrator.

## Usage

Once installed and started, the service will:

1. Run in the background automatically
2. Capture webcam images at set intervals
3. Analyze facial expressions for stress levels
4. Send stress data to the backend server
5. Display results in the manager dashboard

## Troubleshooting

### Service won't start
- Ensure device is registered (run `register_device.py`)
- Check Windows Services for "Stress Detection Service"
- Check event logs for error messages

### Analysis fails
- Ensure webcam is available and not used by other applications
- Check lighting conditions
- Ensure face is clearly visible in frame

### Backend connection fails
- Verify backend server is running
- Check network connectivity
- Verify backend URL configuration

## Uninstallation

1. Stop the service:
   ```bash
   python start_service.py stop
   ```

2. Uninstall the service:
   ```bash
   python install_service.py uninstall
   ```

3. Delete the folder if desired

## Security Notes

- No images are transmitted to the backend server
- Only processed stress data and metadata are sent
- Each device is uniquely authenticated
- API keys are stored locally and encrypted
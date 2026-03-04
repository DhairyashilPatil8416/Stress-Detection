import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import cv2
import json
import os
import sys
import requests
from datetime import datetime, timedelta
import threading
import schedule
from stress_analysis import analyze_image
import base64
from dotenv import load_dotenv

# Load environment variables
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle - try executable dir first, then source dir
    dotenv_paths = [
        os.path.join(os.path.dirname(sys.executable), '.env'),
        os.path.join(os.path.dirname(__file__), '.env')
    ]
    for path in dotenv_paths:
        if os.path.exists(path):
            load_dotenv(path)
            break
else:
    # Running in development
    load_dotenv()

# Create logs directory
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configuration - Read from environment variables
CONFIG_FILE = os.getenv("CONFIG_FILE", "device_config.json")
BACKEND_URL = os.getenv("BACKEND_URL")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

if not BACKEND_URL:
    raise ValueError("BACKEND_URL environment variable is required")
CAPTURE_INTERVAL_SECONDS = int(os.getenv("CAPTURE_INTERVAL_SECONDS", "10"))

class StressDetectionService(win32serviceutil.ServiceFramework):
    _svc_name_ = "StressDetectionService"
    _svc_display_name_ = "Stress Detection Service"
    _svc_description_ = "Background service for stress level detection"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._get_logger()
        self.stop_event = threading.Event()
        self.scheduler_thread = None

    def _get_logger(self):
        logger = logging.getLogger('[StressDetectionService]')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # File handler
            log_file = os.path.join(log_dir, 'stress_detection_service.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            
            # Error file handler
            error_log_file = os.path.join(log_dir, 'stress_detection_service_errors.log')
            error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
            error_file_handler.setFormatter(formatter)
            error_file_handler.setLevel(logging.ERROR)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            logger.addHandler(error_file_handler)
        return logger

    def SvcStop(self):
        self.logger.info('Stopping service...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_event.set()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        self.logger.info('Service started')
        self.main()

    def load_config(self):
        """Load device configuration"""
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        return None

    def capture_and_analyze(self):
        """Capture image from webcam and analyze stress"""
        try:
            self.logger.info("Starting stress detection cycle")

            # Load configuration
            config = self.load_config()
            if not config:
                self.logger.error("No device configuration found. Please run register_device.py first.")
                return

            # Capture image from webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.logger.error("Could not open webcam")
                return

            ret, frame = cap.read()
            cap.release()

            if not ret:
                self.logger.error("Failed to capture image from webcam")
                return

            # Convert to base64 for analysis
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # Analyze the image
            result = analyze_image(img_base64)

            if "error" in result:
                self.logger.warning(f"Analysis failed: {result['error']}")
                return

            self.logger.info(f"Analysis successful: {result['emotion']} -> {result['stress_level']}")

            # Prepare data for backend
            stress_data = {
                "device_id": config["device_id"],
                "employee_id": config["employee_id"],
                "emotion": result["emotion"],
                "stress_level": result["stress_level"],
                "confidence": result["confidence"],
                "timestamp": datetime.now().isoformat(),
                "face_quality": result.get("face_quality")
            }

            # Send to backend
            self.send_to_backend(stress_data, config["api_key"])

        except Exception as e:
            self.logger.error(f"Error in capture_and_analyze: {e}")

    def send_to_backend(self, data, api_key):
        """Send stress data to backend"""
        try:
            url = f"{BACKEND_URL}{API_PREFIX}/stress/record"
            headers = {
                "X-Device-Key": api_key,
                "Content-Type": "application/json"
            }

            self.logger.info(f"Sending stress data to backend: {data}")
            self.logger.info(f"Backend URL: {url}")
            self.logger.info(f"Headers: {headers}")

            timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
            response = requests.post(url, json=data, headers=headers, timeout=timeout_seconds)

            self.logger.info(f"Response status: {response.status_code}")
            self.logger.info(f"Response text: {response.text}")

            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Successfully sent stress data. Record ID: {result.get('record_id')}")
            else:
                self.logger.error(f"Failed to send data: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error sending data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in send_to_backend: {e}")

    def scheduler_worker(self):
        """Worker thread for scheduled tasks"""
        # Schedule the capture function
        schedule.every(CAPTURE_INTERVAL_SECONDS).seconds.do(self.capture_and_analyze)

        # Run initial capture
        self.capture_and_analyze()

        while not self.stop_event.is_set():
            schedule.run_pending()
            check_interval = int(os.getenv("SERVICE_CHECK_INTERVAL_SECONDS", "60"))
            time.sleep(check_interval)  # Configurable check interval

    def main(self):
        """Main service loop"""
        try:
            # Check if device is registered
            config = self.load_config()
            if not config:
                self.logger.error("Device not registered. Please run register_device.py first.")
                return

            self.logger.info(f"Service running for device: {config['device_id']}, employee: {config['employee_id']}")
            self.logger.info(f"Capture interval: {CAPTURE_INTERVAL_SECONDS} seconds")

            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self.scheduler_worker)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()

            # Wait for stop event
            while not self.stop_event.is_set():
                time.sleep(1)

            # Wait for scheduler thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)

        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Check for debug mode
        if os.getenv('SERVICE_DEBUG', '').lower() in ('1', 'true', 'yes'):
            # Run in debug mode - execute service logic directly
            print("Running StressDetectionService in DEBUG mode...")
            # Create a mock service instance for testing
            class MockStressDetectionService:
                def __init__(self):
                    self.logger = self.setup_logging()
                    self.stop_event = threading.Event()
                    self._svc_name_ = "StressDetectionService"

                def setup_logging(self):
                    return self._setup_logging_static()

                @staticmethod
                def _setup_logging_static():
                    logger = logging.getLogger('StressDetectionService')
                    logger.setLevel(logging.INFO)

                    # Create logs directory
                    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
                    os.makedirs(log_dir, exist_ok=True)

                    # Console handler
                    console_handler = logging.StreamHandler(sys.stdout)
                    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                    console_handler.setFormatter(formatter)

                    # File handler
                    log_file = os.path.join(log_dir, 'stress_detection_service.log')
                    file_handler = logging.FileHandler(log_file, encoding='utf-8')
                    file_handler.setFormatter(formatter)

                    # Error file handler
                    error_log_file = os.path.join(log_dir, 'stress_detection_service_errors.log')
                    error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
                    error_file_handler.setFormatter(formatter)
                    error_file_handler.setLevel(logging.ERROR)

                    logger.addHandler(console_handler)
                    logger.addHandler(file_handler)
                    logger.addHandler(error_file_handler)
                    return logger

                def load_config(self):
                    """Load device configuration"""
                    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, 'r') as f:
                                return json.load(f)
                        except Exception as e:
                            self.logger.error(f"Error loading config: {e}")
                    return None

                def capture_and_analyze(self):
                    """Capture image from webcam and analyze stress"""
                    try:
                        self.logger.info("Starting stress detection cycle")

                        # Load configuration
                        config = self.load_config()
                        if not config:
                            self.logger.error("No device configuration found. Please run register_device.py first.")
                            return

                        # Capture image from webcam
                        cap = cv2.VideoCapture(0)
                        if not cap.isOpened():
                            self.logger.error("Could not open webcam")
                            return

                        ret, frame = cap.read()
                        cap.release()

                        if not ret:
                            self.logger.error("Failed to capture image from webcam")
                            return

                        # Convert to base64 for analysis
                        _, buffer = cv2.imencode('.jpg', frame)
                        img_base64 = base64.b64encode(buffer).decode('utf-8')

                        # Analyze the image
                        result = analyze_image(img_base64)

                        if "error" in result:
                            self.logger.warning(f"Analysis failed: {result['error']}")
                            return

                        self.logger.info(f"Analysis successful: {result['emotion']} -> {result['stress_level']}")

                        # Prepare data for backend
                        stress_data = {
                            "device_id": config["device_id"],
                            "employee_id": config["employee_id"],
                            "emotion": result["emotion"],
                            "stress_level": result["stress_level"],
                            "confidence": result["confidence"],
                            "timestamp": datetime.now().isoformat(),
                            "face_quality": result.get("face_quality")
                        }

                        # Send to backend
                        self.send_to_backend(stress_data, config["api_key"])

                    except Exception as e:
                        self.logger.error(f"Error in capture_and_analyze: {e}")

                def send_to_backend(self, data, api_key):
                    """Send stress data to backend"""
                    try:
                        url = f"{BACKEND_URL}{API_PREFIX}/stress/record"
                        headers = {
                            "X-Device-Key": api_key,
                            "Content-Type": "application/json"
                        }

                        self.logger.info(f"Sending stress data to backend: {data}")
                        self.logger.info(f"Backend URL: {url}")
                        self.logger.info(f"Headers: {headers}")

                        timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
                        response = requests.post(url, json=data, headers=headers, timeout=timeout_seconds)

                        self.logger.info(f"Response status: {response.status_code}")
                        self.logger.info(f"Response text: {response.text}")

                        if response.status_code == 200:
                            result = response.json()
                            self.logger.info(f"Successfully sent stress data. Record ID: {result.get('record_id')}")
                        else:
                            self.logger.error(f"Failed to send data: {response.status_code} - {response.text}")

                    except requests.exceptions.RequestException as e:
                        self.logger.error(f"Network error sending data: {e}")
                    except Exception as e:
                        self.logger.error(f"Unexpected error in send_to_backend: {e}")

                def scheduler_worker(self):
                    """Worker thread for scheduled tasks"""
                    # Schedule the capture function
                    schedule.every(CAPTURE_INTERVAL_SECONDS).seconds.do(self.capture_and_analyze)

                    # Run initial capture
                    self.capture_and_analyze()

                    while not self.stop_event.is_set():
                        schedule.run_pending()
                        check_interval = int(os.getenv("SERVICE_CHECK_INTERVAL_SECONDS", "60"))
                        time.sleep(check_interval)  # Configurable check interval

                def main(self):
                    """Main service loop"""
                    try:
                        # Check if device is registered
                        config = self.load_config()
                        if not config:
                            self.logger.error("Device not registered. Please run register_device.py first.")
                            return

                        self.logger.info(f"Service running for device: {config['device_id']}, employee: {config['employee_id']}")
                        self.logger.info(f"Capture interval: {CAPTURE_INTERVAL_SECONDS} seconds")

                        # Start scheduler thread
                        self.scheduler_thread = threading.Thread(target=self.scheduler_worker)
                        self.scheduler_thread.daemon = True
                        self.scheduler_thread.start()

                        # Wait for stop event
                        while not self.stop_event.is_set():
                            time.sleep(1)

                        # Wait for scheduler thread to finish
                        if self.scheduler_thread and self.scheduler_thread.is_alive():
                            self.scheduler_thread.join(timeout=5)

                    except Exception as e:
                        self.logger.error(f"Error in main loop: {e}")

            service = MockStressDetectionService()
            try:
                service.main()
            except KeyboardInterrupt:
                print("Debug mode interrupted by user")
                service.stop_event.set()
            except Exception as e:
                print(f"Debug mode error: {e}")
                service.logger.error(f"Debug mode error: {e}")
        else:
            # Normal service mode
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(StressDetectionService)
            servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(StressDetectionService)
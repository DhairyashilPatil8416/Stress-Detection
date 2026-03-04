import win32serviceutil
import win32service
import sys
import os
import subprocess

def install_service():
    """Install the Windows service"""
    try:
        # Get the full path to the service executable
        service_exe = os.path.join(os.path.dirname(__file__), 'StressDetectionService.exe')

        # Check if executable exists
        if not os.path.exists(service_exe):
            print(f"Service executable not found: {service_exe}")
            print("Please build the executable first using: pyinstaller StressDetectionService.spec")
            return False

        # Install the service using sc command (more reliable than win32serviceutil)
        result = subprocess.run([
            'sc', 'create', 'StressDetectionService',
            'binPath=', f'"{service_exe}"',
            'start=', 'auto',
            'DisplayName=', 'StressSense Stress Detection Service'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error installing service: {result.stderr}")
            return False

        print("Service installed successfully!")
        print("Starting service...")

        # Start the service
        result = subprocess.run(['sc', 'start', 'StressDetectionService'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Warning: Could not start service: {result.stderr}")
            print("You can start it manually from Windows Services")
        else:
            print("Service started successfully!")

        return True

    except Exception as e:
        print(f"Error installing service: {e}")
        return False

def uninstall_service():
    """Uninstall the Windows service"""
    try:
        # Stop the service first
        subprocess.run(['sc', 'stop', 'StressDetectionService'],
                     capture_output=True, timeout=10)

        # Delete the service
        result = subprocess.run(['sc', 'delete', 'StressDetectionService'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error uninstalling service: {result.stderr}")
            return False

        print("Service uninstalled successfully!")
        return True

    except Exception as e:
        print(f"Error uninstalling service: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'uninstall':
            return uninstall_service()
        elif command == 'install':
            return install_service()
        else:
            print("Usage: python install_service.py [install|uninstall]")
            return False
    else:
        # Default action is install
        return install_service()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
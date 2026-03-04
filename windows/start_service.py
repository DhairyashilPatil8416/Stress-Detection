import win32serviceutil
import sys

def start_service():
    """Start the Windows service"""
    try:
        win32serviceutil.StartService('StressDetectionService')
        print("Service started successfully!")
    except Exception as e:
        print(f"Error starting service: {e}")
        return False
    return True

def stop_service():
    """Stop the Windows service"""
    try:
        win32serviceutil.StopService('StressDetectionService')
        print("Service stopped successfully!")
    except Exception as e:
        print(f"Error stopping service: {e}")
        return False
    return True

def restart_service():
    """Restart the Windows service"""
    try:
        win32serviceutil.RestartService('StressDetectionService')
        print("Service restarted successfully!")
    except Exception as e:
        print(f"Error restarting service: {e}")
        return False
    return True

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'stop':
            return stop_service()
        elif command == 'restart':
            return restart_service()
        elif command == 'start':
            return start_service()
        else:
            print("Usage: python start_service.py [start|stop|restart]")
            return False
    else:
        # Default to start
        return start_service()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
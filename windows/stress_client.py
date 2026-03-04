#!/usr/bin/env python3
"""
StressSense Production Client
A simplified client for production use that handles device registration and service management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import os
import sys
import subprocess
import threading
from datetime import datetime
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

class StressSenseClient:
    def __init__(self, root):
        self.root = root
        self.root.title("StressSense+ - Employee Stress Detection")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Load configuration
        self.backend_url = os.getenv("BACKEND_URL")
        self.api_prefix = os.getenv("API_PREFIX", "/api/v1")

        if not self.backend_url:
            raise ValueError("BACKEND_URL environment variable is required")
        self.config_file = os.getenv("CONFIG_FILE", "device_config.json")

        # Load existing config
        self.config = self.load_config()

        self.setup_ui()

    def load_config(self):
        """Load device configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_config(self, config):
        """Save device configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def setup_ui(self):
        """Setup the main UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="StressSense+",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 20))

        if self.config:
            ttk.Label(status_frame, text=f"Device: {self.config['device_id'][:16]}...",
                      font=("Arial", 10)).pack(anchor=tk.W)
            ttk.Label(status_frame, text=f"Employee: {self.config['employee_id']}",
                      font=("Arial", 10)).pack(anchor=tk.W)

            # Service status
            self.status_label = ttk.Label(status_frame, text="Checking service status...",
                                         font=("Arial", 10, "italic"))
            self.status_label.pack(anchor=tk.W, pady=(10, 0))

            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(0, 20))

            ttk.Button(button_frame, text="Test Detection",
                      command=self.test_detection).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="View Logs",
                      command=self.view_logs).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Re-register Device",
                      command=self.re_register).pack(side=tk.LEFT)

        else:
            ttk.Label(status_frame, text="Device not registered",
                     font=("Arial", 10)).pack(anchor=tk.W)

            # Registration frame
            reg_frame = ttk.LabelFrame(main_frame, text="Device Registration", padding="10")
            reg_frame.pack(fill=tk.X, pady=(20, 0))

            # Employee ID
            ttk.Label(reg_frame, text="Employee ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.employee_var = tk.StringVar()
            employee_entry = ttk.Entry(reg_frame, textvariable=self.employee_var, width=30)
            employee_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

            # Device Name
            ttk.Label(reg_frame, text="Device Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.device_var = tk.StringVar(value="Workstation")
            device_entry = ttk.Entry(reg_frame, textvariable=self.device_var, width=30)
            device_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

            # Register button
            ttk.Button(reg_frame, text="Register Device",
                      command=self.register_device).grid(row=2, column=0, columnspan=2, pady=(20, 0))

        # Check service status if registered
        if self.config:
            self.check_service_status()

    def register_device(self):
        """Register device with backend"""
        employee_id = self.employee_var.get().strip()
        device_name = self.device_var.get().strip()

        if not employee_id or not device_name:
            messagebox.showerror("Error", "Please enter both Employee ID and Device Name")
            return

        # Show progress
        progress = ttk.Progressbar(self.root, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=(0, 20))
        progress.start()

        def register():
            try:
                url = f"{self.backend_url}{self.api_prefix}/devices/register"
                data = {
                    "employee_id": employee_id,
                    "device_name": device_name,
                    "device_type": "windows_agent"
                }

                response = requests.post(url, json=data, timeout=30)
                response.raise_for_status()

                result = response.json()

                # Save configuration
                config = {
                    "device_id": result['device_id'],
                    "api_key": result['api_key'],
                    "employee_id": employee_id,
                    "device_name": device_name,
                    "registered_at": datetime.now().isoformat()
                }
                self.save_config(config)
                self.config = config

                # Install and start service
                self.install_and_start_service()

                self.root.after(0, lambda: self.on_registration_success())

            except Exception as e:
                self.root.after(0, lambda: self.on_registration_error(str(e)))
            finally:
                self.root.after(0, progress.destroy)

        threading.Thread(target=register, daemon=True).start()

    def install_and_start_service(self):
        """Install and start the Windows service"""
        try:
            # Install service
            result = subprocess.run([sys.executable, "install_service.py", "install"],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise Exception(f"Service installation failed: {result.stderr}")

            # Start service
            result = subprocess.run([sys.executable, "start_service.py"],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise Exception(f"Service start failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Service setup failed: {str(e)}")

    def on_registration_success(self):
        """Handle successful registration"""
        messagebox.showinfo("Success",
                          "Device registered successfully!\n\n"
                          "The stress detection service has been installed and started.\n"
                          "It will run automatically in the background.")

        # Restart the application to show registered state
        self.root.destroy()
        main()

    def on_registration_error(self, error):
        """Handle registration error"""
        messagebox.showerror("Registration Failed", f"Error: {error}")

    def check_service_status(self):
        """Check if the service is running"""
        try:
            result = subprocess.run(['sc', 'query', 'StressDetectionService'],
                                  capture_output=True, text=True, timeout=10)

            if "RUNNING" in result.stdout:
                self.status_label.config(text="Service: Running", foreground="green")
            elif "STOPPED" in result.stdout:
                self.status_label.config(text="Service: Stopped", foreground="red")
                # Try to start it
                self.start_service()
            else:
                self.status_label.config(text="Service: Unknown status", foreground="orange")

        except Exception as e:
            self.status_label.config(text=f"Service: Error checking status", foreground="red")

    def start_service(self):
        """Start the service"""
        try:
            subprocess.run(['sc', 'start', 'StressDetectionService'],
                         capture_output=True, timeout=10)
            self.status_label.config(text="Service: Starting...", foreground="orange")
            # Check status again after a delay
            self.root.after(3000, self.check_service_status)
        except:
            pass

    def test_detection(self):
        """Run a test detection"""
        messagebox.showinfo("Test Detection",
                          "Test detection would run here.\n\n"
                          "In production, this would capture an image and analyze stress levels.")

    def view_logs(self):
        """View service logs"""
        messagebox.showinfo("Logs",
                          "Log viewing would be implemented here.\n\n"
                          "In production, this would show recent service activity.")

    def re_register(self):
        """Re-register device"""
        if messagebox.askyesno("Re-register",
                              "This will remove the current registration and allow you to register again.\n\n"
                              "The service will be stopped. Continue?"):
            try:
                # Stop and uninstall service
                subprocess.run([sys.executable, "install_service.py", "uninstall"],
                             capture_output=True, timeout=30)

                # Remove config file
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)

                # Restart app
                self.root.destroy()
                main()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to re-register: {str(e)}")


def main():
    root = tk.Tk()
    app = StressSenseClient(root)
    root.mainloop()


if __name__ == "__main__":
    main()
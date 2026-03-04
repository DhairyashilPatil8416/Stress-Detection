import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import subprocess
import threading
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import time
from win10toast import ToastNotifier

# Initialize notification toaster
toaster = ToastNotifier()

def is_office_hours():
    """Check if current time is within office hours (9 AM to 6 PM)"""
    now = datetime.now()
    current_hour = now.hour
    return 9 <= current_hour < 18  # 9 AM to 6 PM

def show_stress_notification():
    """Show Windows notification for high stress"""
    toaster.show_toast(
        "Stress Detection Alert",
        "High stress detected! Take a break and relax.",
        duration=10,
        threaded=True
    )

# Check office hours on startup
if not is_office_hours():
    messagebox.showwarning("Office Hours Only", "This application only runs during office hours (9 AM to 6 PM).")
    sys.exit(0)
try:
    from stress_analysis import analyze_image, analyze_image_array, EMOTION_STRESS_MAP
except ImportError:
    # Handle case where module not available (for development)
    analyze_image = None
    analyze_image_array = None
    EMOTION_STRESS_MAP = {}

# Configure logging
import os
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create formatters
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File handler for all logs
all_logs_file = os.path.join(log_dir, 'stress_app.log')
file_handler = logging.FileHandler(all_logs_file, encoding='utf-8')
file_handler.setFormatter(formatter)

# File handler for errors only
error_logs_file = os.path.join(log_dir, 'stress_app_errors.log')
error_file_handler = logging.FileHandler(error_logs_file, encoding='utf-8')
error_file_handler.setFormatter(formatter)
error_file_handler.setLevel(logging.ERROR)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler, error_file_handler]
)
logger = logging.getLogger(__name__)

# Import emotion stress mapping - lazy load to speed up startup
EMOTION_STRESS_MAP = None

def get_emotion_stress_map():
    """Lazy load emotion stress mapping to speed up app startup"""
    global EMOTION_STRESS_MAP
    if EMOTION_STRESS_MAP is None:
        # Use the already imported EMOTION_STRESS_MAP if available
        if EMOTION_STRESS_MAP is not None:
            return EMOTION_STRESS_MAP
        # Fallback mapping if import fails - now configurable via environment variables
        EMOTION_STRESS_MAP = {
            "happy": {"level": "Low", "min_confidence": int(os.getenv("EMOTION_HAPPY_MIN_CONFIDENCE", "20"))},
            "neutral": {"level": "Low", "min_confidence": int(os.getenv("EMOTION_NEUTRAL_MIN_CONFIDENCE", "25"))},
            "sad": {"level": "Medium", "min_confidence": int(os.getenv("EMOTION_SAD_MIN_CONFIDENCE", "30"))},
            "angry": {"level": "Medium", "min_confidence": int(os.getenv("EMOTION_ANGRY_MIN_CONFIDENCE", "30"))},
            "fear": {"level": "High", "min_confidence": int(os.getenv("EMOTION_FEAR_MIN_CONFIDENCE", "35"))},
                "disgust": {"level": "High", "min_confidence": int(os.getenv("EMOTION_DISGUST_MIN_CONFIDENCE", "35"))},
                "surprise": {"level": "Medium", "min_confidence": int(os.getenv("EMOTION_SURPRISE_MIN_CONFIDENCE", "30"))}
            }
    return EMOTION_STRESS_MAP

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

class StressDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StressSense - Employee Wellness Portal")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)

        # Modern styling
        self.setup_styles()

        # Configuration
        self.config_file = os.getenv("CONFIG_FILE", "device_config.json")
        self.backend_url = os.getenv("BACKEND_URL")
        self.api_prefix = os.getenv("API_PREFIX", "/api/v1")

        if not self.backend_url:
            raise ValueError("BACKEND_URL environment variable is required")

        # Session file - handle bundled environment
        if getattr(sys, '_MEIPASS', None):
            # In bundled app, save session in executable directory
            self.session_file = os.path.join(os.path.dirname(sys.executable), 'user_session.json')
        else:
            # Development mode - save in script directory
            self.session_file = os.path.join(os.path.dirname(__file__), 'user_session.json')

        # Try to load existing session
        self.load_session()

        # Initialize attributes that might not be set by load_session
        if not hasattr(self, 'access_token'):
            self.access_token = None
        if not hasattr(self, 'current_user'):
            self.current_user = None

        # Check if we have a valid session
        self.has_valid_session = self.current_user is not None and self.access_token is not None

        # Auto analysis timer
        self.auto_timer = None

        # Create main container with modern layout
        self.main_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Initialize UI based on session status
        if self.has_valid_session:
            logger.info("Valid session found, going directly to main menu")
            self.show_main_menu()
        else:
            logger.info("No valid session, showing terms and conditions")
            self.show_terms_conditions()

    def setup_styles(self):
        """Setup monochrome black & white styling"""
        style = ttk.Style()

        # Monochrome color scheme: black text on white background
        self.colors = {
            'primary': '#000000',
            'primary_dark': '#000000',
            'primary_light': '#000000',
            'secondary': '#000000',
            'success': '#000000',
            'warning': '#000000',
            'error': '#000000',
            'background': '#ffffff',
            'surface': '#ffffff',
            'text': '#000000',
            'text_secondary': '#000000',
            'border': '#000000',
            'border_focus': '#000000'
        }

        # Main frame style
        style.configure("Main.TFrame", background=self.colors['background'])

        # Card style for sections
        style.configure("Card.TFrame",
                       background=self.colors['surface'],
                       relief="raised",
                       borderwidth=1)

        # Title labels
        style.configure("Title.TLabel",
                       font=("Segoe UI", 24, "bold"),
                       foreground=self.colors['text'],
                       background=self.colors['background'])

        style.configure("Subtitle.TLabel",
                       font=("Segoe UI", 14),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['background'])

        # Form labels
        style.configure("Form.TLabel",
                       font=("Segoe UI", 11),
                       foreground=self.colors['text'],
                       background=self.colors['surface'])

        # Buttons: monochrome style
        style.configure("TButton",
                       font=("Segoe UI", 11),
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       padding=(10, 5),
                       borderwidth=1)
        style.map("TButton",
                  relief=[('pressed', 'sunken')],
                  background=[('active', self.colors['surface'])])

        # Entry fields
        style.configure("Modern.TEntry",
                       font=("Segoe UI", 11),
                       padding=(10, 8),
                       relief="flat",
                       borderwidth=2)

        # Labelframes
        style.configure("Card.TLabelframe",
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=("Segoe UI", 12, "bold"),
                       borderwidth=1,
                       relief="solid")

        style.configure("Card.TLabelframe.Label",
                       background=self.colors['surface'],
                       foreground=self.colors['primary'],
                       font=("Segoe UI", 12, "bold"))

        # Status labels
        style.configure("Status.TLabel",
                       font=("Segoe UI", 10),
                       background=self.colors['background'])

        # Configure button hover effects
        style.map("Primary.TButton",
                 background=[('active', self.colors['primary_dark'])],
                 relief=[('pressed', 'sunken')])
        # Add visible border for better contrast
        style.configure("Primary.TButton", borderwidth=2)

        style.map("Secondary.TButton",
                 background=[('active', '#475569')],
                 relief=[('pressed', 'sunken')])
        style.configure("Secondary.TButton", borderwidth=2)

        style.map("Success.TButton",
                 background=[('active', '#047857')],
                 relief=[('pressed', 'sunken')])
        style.configure("Success.TButton", borderwidth=2)

        # Configure entry focus
        style.map("Modern.TEntry",
                 bordercolor=[('focus', self.colors['border_focus'])])

    def create_scrollable_frame(self, parent, height=None):
        """Create a scrollable frame for content that might exceed window height"""
        # Create a canvas with professional styling and smooth scrolling
        canvas = tk.Canvas(parent, background=self.colors['surface'], highlightthickness=0)
        canvas.configure(bd=0, relief='ridge')  # Remove border
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)

        # Create the scrollable frame
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure grid for better expansion and scrolling
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure canvas expansion
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return scrollable_frame

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_terms_conditions(self):
        """Show terms and conditions screen"""
        self.clear_frame()

        # Header section
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(20, 15))
        header_frame.columnconfigure(0, weight=1)

        # Logo/Title area
        title_label = ttk.Label(header_frame, text="🧠 StressSense",
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(header_frame, text="Employee Wellness Monitoring System",
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0)

        # Main content card (centered like login)
        content_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding="40")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=60, pady=(0, 30))
        content_frame.columnconfigure(0, weight=1)

        # Terms title
        terms_title = ttk.Label(content_frame, text="📋 Terms and Conditions",
                               font=("Segoe UI", 16, "bold"),
                               foreground=self.colors['text'],
                               background=self.colors['surface'])
        terms_title.grid(row=0, column=0, pady=(10, 15))

        # Terms text in a modern scrolled frame
        terms_frame = ttk.Frame(content_frame, style="Card.TFrame")
        terms_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        terms_frame.columnconfigure(0, weight=1)

        terms_text = scrolledtext.ScrolledText(
            terms_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            background=self.colors['surface'],
            foreground=self.colors['text'],
            borderwidth=0,
            padx=10,
            pady=10,
            height=12  # Limit height to make it scrollable
        )
        terms_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        terms_content = """
STRESSSENSE EMPLOYEE STRESS DETECTION SYSTEM

TERMS AND CONDITIONS

1. PURPOSE
This application monitors employee stress levels through facial expression analysis to promote workplace wellness.

2. DATA COLLECTION
- Facial images are captured locally on your device
- Images are processed locally and immediately deleted
- Only stress analysis results are transmitted to the server
- No images or videos are stored or transmitted

3. PRIVACY PROTECTION
- All processing occurs on your local device
- Stress data is anonymized and aggregated
- Data is retained for 12 months and then anonymized
- You can request data deletion at any time

4. DEVICE REGISTRATION
- Each device must be registered to a specific employee
- Registration prevents data mixing between employees
- You can unregister your device at any time

5. SYSTEM REQUIREMENTS
- Windows 10/11 operating system
- Webcam access required
- Internet connection for data transmission
- Background service operation

6. USER RESPONSIBILITIES
- Ensure proper lighting for accurate detection
- Position yourself appropriately in camera view
- Keep webcam clean and functional
- Report any technical issues promptly

7. LIMITATIONS
- System provides stress level estimates only
- Not a substitute for professional medical advice
- Results may vary based on lighting and positioning
- System requires clear facial visibility

8. DATA USAGE
- Stress data helps management identify wellness trends
- Individual data remains confidential
- Aggregated data may be used for workplace improvements

9. TECHNICAL SUPPORT
- Contact your IT department for technical issues
- Service can be paused or uninstalled at any time

10. AGREEMENT
By accepting these terms, you agree to participate in workplace stress monitoring for wellness purposes.

Last updated: September 2025
        """

        terms_text.insert(tk.END, terms_content.strip())
        terms_text.config(state=tk.DISABLED)

        # Acceptance section
        accept_frame = ttk.Frame(content_frame, style="Card.TFrame")
        accept_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 10))

        # Checkbox with better styling
        self.accept_var = tk.BooleanVar()
        accept_check = ttk.Checkbutton(
            accept_frame,
            text="I have read and agree to the terms and conditions",
            variable=self.accept_var,
            style="TCheckbutton"
        )
        accept_check.grid(row=0, column=0, pady=10, padx=20)

        # Buttons
        button_frame = ttk.Frame(content_frame, style="Card.TFrame")
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(20, 20))

        accept_btn = ttk.Button(
            button_frame,
            text="Accept and Continue",
            style="TButton",
            command=self.on_terms_accepted
        )
        accept_btn.grid(row=0, column=0, padx=(0, 15))

        decline_btn = ttk.Button(
            button_frame,
            text="Decline and Exit",
            style="TButton",
            command=self.on_terms_declined
        )
        decline_btn.grid(row=0, column=1)

    def on_terms_accepted(self):
        """Handle terms acceptance"""
        if not self.accept_var.get():
            messagebox.showerror("Error", "Please accept the terms and conditions to continue.")
            return

        # Check if device is already registered
        config = self.load_config()
        if config and config.get('device_id') and config.get('api_key'):
            # Device already registered, go to login
            self.show_login()
        else:
            # New installation, start with user registration
            self.show_user_registration()

    def on_terms_declined(self):
        """Handle terms decline"""
        if messagebox.askyesno("Confirm", "Are you sure you want to exit?"):
            self.root.quit()

    def show_login(self):
        """Show login screen"""
        self.clear_frame()
        # Load existing configuration to control registration option
        config = self.load_config()

        # Header section
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(30, 20))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="Welcome Back",
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(header_frame, text="Sign in to your StressSense account",
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0)

        # Main content card
        content_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding="40")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=60, pady=(0, 30))
        content_frame.columnconfigure(0, weight=1)

        # Login form section
        form_frame = ttk.Frame(content_frame, style="Card.TFrame")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        form_frame.columnconfigure(1, weight=1)

        # Username field
        username_label = ttk.Label(form_frame, text="Username", style="Form.TLabel")
        username_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, style="Modern.TEntry")
        username_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Password field
        password_label = ttk.Label(form_frame, text="Password", style="Form.TLabel")
        password_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        # Password entry with toggle button
        password_frame = ttk.Frame(form_frame, style="Card.TFrame")
        password_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 30))
        password_frame.columnconfigure(0, weight=1)

        self.password_var = tk.StringVar()
        self.password_show = False
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var,
                                 show="*", style="Modern.TEntry")
        password_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Password toggle button
        def toggle_password():
            self.password_show = not self.password_show
            password_entry.config(show="" if self.password_show else "*")
            toggle_btn.config(text="🙈" if self.password_show else "👁️")

        toggle_btn = ttk.Button(password_frame, text="👁️", width=3,
                              command=toggle_password, style="TButton")
        toggle_btn.grid(row=0, column=1, padx=(5, 0))

        # Buttons section
        button_frame = ttk.Frame(content_frame, style="Card.TFrame")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        login_btn = ttk.Button(
            button_frame,
            text="Sign In",
            command=self.do_login
        )
        login_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Secondary actions
        actions_frame = ttk.Frame(content_frame, style="Card.TFrame")
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 0))

        # Only show registration option if no existing configuration
        if not config:
            register_btn = ttk.Button(
                actions_frame,
                text="Register",
                command=self.show_user_registration
            )
            register_btn.grid(row=0, column=0, pady=(0, 10))

        back_btn = ttk.Button(
            actions_frame,
            text="Back",
            command=self.show_terms_conditions
        )
        back_btn.grid(row=1, column=0)

        # Status label
        self.login_status_var = tk.StringVar()
        status_label = ttk.Label(
            content_frame,
            textvariable=self.login_status_var,
            style="Status.TLabel",
            foreground=self.colors['error']
        )
        status_label.grid(row=3, column=0, pady=(20, 0))

    def do_login(self):
        """Perform login"""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.login_status_var.set("Please enter both username and password.")
            return

        # Perform login request
        try:
            url = f"{self.backend_url}{self.api_prefix}/auth/login"
            data = {"username": username, "password": password}

            logger.info(f"[LOGIN] Sending login data: {data}")
            logger.info(f"[LOGIN] URL: {url}")

            response = requests.post(url, data=data)
            
            logger.info(f"[LOGIN] Response status: {response.status_code}")
            logger.info(f"[LOGIN] Response text: {response.text}")
            
            response.raise_for_status()

            result = response.json()
            logger.info(f"[LOGIN] Login successful for user: {username}")
            
            self.current_user = result
            self.access_token = result.get("access_token")  # Store the access token

            # Save session for persistence
            self.save_session(self.current_user, self.access_token)

            # On login success, navigate to main menu
            logger.info("[LOGIN] Login successful, navigating to main menu")
            self.login_status_var.set("Login successful!")

            self.root.after(500, self.show_main_menu)

        except requests.exceptions.RequestException as e:
            logger.error(f"[LOGIN] Login failed: {str(e)}")
            self.login_status_var.set(f"Login failed: {str(e)}")
        except Exception as e:
            logger.error(f"[LOGIN] Error: {str(e)}")
            self.login_status_var.set(f"Error: {str(e)}")

    def show_user_registration(self):
        """Show user registration screen"""
        self.clear_frame()

        # Header section
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(20, 15))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="📝 Create Account",
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(header_frame, text="Join StressSense for employee wellness monitoring",
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0)

        # Create main container for full screen layout
        container_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        container_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container_frame.columnconfigure(0, weight=1)
        container_frame.rowconfigure(0, weight=1)

        # Main content card
        content_frame = ttk.Frame(container_frame, style="Card.TFrame", padding="40")
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=60, pady=(0, 30))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Create scrollable content area that fills the frame
        scrollable_content = self.create_scrollable_frame(content_frame)
        scrollable_content.columnconfigure(0, weight=2)  # Device info column
        scrollable_content.columnconfigure(1, weight=3)  # Form column (wider)
        scrollable_content.rowconfigure(0, weight=1)     # Allow vertical expansion

        # Get device info
        device_info = self.get_device_info()

        # Left column - Device Information
        device_frame = ttk.LabelFrame(scrollable_content, text="🖥️ Device Information", style="Card.TLabelframe", padding="25")
        device_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 20), pady=10)
        device_frame.columnconfigure(0, weight=1)  # Allow horizontal expansion

        device_info_text = f"Device Number: {device_info.get('device_number', 'Unknown')}\n"
        device_info_text += f"OS: {device_info.get('os', 'Unknown')}\n"
        device_info_text += f"OS Version: {device_info.get('os_version', 'Unknown')}\n"
        device_info_text += f"Architecture: {device_info.get('architecture', 'Unknown')}\n"
        device_info_text += f"Hostname: {device_info.get('hostname', 'Unknown')}\n"
        device_info_text += f"MAC Address: {device_info.get('mac_address', 'Unknown')}"

        device_info_label = ttk.Label(device_frame, text=device_info_text,
                                     font=("Segoe UI", 9),
                                     foreground=self.colors['text_secondary'],
                                     background=self.colors['surface'],
                                     justify=tk.LEFT)
        device_info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Right column - Registration Form
        form_container = ttk.Frame(scrollable_content, style="Card.TFrame")
        form_container.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(20, 0), pady=10)
        form_container.columnconfigure(0, weight=1)

        # Registration form with professional layout
        # Account Information Section
        account_frame = ttk.LabelFrame(form_container, text="🔐 Account Information", style="Card.TLabelframe", padding="20")
        account_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        account_frame.columnconfigure(0, weight=1)
        account_frame.columnconfigure(1, weight=0)

        # Username field
        username_label = ttk.Label(account_frame, text="👤 Username", style="Form.TLabel")
        username_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_username_var = tk.StringVar()
        username_entry = ttk.Entry(account_frame, textvariable=self.reg_username_var, style="Modern.TEntry")
        username_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Password fields
        password_label = ttk.Label(account_frame, text="🔒 Password", style="Form.TLabel")
        password_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        # Password entry with toggle button
        password_frame = ttk.Frame(account_frame, style="Card.TFrame")
        password_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        password_frame.columnconfigure(0, weight=1)

        self.reg_password_var = tk.StringVar()
        self.reg_password_show = False
        password_entry = ttk.Entry(password_frame, textvariable=self.reg_password_var,
                                 show="*", style="Modern.TEntry")
        password_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Password toggle button
        def toggle_reg_password():
            self.reg_password_show = not self.reg_password_show
            password_entry.config(show="" if self.reg_password_show else "*")
            reg_toggle_btn.config(text="🙈" if self.reg_password_show else "👁️")

        reg_toggle_btn = ttk.Button(password_frame, text="👁️", width=3,
                                  command=toggle_reg_password, style="TButton")
        reg_toggle_btn.grid(row=0, column=1, padx=(5, 0))

        confirm_label = ttk.Label(account_frame, text="🔒 Confirm Password", style="Form.TLabel")
        confirm_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 8))

        # Confirm password entry with toggle button
        confirm_frame = ttk.Frame(account_frame, style="Card.TFrame")
        confirm_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        confirm_frame.columnconfigure(0, weight=1)

        self.reg_confirm_password_var = tk.StringVar()
        self.reg_confirm_show = False
        confirm_entry = ttk.Entry(confirm_frame, textvariable=self.reg_confirm_password_var,
                                show="*", style="Modern.TEntry")
        confirm_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Confirm password toggle button
        def toggle_confirm_password():
            self.reg_confirm_show = not self.reg_confirm_show
            confirm_entry.config(show="" if self.reg_confirm_show else "*")
            confirm_toggle_btn.config(text="🙈" if self.reg_confirm_show else "👁️")

        confirm_toggle_btn = ttk.Button(confirm_frame, text="👁️", width=3,
                                      command=toggle_confirm_password, style="TButton")
        confirm_toggle_btn.grid(row=0, column=1, padx=(5, 0))

        # Personal Information Section
        personal_frame = ttk.LabelFrame(form_container, text="👤 Personal Information", style="Card.TLabelframe", padding="20")
        personal_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        personal_frame.columnconfigure(0, weight=1)
        personal_frame.columnconfigure(1, weight=0)

        # Full Name field
        fullname_label = ttk.Label(personal_frame, text="👨‍💼 Full Name", style="Form.TLabel")
        fullname_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_fullname_var = tk.StringVar()
        fullname_entry = ttk.Entry(personal_frame, textvariable=self.reg_fullname_var, style="Modern.TEntry")
        fullname_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Email field
        email_label = ttk.Label(personal_frame, text="📧 Email Address", style="Form.TLabel")
        email_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_email_var = tk.StringVar()
        email_entry = ttk.Entry(personal_frame, textvariable=self.reg_email_var, style="Modern.TEntry")
        email_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Employee ID field
        employee_label = ttk.Label(personal_frame, text="🆔 Employee ID", style="Form.TLabel")
        employee_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_employee_id_var = tk.StringVar()
        employee_entry = ttk.Entry(personal_frame, textvariable=self.reg_employee_id_var, style="Modern.TEntry")
        employee_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Department field
        department_label = ttk.Label(personal_frame, text="🏢 Department", style="Form.TLabel")
        department_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_department_var = tk.StringVar()
        department_entry = ttk.Entry(personal_frame, textvariable=self.reg_department_var, style="Modern.TEntry")
        department_entry.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Buttons section
        button_frame = ttk.Frame(form_container, style="Card.TFrame")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        button_frame.columnconfigure(0, weight=1)

        register_btn = ttk.Button(
            button_frame,
            text="✅ Create Account",
            style="Success.TButton",
            command=self.do_user_registration
        )
        register_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        login_btn = ttk.Button(
            button_frame,
            text="🔐 Already have an account? Sign In",
            style="TButton",
            command=self.show_login
        )
        login_btn.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Status label
        self.reg_status_var = tk.StringVar()
        status_label = ttk.Label(
            form_container,
            textvariable=self.reg_status_var,
            style="Status.TLabel",
            foreground=self.colors['error']
        )
        status_label.grid(row=3, column=0, pady=(10, 20))

    def do_user_registration(self):
        """Perform user registration"""
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get()
        confirm_password = self.reg_confirm_password_var.get()
        fullname = self.reg_fullname_var.get().strip()
        email = self.reg_email_var.get().strip()
        employee_id = self.reg_employee_id_var.get().strip()
        department = self.reg_department_var.get().strip()

        # Validation
        if not all([username, password, confirm_password, fullname, email, employee_id]):
            self.reg_status_var.set("Please fill in all fields.")
            return

        if password != confirm_password:
            self.reg_status_var.set("Passwords do not match.")
            return

        if len(password) < 6:
            self.reg_status_var.set("Password must be at least 6 characters long.")
            return

        # Perform registration request
        try:
            url = f"{self.backend_url}{self.api_prefix}/auth/register"
            data = {
                "username": username,
                "password": password,
                "full_name": fullname,
                "email": email,
                "employee_id": employee_id,
                "department": department or "General",  # Default to General if empty
                "role": "employee"
            }

            logger.info(f"[USER REGISTRATION] Sending registration data: {data}")
            logger.info(f"[USER REGISTRATION] URL: {url}")

            response = requests.post(url, json=data)
            
            logger.info(f"[USER REGISTRATION] Response status: {response.status_code}")
            logger.info(f"[USER REGISTRATION] Response text: {response.text}")
            
            response.raise_for_status()

            result = response.json()
            self.current_user = result

            # Now register the device automatically
            logger.info("[USER REGISTRATION] User registered successfully, now registering device...")
            
            # Get device info
            device_info = self.get_device_info()
            
            # Register device
            device_url = f"{self.backend_url}{self.api_prefix}/devices/register"
            device_data = {
                "employee_id": employee_id,
                "device_name": f"{fullname}'s Device",
                "device_number": device_info.get('device_number', ''),
                "device_type": "windows_agent",
                "device_info": {
                    "os": device_info.get('os', 'Unknown'),
                    "os_version": device_info.get('os_version', 'Unknown'),
                    "architecture": device_info.get('architecture', 'Unknown'),
                    "hostname": device_info.get('hostname', 'Unknown'),
                    "mac_address": device_info.get('mac_address', 'Unknown')
                }
            }

            # For device registration, we need authentication, but since we just registered the user,
            # we need to login first to get the token
            login_url = f"{self.backend_url}{self.api_prefix}/auth/login"
            login_data = {"username": username, "password": password}
            
            login_response = requests.post(login_url, data=login_data)
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.access_token = login_result.get("access_token")
                self.current_user = login_result
                
                # Now register device with authentication
                headers = {"Authorization": f"Bearer {self.access_token}"}
                device_response = requests.post(device_url, json=device_data, headers=headers)
                
                if device_response.status_code == 201:
                    device_result = device_response.json()
                    logger.info(f"[DEVICE REGISTRATION] Device registered successfully: {device_result}")
                    
                    # Save configuration
                    config = {
                        "device_id": device_result['device_id'],
                        "api_key": device_result['api_key'],
                        "employee_id": employee_id,
                        "device_name": device_data['device_name'],
                        "device_number": device_data['device_number'],
                        "username": username,
                        "user_id": self.current_user.get('user_id'),
                        "role": "employee",
                        "registered_at": datetime.now().isoformat(),
                        "backend_url": self.backend_url
                    }
                    self.save_config(config)
                    
                    self.reg_status_var.set("Registration complete! Welcome to StressSense.")
                    self.root.after(1000, self.show_main_menu)
                else:
                    logger.error(f"[DEVICE REGISTRATION] Failed: {device_response.text}")
                    self.reg_status_var.set("User registered but device registration failed. Please contact support.")
            else:
                logger.error(f"[LOGIN] Auto-login failed: {login_response.text}")
                self.reg_status_var.set("User registered but login failed. Please login manually.")

        except requests.exceptions.RequestException as e:
            self.reg_status_var.set(f"Registration failed: {str(e)}")
        except Exception as e:
            self.reg_status_var.set(f"Error: {str(e)}")

    def show_device_registration(self):
        """Show device registration screen"""
        self.clear_frame()

        # Header section
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(20, 15))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="📝 Complete Registration",
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(header_frame, text="Register this device for stress monitoring",
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0)

        # Main content card with scrollable area
        content_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding="20")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=40, pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Create scrollable content area
        scrollable_content = self.create_scrollable_frame(content_frame)

        # Info section
        info_frame = ttk.Frame(scrollable_content, style="Card.TFrame")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))

        info_text = f"👤 Logged in as: {self.current_user.get('username', 'Unknown')}\n\n"
        info_text += "📋 Please complete your registration and register this device for stress monitoring."

        info_label = ttk.Label(info_frame, text=info_text,
                              font=("Segoe UI", 11),
                              foreground=self.colors['text'],
                              background=self.colors['surface'],
                              justify=tk.LEFT)
        info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Get device info
        device_info = self.get_device_info()

        # User information section
        user_frame = ttk.LabelFrame(scrollable_content, text="👤 User Information", style="Card.TLabelframe", padding="15")
        user_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        user_frame.columnconfigure(1, weight=1)

        # Username field
        username_label = ttk.Label(user_frame, text="Username", style="Form.TLabel")
        username_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_username_var = tk.StringVar()
        self.reg_username_var.set(self.current_user.get('username', ''))
        username_entry = ttk.Entry(user_frame, textvariable=self.reg_username_var, style="Modern.TEntry")
        username_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Full Name field
        fullname_label = ttk.Label(user_frame, text="Full Name", style="Form.TLabel")
        fullname_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_fullname_var = tk.StringVar()
        self.reg_fullname_var.set(self.current_user.get('full_name', ''))
        fullname_entry = ttk.Entry(user_frame, textvariable=self.reg_fullname_var, style="Modern.TEntry")
        fullname_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Email field
        email_label = ttk.Label(user_frame, text="Email Address", style="Form.TLabel")
        email_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 8))

        self.reg_email_var = tk.StringVar()
        self.reg_email_var.set(self.current_user.get('email', ''))
        email_entry = ttk.Entry(user_frame, textvariable=self.reg_email_var, style="Modern.TEntry")
        email_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Device information section
        device_frame = ttk.LabelFrame(scrollable_content, text="🖥️ Device Information", style="Card.TLabelframe", padding="15")
        device_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        device_frame.columnconfigure(1, weight=1)

        # Employee ID field
        employee_label = ttk.Label(device_frame, text="Employee ID", style="Form.TLabel")
        employee_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        self.employee_id_var = tk.StringVar()
        self.employee_id_var.set(self.current_user.get('employee_id', ''))
        employee_entry = ttk.Entry(device_frame, textvariable=self.employee_id_var, style="Modern.TEntry")
        employee_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Device Name field
        device_name_label = ttk.Label(device_frame, text="Device Name", style="Form.TLabel")
        device_name_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        self.device_name_var = tk.StringVar()
        self.device_name_var.set(f"{self.current_user.get('username', 'User')}'s Device")
        device_entry = ttk.Entry(device_frame, textvariable=self.device_name_var, style="Modern.TEntry")
        device_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Device Number field
        device_number_label = ttk.Label(device_frame, text="Device Number", style="Form.TLabel")
        device_number_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 8))

        self.device_number_var = tk.StringVar()
        self.device_number_var.set(device_info.get('device_number', ''))
        device_number_entry = ttk.Entry(device_frame, textvariable=self.device_number_var, style="Modern.TEntry")
        device_number_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # System information display
        system_frame = ttk.LabelFrame(scrollable_content, text="🔧 System Information", style="Card.TLabelframe", padding="15")
        system_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        system_frame.columnconfigure(0, weight=1)

        device_info_text = f"Device Name: {self.device_name_var.get()}\n"
        device_info_text += f"Device Number: {device_info.get('device_number', 'Unknown')}\n"
        device_info_text += f"OS: {device_info.get('os', 'Unknown')}\n"
        device_info_text += f"OS Version: {device_info.get('os_version', 'Unknown')}\n"
        device_info_text += f"Architecture: {device_info.get('architecture', 'Unknown')}\n"
        device_info_text += f"Hostname: {device_info.get('hostname', 'Unknown')}\n"
        device_info_text += f"MAC Address: {device_info.get('mac_address', 'Unknown')}"

        device_info_label = ttk.Label(system_frame, text=device_info_text,
                                     font=("Segoe UI", 9),
                                     foreground=self.colors['text_secondary'],
                                     background=self.colors['surface'],
                                     justify=tk.LEFT)
        device_info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Store reference to device info label for updates
        self.device_info_label = device_info_label

        # Buttons section - place at bottom of scrollable area
        button_frame = ttk.Frame(scrollable_content, style="Card.TFrame")
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 20))

        register_btn = ttk.Button(
            button_frame,
            text="✅ Complete Registration",
            style="Success.TButton",
            command=self.do_register_device
        )
        register_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        logout_btn = ttk.Button(
            button_frame,
            text="🚪 Logout",
            style="Secondary.TButton",
            command=self.logout
        )
        logout_btn.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Status label
        self.register_status_var = tk.StringVar()
        status_label = ttk.Label(
            scrollable_content,
            textvariable=self.register_status_var,
            style="Status.TLabel",
            foreground=self.colors['error']
        )
        status_label.grid(row=5, column=0, pady=(10, 20))

    def do_register_device(self):
        """Complete registration - register device"""
        # Get form data
        username = self.reg_username_var.get().strip()
        fullname = self.reg_fullname_var.get().strip()
        email = self.reg_email_var.get().strip()
        employee_id = self.employee_id_var.get().strip()
        device_name = self.device_name_var.get().strip()
        device_number = self.device_number_var.get().strip()

        # Validation
        if not all([username, fullname, email, employee_id]):
            self.register_status_var.set("Please fill in all required fields.")
            return

        # Use the entered device name or default
        if not device_name:
            device_name = f"{username}'s Device"

        if not device_number:
            device_number = self.get_device_info().get('device_number', 'Unknown')

        # Get device info
        device_info = self.get_device_info()

        # Register device
        try:
            url = f"{self.backend_url}{self.api_prefix}/devices/register"
            data = {
                "employee_id": employee_id,
                "device_name": device_name,
                "device_number": device_number,
                "device_type": "windows_agent",
                "device_info": {
                    "os": device_info.get('os', 'Unknown'),
                    "os_version": device_info.get('os_version', 'Unknown'),
                    "architecture": device_info.get('architecture', 'Unknown'),
                    "hostname": device_info.get('hostname', 'Unknown'),
                    "mac_address": device_info.get('mac_address', 'Unknown')
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            logger.info(f"[DEVICE REGISTRATION] Sending registration data: {data}")
            logger.info(f"[DEVICE REGISTRATION] URL: {url}")
            logger.info(f"[DEVICE REGISTRATION] Headers: {headers}")

            response = requests.post(url, json=data, headers=headers)
            
            logger.info(f"[DEVICE REGISTRATION] Response status: {response.status_code}")
            logger.info(f"[DEVICE REGISTRATION] Response text: {response.text}")
            
            response.raise_for_status()

            result = response.json()
            logger.info(f"[DEVICE REGISTRATION] Registration successful: {result}")

            # Save configuration
            config = {
                "device_id": result['device_id'],
                "api_key": result['api_key'],
                "employee_id": employee_id,
                "device_name": device_name,
                "device_number": device_number,
                "username": username,
                "user_id": self.current_user.get('user_id'),
                "role": "employee",
                "registered_at": datetime.now().isoformat(),
                "backend_url": self.backend_url
            }
            self.save_config(config)

            self.register_status_var.set("Registration completed successfully!")
            self.root.after(1000, self.show_main_menu)

        except requests.exceptions.RequestException as e:
            self.register_status_var.set(f"Registration failed: {str(e)}")
        except Exception as e:
            self.register_status_var.set(f"Error: {str(e)}")

    def show_main_menu(self):
        """Show main menu"""
        self.clear_frame()

        # Load config
        config = self.load_config()

        # Header section
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(20, 15))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="Control Panel",
                                   style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(header_frame, text="Manage your StressSense monitoring system",
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0)

        # Main content area with scrollable content
        content_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding="20")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=40, pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Create scrollable content area
        scrollable_content = self.create_scrollable_frame(content_frame)

        # Status info card
        status_frame = ttk.LabelFrame(scrollable_content, text="System Status", style="Card.TLabelframe", padding="20")
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 30))
        status_frame.columnconfigure(0, weight=1)

        if config:
            status_text = f"User: {config.get('username', 'Unknown')}\n"
            status_text += f"Device: {config.get('device_name', 'Unknown')}\n"
            status_text += f"Device Number: {config.get('device_number', 'Unknown')}\n"
            status_text += f"Employee ID: {config.get('employee_id', 'Unknown')}\n"
            status_text += f"✅ Status: Active & Registered"
            status_color = self.colors['success']
        else:
            status_text = "❌ Status: Not Registered"
            status_color = self.colors['error']

        status_label = ttk.Label(status_frame, text=status_text,
                                font=("Segoe UI", 11),
                                foreground=status_color,
                                background=self.colors['surface'],
                                justify=tk.LEFT)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Service control section
        if config:
            service_frame = ttk.LabelFrame(scrollable_content, text="Service Management", style="Card.TLabelframe", padding="20")
            service_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 30))

            # Service buttons in a grid
            install_btn = ttk.Button(service_frame, text="📦 Install Service",
                                   style="Secondary.TButton", command=self.install_service)
            install_btn.grid(row=0, column=0, padx=(0, 10), pady=5)

            start_btn = ttk.Button(service_frame, text="▶️ Start Service",
                                 style="Success.TButton", command=self.start_service)
            start_btn.grid(row=0, column=1, padx=(0, 10), pady=5)

            stop_btn = ttk.Button(service_frame, text="⏹️ Stop Service",
                                style="Secondary.TButton", command=self.stop_service)
            stop_btn.grid(row=0, column=2, padx=(0, 10), pady=5)

            uninstall_btn = ttk.Button(service_frame, text="🗑️ Uninstall Service",
                                     style="Secondary.TButton", command=self.uninstall_service)
            uninstall_btn.grid(row=0, column=3, pady=5)

            # Testing section
            test_frame = ttk.LabelFrame(scrollable_content, text="🧪 Testing & Diagnostics", style="Card.TLabelframe", padding="20")
            test_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 30))

            test_btn = ttk.Button(test_frame, text="🔍 Test Stress Detection",
                                style="Primary.TButton", command=self.test_detection)
            test_btn.grid(row=0, column=0, padx=(0, 10), pady=5)

            # Status label for test results
            self.service_status_var = tk.StringVar()
            self.service_status_var.set("Ready")
            status_label = ttk.Label(test_frame, textvariable=self.service_status_var,
                                   font=("Segoe UI", 10),
                                   background=self.colors['surface'])
            status_label.grid(row=0, column=1, padx=(10, 0), pady=5)

        # Bottom actions - place at bottom of scrollable area
        bottom_frame = ttk.Frame(scrollable_content, style="Card.TFrame")
        bottom_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(20, 20))

        if config:
            re_register_btn = ttk.Button(bottom_frame, text="🔄 Re-register Device",
                                       style="Secondary.TButton", command=self.re_register)
            re_register_btn.grid(row=0, column=0, padx=(0, 10))

        logout_btn = ttk.Button(bottom_frame, text="🚪 Logout",
                              style="Secondary.TButton", command=self.logout)
        logout_btn.grid(row=0, column=1)

        # Start auto analysis if device is registered
        if config and not self.auto_timer:
            self.start_auto_analysis()

    def install_service(self):
        """Install the Windows service"""
        try:
            result = subprocess.run([sys.executable, "install_service.py"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service installed successfully!")
            else:
                messagebox.showerror("Error", f"Failed to install service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error installing service: {str(e)}")

    def start_service(self):
        """Start the Windows service"""
        try:
            result = subprocess.run([sys.executable, "start_service.py"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service started successfully!")
            else:
                messagebox.showerror("Error", f"Failed to start service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting service: {str(e)}")

    def stop_service(self):
        """Stop the Windows service"""
        try:
            result = subprocess.run([sys.executable, "start_service.py", "stop"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service stopped successfully!")
            else:
                messagebox.showerror("Error", f"Failed to stop service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping service: {str(e)}")

    def uninstall_service(self):
        """Uninstall the Windows service"""
        try:
            result = subprocess.run([sys.executable, "install_service.py", "uninstall"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service uninstalled successfully!")
            else:
                messagebox.showerror("Error", f"Failed to uninstall service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error uninstalling service: {str(e)}")

    def test_detection(self):
        """Test stress detection and send to backend"""
        config = self.load_config()
        if not config:
            self.service_status_var.set("Device not registered")
            return

        self.service_status_var.set("Testing...")

        def run_test():
            try:
                # Check if stress analysis is available
                if analyze_image is None:
                    logger.error("[TEST DETECTION] analyze_image function not available")
                    self.service_status_var.set("Analysis module not available")
                    return
                    
                import cv2
                import base64
                from datetime import datetime

                # Load emotion stress map
                get_emotion_stress_map()

                # Capture image with better error handling
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.error("[IMAGE CAPTURE] Failed to open webcam")
                    self.service_status_var.set("No webcam found")
                    return

                # Try multiple capture attempts
                max_attempts = int(os.getenv("MAX_CAPTURE_ATTEMPTS", "3"))
                retry_delay = float(os.getenv("CAPTURE_RETRY_DELAY_SECONDS", "0.5"))
                ret = False
                frame = None
                for attempt in range(max_attempts):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        break
                    logger.warning(f"[IMAGE CAPTURE] Capture attempt {attempt + 1} failed, retrying...")
                    time.sleep(retry_delay)  # Configurable wait before retry
                
                cap.release()

                if not ret or frame is None:
                    logger.error(f"[IMAGE CAPTURE] Failed to capture image after {max_attempts} attempts")
                    self.service_status_var.set("Failed to capture image")
                    return

                # Validate captured frame
                if frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
                    logger.error(f"[IMAGE CAPTURE] Invalid frame dimensions: {frame.shape}")
                    self.service_status_var.set("Invalid image captured")
                    return

                logger.info(f"[IMAGE CAPTURE] Successfully captured image with shape: {frame.shape}")

                # Convert to base64 with error handling
                try:
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    if buffer is None or buffer.size == 0:
                        logger.error("[IMAGE CAPTURE] Failed to encode image to JPEG")
                        self.service_status_var.set("Failed to encode image")
                        return
                    
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    if not img_base64:
                        logger.error("[IMAGE CAPTURE] Base64 encoding resulted in empty string")
                        self.service_status_var.set("Failed to encode image data")
                        return
                        
                except Exception as encode_error:
                    logger.error(f"[IMAGE CAPTURE] Error encoding image: {str(encode_error)}")
                    self.service_status_var.set("Failed to process image")
                    return

                # Analyze locally
                result = analyze_image(img_base64)

                if result is None or not isinstance(result, dict):
                    self.service_status_var.set("Analysis failed")
                    return

                if "error" in result:
                    self.service_status_var.set(f"Error: {result['error']}")
                    return

                # Show local result first
                emotion = result.get('emotion', 'Unknown')
                stress_level = result.get('stress_level', 'Unknown')
                confidence = result.get('confidence', 0) or 0
                local_result = f"Detected: {emotion} -> {stress_level} ({confidence:.1f}%)"

                logger.info(f"[LOCAL ANALYSIS] Result: {local_result}")
                self.service_status_var.set(local_result)

                # Show notification if high stress detected
                if stress_level == "High":
                    show_stress_notification()
                    logger.info("[SERVICE] High stress notification shown")

                # Send to backend
                logger.info("[BACKEND] Starting backend submission...")
                try:
                    url = f"{self.backend_url}{self.api_prefix}/stress/record"
                    api_key = config.get('api_key')
                    logger.info(f"[BACKEND] Using API key: {api_key[:8]}...")
                    headers = {
                        "X-Device-Key": api_key,
                        "Content-Type": "application/json"
                    }

                    # Map emotion to API enum format
                    emotion_map = {
                        'angry': 'angry',
                        'disgusted': 'disgust',
                        'fearful': 'fear',
                        'happy': 'happy',
                        'neutral': 'neutral',
                        'sad': 'sad',
                        'surprised': 'surprise'
                    }

                    api_emotion = emotion_map.get(emotion, 'neutral')

                    # Prepare submission data
                    submission_data = {
                        "emotion": api_emotion,
                        "stress_level": stress_level,
                        "confidence": float(confidence * 100),  # Convert to 0-100 scale
                        "timestamp": datetime.now().isoformat(),
                        "face_quality": result.get('face_quality', {})
                    }

                    print(f"[FRONTEND] Sending stress data to backend: {submission_data}")
                    print(f"[FRONTEND] URL: {url}")
                    print(f"[FRONTEND] Headers: {headers}")

                    logger.info(f"[STRESS SUBMISSION] Sending stress data: {submission_data}")
                    logger.info(f"[STRESS SUBMISSION] URL: {url}")
                    logger.info(f"[STRESS SUBMISSION] Headers: {headers}")

                    response = requests.post(url, json=submission_data, headers=headers)
                    print(f"[FRONTEND] Response status: {response.status_code}")
                    print(f"[FRONTEND] Response text: {response.text}")
                    
                    logger.info(f"[STRESS SUBMISSION] Response status: {response.status_code}")
                    logger.info(f"[STRESS SUBMISSION] Response text: {response.text}")
                    
                    response.raise_for_status()

                    backend_result = response.json()
                    record_id = backend_result.get('record_id', 'Unknown')

                    print(f"[FRONTEND] Successfully saved record: {record_id}")
                    logger.info(f"[STRESS SUBMISSION] Successfully saved record: {record_id}")
                    self.service_status_var.set(f"{local_result} | Saved: {record_id}")

                except requests.exceptions.RequestException as e:
                    print(f"[FRONTEND] Backend request failed: {str(e)}")
                    logger.error(f"[STRESS SUBMISSION] Backend request failed: {str(e)}")
                    self.service_status_var.set(f"{local_result} | Backend Error: {str(e)}")
                except Exception as e:
                    print(f"[FRONTEND] Save error: {str(e)}")
                    self.service_status_var.set(f"{local_result} | Save Error: {str(e)}")

            except Exception as e:
                self.service_status_var.set(f"Error: {str(e)}")

        # Run in thread to avoid blocking UI
        threading.Thread(target=run_test, daemon=True).start()

    def re_register(self):
        """Re-register device"""
        if messagebox.askyesno("Confirm", "This will unregister the current device. Continue?"):
            # Delete config using the same path logic as save_config()
            config_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), self.config_file)
            if os.path.exists(config_path):
                os.remove(config_path)
                logger.info("Config file deleted for re-registration")

            # Clear session data
            self.current_user = None
            self.access_token = None
            
            # Remove session file
            if os.path.exists(self.session_file):
                try:
                    os.remove(self.session_file)
                    logger.info("Session file removed")
                except Exception as e:
                    logger.error(f"Error removing session file: {e}")
            
            # Go back to login screen
            self.show_login()

    def logout(self):
        """Logout user"""
        # Cancel auto analysis timer
        if self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = None
        
        # Cancel remote check timer
        if hasattr(self, 'remote_timer') and self.remote_timer:
            self.remote_timer.cancel()
            self.remote_timer = None
        
        self.current_user = None
        self.access_token = None
        
        # Remove session file
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
                logger.info("Session file removed")
            except Exception as e:
                logger.error(f"Error removing session file: {e}")
        
        self.show_terms_conditions()

    def load_config(self):
        """Load device configuration"""
        # Check if running in bundled environment
        is_bundled = getattr(sys, '_MEIPASS', None) is not None
        print(f"[CONFIG] Running in bundled environment: {is_bundled}")

        if is_bundled:
            # In bundled app, only look in the executable's directory
            bundle_dir = os.path.dirname(sys.executable)
            config_path = os.path.join(bundle_dir, self.config_file)
            print(f"[CONFIG] Looking for config in bundled dir: {config_path}")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        print(f"[CONFIG] Found config in bundled app: {config.get('device_id', 'unknown')}")
                        return config
                except Exception as e:
                    print(f"[CONFIG] Error loading bundled config: {e}")
                    return None
            print("[CONFIG] No config found in bundled app")
            return None
        else:
            # Development mode - search multiple locations
            print("[CONFIG] Running in development mode")
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
            grandparent_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
            for base_dir in [os.getcwd(), script_dir, parent_dir, grandparent_dir]:
                config_path = os.path.join(base_dir, self.config_file)
                print(f"[CONFIG] Checking: {config_path}")
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            print(f"[CONFIG] Found config in dev mode: {config.get('device_id', 'unknown')}")
                            return config
                    except Exception as e:
                        print(f"[CONFIG] Error loading dev config: {e}")
                        return None
            print("[CONFIG] No config found in development mode")
            return None

    def save_config(self, config):
        """Save device configuration"""
        if getattr(sys, '_MEIPASS', None):
            # In bundled app, save in the executable's directory
            config_path = os.path.join(os.path.dirname(sys.executable), self.config_file)
        else:
            # Development mode - save in script directory
            config_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), self.config_file)

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def load_session(self):
        """Load user session from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Check if session is still valid (not expired)
                if self.validate_session(session_data):
                    self.current_user = session_data.get('user')
                    self.access_token = session_data.get('access_token')
                    logger.info(f"Loaded existing session for user: {self.current_user.get('username', 'Unknown')}")
                    return True  # Indicate valid session was loaded
                else:
                    logger.info("Session expired, user needs to login again")
                    os.remove(self.session_file)  # Remove expired session
                    return False  # No valid session
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False  # No valid session on error
        except Exception as e:
            logger.error(f"Error loading session: {e}")

    def save_session(self, user_data, access_token):
        """Save user session to file"""
        try:
            session_data = {
                'user': user_data,
                'access_token': access_token,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Error saving session: {e}")

    def validate_session(self, session_data):
        """Validate if session is still active"""
        try:
            # Check if access token exists
            token = session_data.get('access_token')
            if not token:
                return False
            
            # For now, just check if token exists and session is not too old
            # In a production app, you'd validate the JWT token properly
            timestamp = session_data.get('timestamp')
            if timestamp:
                session_time = datetime.fromisoformat(timestamp)
                # Session valid for 24 hours
                if datetime.now() - session_time > timedelta(hours=24):
                    logger.info("Session is too old (24+ hours)")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False

    def start_auto_analysis(self):
        """Start automatic stress analysis every 2 minutes (dev mode)"""
        if hasattr(self, 'auto_timer') and self.auto_timer:
            self.auto_timer.cancel()

        auto_interval = int(os.getenv("AUTO_ANALYSIS_INTERVAL_SECONDS", "120"))
        if auto_interval > 0:
            self.auto_timer = threading.Timer(auto_interval, self.run_auto_analysis)  # Configurable interval
        self.auto_timer.start()
        logger.info("[AUTO ANALYSIS] Started automatic stress analysis (every 2 minutes - dev mode)")

        # Also start checking for remote stress requests
        self.start_remote_check_timer()

    def start_remote_check_timer(self):
        """Start timer to check for remote stress check requests"""
        if hasattr(self, 'remote_timer') and self.remote_timer:
            self.remote_timer.cancel()

        # Use shorter interval for more responsive checking (30 seconds in dev mode)
        check_interval = 30  # 30 seconds for dev mode
        self.remote_timer = threading.Timer(check_interval, self.check_remote_stress_requests)
        self.remote_timer.start()
        logger.info(f"[REMOTE CHECK] Started checking for remote stress requests (every {check_interval} seconds - dev mode)")

    def check_remote_stress_requests(self):
        """Check for pending remote stress check requests"""
        config = self.load_config()
        if not config:
            logger.warning("[REMOTE CHECK] Device not registered, skipping remote check")
            self.start_remote_check_timer()  # Still restart timer
            return

        # Check if we have a valid access token
        if not self.access_token:
            logger.warning("[REMOTE CHECK] No access token available, skipping remote check")
            self.start_remote_check_timer()
            return

        try:
            url = f"{self.backend_url}{self.api_prefix}/stress/remote-check/{config.get('employee_id')}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            logger.debug(f"[REMOTE CHECK] Checking for remote requests: {url}")
            timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
            response = requests.get(url, headers=headers, timeout=timeout_seconds)  # Configurable timeout

            if response.status_code == 200:
                request_data = response.json()
                if request_data and request_data.get('pending_request'):
                    logger.info("[REMOTE CHECK] Found pending remote stress check request - processing immediately")
                    # Run stress detection for remote request
                    self.run_remote_stress_check(request_data)
                    # After processing, restart timer with normal interval
                    self.start_remote_check_timer()
                else:
                    logger.debug("[REMOTE CHECK] No pending requests")
                    self.start_remote_check_timer()
            elif response.status_code == 401:
                logger.warning("[REMOTE CHECK] Authentication failed - token may be expired")
                self.start_remote_check_timer()
            elif response.status_code == 404:
                logger.warning("[REMOTE CHECK] Remote check endpoint not found - backend may need restart")
                self.start_remote_check_timer()
            else:
                logger.warning(f"[REMOTE CHECK] Failed to check remote requests: HTTP {response.status_code}")
                self.start_remote_check_timer()

        except requests.exceptions.Timeout:
            logger.warning("[REMOTE CHECK] Request timed out")
            self.start_remote_check_timer()
        except requests.exceptions.ConnectionError:
            logger.warning("[REMOTE CHECK] Connection error - backend may be down")
            self.start_remote_check_timer()
        except Exception as e:
            logger.error(f"[REMOTE CHECK] Error checking remote requests: {str(e)}")
            self.start_remote_check_timer()

    def run_remote_stress_check(self, request_data):
        """Run stress detection for remote request"""
        if not request_data:
            logger.error("[REMOTE STRESS] Invalid request data received")
            return
            
        logger.info("[REMOTE STRESS] Running remote stress check")

        def run_check():
            try:
                # Check if stress analysis is available
                if analyze_image is None or analyze_image_array is None:
                    logger.error("[REMOTE STRESS] stress_analysis module not available")
                    return
                import cv2
                from datetime import datetime

                # Load emotion stress map
                get_emotion_stress_map()

                if EMOTION_STRESS_MAP is None:
                    logger.error("[REMOTE STRESS] Failed to load emotion stress map")
                    return

                # Capture image with better error handling
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.warning("[REMOTE STRESS] No webcam found")
                    return

                # Try multiple capture attempts
                ret = False
                frame = None
                for attempt in range(3):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        break
                    logger.warning(f"[REMOTE STRESS] Capture attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.5)  # Wait before retry
                
                cap.release()

                if not ret or frame is None:
                    logger.warning("[REMOTE STRESS] Failed to capture image after 3 attempts")
                    return

                # Validate captured frame
                if frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
                    logger.warning(f"[REMOTE STRESS] Invalid frame dimensions: {frame.shape}")
                    return

                logger.info(f"[REMOTE STRESS] Successfully captured image with shape: {frame.shape}")

                # Analyze stress (no need to convert to base64 for local analysis)
                result = analyze_image_array(frame)

                if not result:
                    logger.error("[REMOTE STRESS] Analysis failed - no result returned")
                    return

                logger.info(f"[REMOTE STRESS] Analysis result: {result}")
                if "error" in result:
                    logger.warning(f"[REMOTE STRESS] Analysis returned error: {result['error']}")
                    return
                confidence = result.get('confidence', 0)
                emotion = result.get('emotion', 'unknown')
                logger.info(f"[REMOTE STRESS] Confidence: {confidence} (type: {type(confidence)}), Emotion: {emotion}")
                emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25}) if EMOTION_STRESS_MAP else {"min_confidence": 25}
                logger.info(f"[REMOTE STRESS] Required confidence for {emotion}: {emotion_config['min_confidence']}%")

                # Use emotion-specific confidence threshold
                emotion = result.get('emotion', '')
                emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25}) if EMOTION_STRESS_MAP else {"min_confidence": 25}
                min_confidence = emotion_config["min_confidence"] / 100.0
                
                confidence_val = float(result.get('confidence', 0))
                should_submit = confidence_val > min_confidence
                
                logger.info(f"[REMOTE STRESS] Emotion: {emotion}, Confidence: {confidence_val:.3f}, Min required: {min_confidence:.3f} ({emotion_config['min_confidence']}%), Should submit: {should_submit}")
                
                if should_submit:
                    # Submit to backend with remote request info
                    logger.info("[REMOTE STRESS] Starting backend submission for high confidence result")
                    config = self.load_config()
                    if config:
                        url = f"{self.backend_url}{self.api_prefix}/stress/remote-submit"
                        
                        # Map emotion to API enum format
                        emotion = result.get('emotion', 'neutral')
                        emotion_map = {
                            'angry': 'angry',
                            'disgusted': 'disgust',
                            'fearful': 'fear',
                            'happy': 'happy',
                            'neutral': 'neutral',
                            'sad': 'sad',
                            'surprised': 'surprise'
                        }
                        api_emotion = emotion_map.get(emotion, 'neutral')
                        
                        logger.info(f"[REMOTE STRESS] Original emotion: {emotion}, Mapped emotion: {api_emotion}")
                        
                        data = {
                            "stress_level": result.get('stress_level', 'Low'),
                            "emotion": api_emotion,
                            "confidence": result.get('confidence', 0) * 100,  # Convert to 0-100 scale
                            "request_id": request_data.get('request_id') if request_data else None,
                            "remote_request": True
                        }

                        headers = {
                            "X-Device-Key": config.get('api_key'),
                            "Content-Type": "application/json"
                        }

                        logger.info(f"[REMOTE STRESS] Using API key: {config.get('api_key')[:8]}...")
                        logger.info(f"[REMOTE STRESS] Submitting to: {url}")

                        try:
                            response = requests.post(url, json=data, headers=headers, timeout=30)
                            if response.status_code in [200, 201]:
                                logger.info(f"[REMOTE STRESS] Remote stress data submitted successfully: {result}")
                            else:
                                logger.error(f"[REMOTE STRESS] Failed to submit data. Status: {response.status_code}, Response: {response.text}")
                        except Exception as submit_error:
                            logger.error(f"[REMOTE STRESS] Error submitting to backend: {str(submit_error)}")

            except Exception as e:
                logger.error(f"[REMOTE STRESS] Error: {str(e)}")

        # Run in background thread
        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()

    def run_auto_analysis(self):
        """Run automatic stress analysis"""
        # Check if within office hours
        if not is_office_hours():
            logger.info("[AUTO ANALYSIS] Outside office hours (9 AM - 6 PM), skipping analysis")
            return

        config = self.load_config()
        if not config:
            logger.warning("[AUTO ANALYSIS] Device not registered, skipping analysis")
            return

        logger.info("[AUTO ANALYSIS] Running automatic stress analysis")
        # Run the same test detection logic
        self.test_detection_background()

        # Restart timer
        self.start_auto_analysis()

    def test_detection_background(self):
        """Run stress detection in background"""
        def run_test():
            try:
                # Check if stress analysis is available
                if analyze_image is None or analyze_image_array is None:
                    logger.error("[AUTO ANALYSIS] stress_analysis module not available")
                    return
                    
                import cv2
                import base64
                from datetime import datetime

                # Load emotion stress map
                get_emotion_stress_map()

                if EMOTION_STRESS_MAP is None:
                    logger.error("[AUTO ANALYSIS] Failed to load emotion stress map")
                    return

                # Capture image with better error handling
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.warning("[AUTO ANALYSIS] No webcam found")
                    return

                # Try multiple capture attempts
                ret = False
                frame = None
                for attempt in range(3):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        break
                    logger.warning(f"[AUTO ANALYSIS] Capture attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.5)  # Wait before retry
                
                cap.release()

                if not ret or frame is None:
                    logger.warning("[AUTO ANALYSIS] Failed to capture image after 3 attempts")
                    return

                # Validate captured frame
                if frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
                    logger.warning(f"[AUTO ANALYSIS] Invalid frame dimensions: {frame.shape}")
                    return

                logger.debug(f"[AUTO ANALYSIS] Successfully captured image with shape: {frame.shape}")

                # Analyze stress (no need to convert to base64 for local analysis)
                result = analyze_image_array(frame)

                if result is None:
                    logger.warning("[AUTO ANALYSIS] Analysis returned None, skipping")
                    return

                if not isinstance(result, dict):
                    logger.warning(f"[AUTO ANALYSIS] Analysis returned {type(result)}, expected dict, skipping")
                    return

                logger.info(f"[AUTO ANALYSIS] Analysis result: {result}")
                if result:
                    if "error" in result:
                        logger.warning(f"[AUTO ANALYSIS] Analysis returned error: {result['error']}")
                    confidence = result.get('confidence', 0)
                    emotion = result.get('emotion', 'unknown')
                    logger.info(f"[AUTO ANALYSIS] Confidence: {confidence} (type: {type(confidence)}), Emotion: {emotion}")
                    emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25}) if EMOTION_STRESS_MAP else {"min_confidence": 25}
                    logger.info(f"[AUTO ANALYSIS] Required confidence for {emotion}: {emotion_config['min_confidence']}%")

                # Use emotion-specific confidence threshold instead of fixed 0.5
                emotion = result.get('emotion', '') if result else ''
                emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25}) if EMOTION_STRESS_MAP else {"min_confidence": 25}
                min_confidence = emotion_config["min_confidence"] / 100.0  # Convert to decimal
                
                confidence_val = float(result.get('confidence', 0)) if result else 0.0
                should_submit = confidence_val > min_confidence
                
                logger.info(f"[AUTO ANALYSIS] Emotion: {emotion}, Confidence: {confidence_val:.3f}, Min required: {min_confidence:.3f} ({emotion_config['min_confidence']}%), Should submit: {should_submit}")
                
                if result and "error" not in result and confidence_val > min_confidence:
                    # Submit to backend
                    logger.info("[AUTO ANALYSIS] Starting backend submission for high confidence result")
                    config = self.load_config()
                    if config:
                        url = f"{self.backend_url}{self.api_prefix}/stress/record"
                        api_key = config.get('api_key')
                        if api_key:
                            logger.info(f"[AUTO ANALYSIS] Using API key: {api_key[:8]}...")
                            
                            # Map emotion to API enum format
                            emotion = result.get('emotion')
                            emotion_map = {
                                'angry': 'angry',
                                'disgusted': 'disgust',
                                'fearful': 'fear',
                                'happy': 'happy',
                                'neutral': 'neutral',
                                'sad': 'sad',
                                'surprised': 'surprise'
                            }
                            api_emotion = emotion_map.get(emotion, 'neutral')
                            logger.info(f"[AUTO ANALYSIS] Original emotion: {emotion}, Mapped emotion: {api_emotion}")
                            
                            headers = {
                                "X-Device-Key": api_key,
                                "Content-Type": "application/json"
                            }
                            data = {
                                "emotion": api_emotion,
                                "stress_level": result.get('stress_level', 'unknown'),
                                "confidence": (result.get('confidence', 0) or 0) * 100,  # Convert to 0-100 scale
                                "timestamp": datetime.now().isoformat(),
                                "face_quality": result.get('face_quality', {})
                            }

                            # Show notification if high stress detected
                            stress_level = result.get('stress_level', 'unknown')
                            if stress_level == "High":
                                show_stress_notification()
                                logger.info("[AUTO ANALYSIS] High stress notification shown")

                            response = requests.post(url, json=data, headers=headers)
                            status_code = response.status_code
                            if status_code in [200, 201] or str(status_code) in ["200", "201"]:
                                logger.info(f"[AUTO ANALYSIS] Stress data submitted: {result}")
                            else:
                                logger.warning(f"[AUTO ANALYSIS] Failed to submit: {status_code} (type: {type(status_code)})")
                        else:
                            logger.warning("[AUTO ANALYSIS] No API key found in config, skipping submission")
                    else:
                        logger.warning("[AUTO ANALYSIS] No config found, skipping backend submission")

            except Exception as e:
                logger.error(f"[AUTO ANALYSIS] Error: {str(e)}")

        # Run in background thread
        thread = threading.Thread(target=run_test)
        thread.daemon = True
        thread.start()

    def get_device_info(self):
        """Collect and return basic device information"""
        import platform, uuid
        mac_num = uuid.getnode()
        mac = ':'.join(f"{(mac_num >> ele) & 0xff:02x}" for ele in range(0,48,8)[::-1])
        return {
            'device_number': str(mac_num),
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'mac_address': mac
        }

def main():
    root = tk.Tk()
    app = StressDetectionApp(root)
    
    # Start automatic analysis if device is registered
    config = app.load_config()
    if config:
        app.start_auto_analysis()
    
    # Handle app closing
    def on_closing():
        if app.auto_timer:
            app.auto_timer.cancel()
        if hasattr(app, 'remote_timer') and app.remote_timer:
            app.remote_timer.cancel()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
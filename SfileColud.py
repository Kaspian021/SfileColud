import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from tkinter.font import Font
import requests
import webbrowser
import json
import os
from urllib.parse import urlparse, parse_qs
import pyperclip
from dotenv import load_dotenv
import threading
import time
import sv_ttk
from PIL import Image, ImageTk
import io
from datetime import datetime
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='SfileColud.log'
)

# Load environment variables
load_dotenv()


class SfileColud:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.initialize_variables()
        self.setup_ui()

    def setup_main_window(self):
        """Configure the main application window"""
        self.root.title("SfileColud Professional")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Try to load icon
        try:
            self.root.iconbitmap(self.resource_path('icon.ico'))
        except:
            pass

        # Center the window
        self.center_window()

    def resource_path(self, relative_path):
        """Get absolute path to resource for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def initialize_variables(self):
        """Initialize application variables"""
        # Theme settings
        self.theme_mode = "light"
        self.available_themes = ["light", "dark", "blue", "green"]

        # OAuth configuration
        self.client_config = {
            "installed": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', ''),
                "redirect_uris": ["http://localhost:8080"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        # User session
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.user_info = {}

        # File management
        self.file_path = ""
        self.current_folder_id = "root"
        self.folder_stack = ["root"]

    def setup_ui(self):
        """Setup the main user interface"""
        self.create_menu_bar()
        self.create_toolbar()
        self.create_main_notebook()
        self.create_status_bar()

        # Apply initial theme
        sv_ttk.set_theme(self.theme_mode)

    def create_menu_bar(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Upload", command=self.new_upload)
        file_menu.add_command(label="Open Folder", command=self.open_local_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy Link", command=self.copy_file_link)
        edit_menu.add_command(label="Refresh", command=self.load_files_list)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        """Create the toolbar with quick actions"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Navigation buttons
        self.back_btn = ttk.Button(
            self.toolbar,
            text="← Back",
            command=self.navigate_back,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, padx=2)

        self.up_btn = ttk.Button(
            self.toolbar,
            text="↑ Up",
            command=self.navigate_up,
            state=tk.DISABLED
        )
        self.up_btn.pack(side=tk.LEFT, padx=2)

        # Quick Upload button
        self.quick_upload_btn = ttk.Button(
            self.toolbar,
            text="Quick Upload",
            command=self.quick_upload,
            style='Accent.TButton'
        )
        self.quick_upload_btn.pack(side=tk.LEFT, padx=5)

        # User info
        self.user_label = ttk.Label(
            self.toolbar,
            text="User: Not logged in",
            font=('Helvetica', 10)
        )
        self.user_label.pack(side=tk.RIGHT, padx=10)

    def create_main_notebook(self):
        """Create the main notebook with tabs"""
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Create tabs
        self.create_drive_explorer_tab()
        self.create_upload_tab()
        self.create_settings_tab()

    def create_drive_explorer_tab(self):
        """Create the Drive Explorer tab"""
        self.explorer_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.explorer_tab, text="Drive Explorer")

        # Create file list with Treeview
        self.create_file_tree()

    def create_file_tree(self):
        """Create the file tree view with columns"""
        columns = ('name', 'size', 'type', 'modified', 'shared', 'id')
        self.files_tree = ttk.Treeview(
            self.explorer_tab,
            columns=columns,
            show='headings',
            selectmode='extended',
            height=25
        )

        # Configure columns
        self.files_tree.heading('name', text='Name', anchor=tk.W)
        self.files_tree.heading('size', text='Size', anchor=tk.CENTER)
        self.files_tree.heading('type', text='Type', anchor=tk.CENTER)
        self.files_tree.heading('modified', text='Modified', anchor=tk.CENTER)
        self.files_tree.heading('shared', text='Shared', anchor=tk.CENTER)
        self.files_tree.heading('id', text='ID')

        self.files_tree.column('name', width=300, anchor=tk.W)
        self.files_tree.column('size', width=100, anchor=tk.CENTER)
        self.files_tree.column('type', width=100, anchor=tk.CENTER)
        self.files_tree.column('modified', width=150, anchor=tk.CENTER)
        self.files_tree.column('shared', width=80, anchor=tk.CENTER)
        self.files_tree.column('id', width=0, stretch=tk.NO)  # Hidden column

        # Add scrollbars
        scroll_y = ttk.Scrollbar(self.explorer_tab, orient=tk.VERTICAL, command=self.files_tree.yview)
        scroll_x = ttk.Scrollbar(self.explorer_tab, orient=tk.HORIZONTAL, command=self.files_tree.xview)
        self.files_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Grid layout
        self.files_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        self.explorer_tab.grid_rowconfigure(0, weight=1)
        self.explorer_tab.grid_columnconfigure(0, weight=1)

        # Bind double click to open folders
        self.files_tree.bind('<Double-1>', self.on_tree_double_click)

        # Create context menu
        self.create_tree_context_menu()

    def create_tree_context_menu(self):
        """Create context menu for tree items"""
        self.tree_menu = tk.Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Open", command=self.open_selected_item)
        self.tree_menu.add_command(label="Download", command=self.download_file)
        self.tree_menu.add_command(label="Rename", command=self.rename_file)
        self.tree_menu.add_command(label="Share", command=self.share_file)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Delete", command=self.delete_file)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Properties", command=self.show_file_properties)

        self.files_tree.bind('<Button-3>', self.show_tree_menu)

    def open_selected_item(self):
        """Open selected item (file or folder)"""
        selected = self.files_tree.selection()
        if not selected:
            return

        item_id = self.files_tree.item(selected[0], 'values')[5]
        item_name = self.files_tree.item(selected[0], 'values')[0]

        # Check if it's a folder
        if self.files_tree.item(selected[0], 'tags')[0] == 'folder':
            self.navigate_to_folder(item_id)
        else:
            # For files, open in browser
            file_link = f"https://drive.google.com/file/d/{item_id}/view"
            webbrowser.open(file_link)

    def show_tree_menu(self, event):
        """Show context menu on right-click"""
        item = self.files_tree.identify_row(event.y)
        if item:
            self.files_tree.selection_set(item)
            self.tree_menu.post(event.x_root, event.y_root)

    def create_upload_tab(self):
        """Create the file upload tab"""
        self.upload_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.upload_tab, text="Upload Files")

        # Main container with padding
        container = ttk.Frame(self.upload_tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # File selection frame
        file_frame = ttk.LabelFrame(container, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, pady=5)

        # File entry and browse button
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)

        self.file_entry = ttk.Entry(file_select_frame)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(
            file_select_frame,
            text="Browse...",
            command=self.select_file,
            width=10
        ).pack(side=tk.LEFT)

        # File info display
        self.file_info_label = ttk.Label(
            file_frame,
            text="No file selected",
            wraplength=400
        )
        self.file_info_label.pack(fill=tk.X, pady=5)

        # Upload options frame
        options_frame = ttk.LabelFrame(container, text="Upload Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)

        # Destination folder
        ttk.Label(options_frame, text="Destination Folder:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=2)
        self.folder_entry = ttk.Entry(options_frame)
        self.folder_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.folder_entry.insert(0, "My Drive")

        ttk.Button(
            options_frame,
            text="Change...",
            command=self.select_destination_folder,
            width=10
        ).grid(row=0, column=2, padx=5, pady=2)

        # Configure grid weights
        options_frame.grid_columnconfigure(1, weight=1)

        # Progress frame
        progress_frame = ttk.LabelFrame(container, text="Upload Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(
            progress_frame,
            text="Ready to upload",
            anchor=tk.CENTER
        )
        self.progress_label.pack(fill=tk.X)

        # Upload button
        self.upload_btn = ttk.Button(
            container,
            text="Start Upload",
            command=self.upload_file,
            style='Accent.TButton',
            state=tk.DISABLED
        )
        self.upload_btn.pack(pady=10)

    def create_settings_tab(self):
        """Create the settings tab"""
        self.settings_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.settings_tab, text="Settings")

        # Main container with padding
        container = ttk.Frame(self.settings_tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Connection settings frame
        conn_frame = ttk.LabelFrame(container, text="Connection Settings", padding=10)
        conn_frame.pack(fill=tk.X, pady=5)

        # Client ID
        ttk.Label(conn_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.client_id_entry = ttk.Entry(conn_frame, width=50)
        self.client_id_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.client_id_entry.insert(0, self.client_config["installed"]["client_id"])

        # Client Secret
        ttk.Label(conn_frame, text="Client Secret:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.client_secret_entry = ttk.Entry(conn_frame, width=50, show="*")
        self.client_secret_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.client_secret_entry.insert(0, self.client_config["installed"]["client_secret"])

        # Redirect URI
        ttk.Label(conn_frame, text="Redirect URI:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.redirect_entry = ttk.Entry(conn_frame, width=50)
        self.redirect_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.redirect_entry.insert(0, self.client_config["installed"]["redirect_uris"][0])

        # Button frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame,
            text="Save Settings",
            command=self.save_settings,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Test Connection",
            command=self.test_connection
        ).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        conn_frame.grid_columnconfigure(1, weight=1)

    def create_status_bar(self):
        """Create the status bar at bottom of window"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        ttk.Label(
            self.status_bar,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Connection status
        self.connection_status = ttk.Label(
            self.status_bar,
            text="Not Connected",
            relief=tk.SUNKEN,
            width=15
        )
        self.connection_status.pack(side=tk.RIGHT)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.theme_mode == "light":
            sv_ttk.set_theme("dark")
            self.theme_mode = "dark"
        else:
            sv_ttk.set_theme("light")
            self.theme_mode = "light"

    def select_file(self):
        """Select a file for upload"""
        file_path = filedialog.askopenfilename(
            title="Select File to Upload",
            filetypes=[
                ("All Files", "*.*"),
                ("Documents", "*.doc *.docx *.pdf *.txt *.rtf"),
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Videos", "*.mp4 *.avi *.mov *.mkv")
            ]
        )

        if file_path:
            self.file_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.update_file_info()

            if self.access_token:
                self.upload_btn['state'] = tk.NORMAL

    def update_file_info(self):
        """Update file information display"""
        if not self.file_path:
            self.file_info_label.config(text="No file selected")
            return

        try:
            file_name = os.path.basename(self.file_path)
            file_size = os.path.getsize(self.file_path)

            info_text = f"File: {file_name}\nSize: {self.format_size(file_size)}"
            self.file_info_label.config(text=info_text)

        except Exception as e:
            logging.error(f"Error getting file info: {e}")
            self.file_info_label.config(text="Error getting file information")

    def select_destination_folder(self):
        """Select destination folder in Google Drive"""
        if not self.access_token:
            messagebox.showerror("Error", "You must be authenticated first")
            return

        # TODO: Implement folder selection dialog
        messagebox.showinfo("Info", "Folder selection will be implemented in a future version")

    def start_auth(self):
        """Start Google OAuth authentication"""
        if not self.client_config["installed"]["client_id"] or not self.client_config["installed"]["client_secret"]:
            messagebox.showerror("Error", "Please enter Client ID and Client Secret in Settings")
            self.main_notebook.select(self.settings_tab)
            return

        auth_url = (f"{self.client_config['installed']['auth_uri']}?"
                    f"client_id={self.client_config['installed']['client_id']}&"
                    f"redirect_uri={self.client_config['installed']['redirect_uris'][0]}&"
                    f"scope=https://www.googleapis.com/auth/drive&"
                    f"response_type=code&"
                    f"access_type=offline&"
                    f"prompt=consent")

        self.status_var.set("Opening browser for authentication...")
        webbrowser.open(auth_url)

        # Show auth code window
        self.show_auth_code_window()

    def show_auth_code_window(self):
        """Show window to enter auth code"""
        if hasattr(self, 'auth_window') and self.auth_window:
            self.auth_window.destroy()

        self.auth_window = tk.Toplevel(self.root)
        self.auth_window.title("Authentication Code")
        self.auth_window.geometry("500x300")
        self.auth_window.resizable(False, False)

        # Center the window
        self.auth_window.update_idletasks()
        width = self.auth_window.winfo_width()
        height = self.auth_window.winfo_height()
        x = (self.auth_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.auth_window.winfo_screenheight() // 2) - (height // 2)
        self.auth_window.geometry(f'{width}x{height}+{x}+{y}')

        # Content
        ttk.Label(
            self.auth_window,
            text="Authentication Steps:",
            font=('Helvetica', 10, "bold")
        ).pack(pady=(10, 5))

        instructions = (
            "1. After signing in, you'll be redirected to a local URL\n"
            "2. Copy the full URL from your browser's address bar\n"
            "3. Paste the URL in the field below\n\n"
            "Example:\n"
            "http://localhost:8080/?code=4/0Ade...&scope=..."
        )

        ttk.Label(
            self.auth_window,
            text=instructions,
            wraplength=450,
            justify=tk.LEFT
        ).pack(pady=5)

        self.auth_code_entry = ttk.Entry(self.auth_window, width=60)
        self.auth_code_entry.pack(pady=10, padx=10)

        btn_frame = ttk.Frame(self.auth_window)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="Submit",
            command=self.process_auth_code,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.auth_window.destroy
        ).pack(side=tk.LEFT)

        # Check clipboard for URL
        try:
            clipboard_content = pyperclip.paste()
            if "http://localhost" in clipboard_content:
                self.auth_code_entry.insert(0, clipboard_content)
        except Exception as e:
            logging.warning(f"Could not access clipboard: {e}")

    def process_auth_code(self):
        """Process the authentication code"""
        redirect_response = self.auth_code_entry.get().strip()

        try:
            parsed = urlparse(redirect_response)
            auth_code = parse_qs(parsed.query)['code'][0]
        except (KeyError, IndexError):
            messagebox.showerror("Error", "Authorization code not found in URL")
            return

        self.status_var.set("Getting access token...")
        if hasattr(self, 'auth_window') and self.auth_window:
            self.auth_window.destroy()
        self.root.update()

        # Get token in a separate thread
        threading.Thread(
            target=self.get_access_token,
            args=(auth_code,),
            daemon=True
        ).start()

    def get_access_token(self, auth_code):
        """Get access token from auth code"""
        token_data = {
            'code': auth_code,
            'client_id': self.client_config["installed"]["client_id"],
            'client_secret': self.client_config["installed"]["client_secret"],
            'redirect_uri': self.client_config["installed"]["redirect_uris"][0],
            'grant_type': 'authorization_code'
        }

        try:
            response = requests.post(
                self.client_config["installed"]["token_uri"],
                data=token_data
            )

            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info['access_token']
                self.refresh_token = token_info.get('refresh_token')
                self.token_expiry = time.time() + token_info.get('expires_in', 3600)

                # Get user info
                self.user_info = self.get_user_info()

                # Update UI
                self.root.after(0, self.update_ui_after_login)

            else:
                error_msg = f"Error getting token: {response.status_code}\n"
                if response.status_code == 401:
                    error_msg += "Authentication issue. Please check your Client ID and Client Secret."
                else:
                    error_msg += response.text

                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.status_var.set("Token error"))

        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Server connection error:\n{str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Connection error"))

    def get_user_info(self):
        """Get current user info"""
        if not self.access_token:
            return {}

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers=headers
            )

            if response.status_code == 200:
                return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting user info: {e}")

        return {}

    def update_ui_after_login(self):
        """Update UI after successful login"""
        if self.user_info:
            user_text = f"User: {self.user_info.get('name', 'Unknown')} ({self.user_info.get('email', 'No email')})"
            self.user_label.config(text=user_text)

        self.connection_status.config(text="Connected", foreground="green")
        self.status_var.set("Successfully connected to Google Drive")
        messagebox.showinfo("Success", "Google authentication successful")

        # Enable UI elements
        self.upload_btn['state'] = tk.NORMAL
        self.back_btn['state'] = tk.NORMAL
        self.up_btn['state'] = tk.NORMAL

        # Load files list
        self.load_files_list()

    def upload_file(self):
        """Upload selected file to Google Drive"""
        if not self.access_token:
            messagebox.showerror("Error", "You must authenticate first")
            return

        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return

        # Start upload in a separate thread
        threading.Thread(
            target=self.do_upload,
            daemon=True
        ).start()

    def do_upload(self):
        """Perform the actual file upload"""
        file_name = os.path.basename(self.file_path)
        mime_type = 'application/octet-stream'

        try:
            import mimetypes
            mime_type = mimetypes.guess_type(self.file_path)[0] or mime_type
        except ImportError:
            pass

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        metadata = {
            'name': file_name,
            'mimeType': mime_type
        }

        # Set parent folder if specified
        if self.current_folder_id != "root":
            metadata['parents'] = [self.current_folder_id]

        self.root.after(0, lambda: self.status_var.set(f"Uploading {file_name}..."))
        self.root.after(0, lambda: self.progress.config(value=0))
        self.root.after(0, lambda: self.progress_label.config(text=f"Starting upload of {file_name}"))

        try:
            with open(self.file_path, 'rb') as file:
                files = {
                    'data': ('metadata', json.dumps(metadata), 'application/json'),
                    'file': (file_name, file, mime_type)
                }

                response = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers=headers,
                    files=files
                )

                if response.status_code == 200:
                    self.root.after(0, lambda: self.progress.config(value=100))
                    self.root.after(0, lambda: self.progress_label.config(text="Upload complete!"))
                    self.root.after(0, lambda: self.status_var.set("Upload successful"))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success",
                        f"File uploaded successfully!\nFile ID: {response.json().get('id')}"
                    ))
                    self.root.after(0, self.load_files_list)
                else:
                    self.root.after(0, lambda: self.status_var.set("Upload failed"))
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error",
                        f"Upload failed\nStatus: {response.status_code}\n{response.text}"
                    ))

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Upload error"))
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Upload failed:\n{str(e)}"
            ))

    def load_files_list(self):
        """Load list of files from Google Drive"""
        if not self.access_token:
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        params = {
            'pageSize': 100,
            'fields': "files(id,name,size,mimeType,modifiedTime,shared)",
            'q': f"'{self.current_folder_id}' in parents and trashed=false"
        }

        try:
            response = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                files = response.json().get('files', [])
                self.root.after(0, self.update_files_tree, files)
            else:
                self.root.after(0, lambda: self.status_var.set("Error loading files"))

        except Exception as e:
            logging.error(f"Error loading files list: {e}")
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))

    def update_files_tree(self, files):
        """Update the files tree with new data"""
        self.files_tree.delete(*self.files_tree.get_children())

        # Add folders first
        folders = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.folder']
        for folder in folders:
            self.files_tree.insert(
                '', tk.END,
                values=(
                    folder['name'],
                    "",
                    "Folder",
                    self.format_date(folder['modifiedTime']),
                    "Yes" if folder.get('shared', False) else "No",
                    folder['id']
                ),
                tags=('folder',)
            )

        # Then add files
        other_files = [f for f in files if f['mimeType'] != 'application/vnd.google-apps.folder']
        for file in other_files:
            self.files_tree.insert(
                '', tk.END,
                values=(
                    file['name'],
                    self.format_size(int(file.get('size', 0))),
                    file['mimeType'].split('/')[-1].title(),
                    self.format_date(file['modifiedTime']),
                    "Yes" if file.get('shared', False) else "No",
                    file['id']
                ),
                tags=('file',)
            )

        self.status_var.set(f"Loaded {len(files)} items")

    def on_tree_double_click(self, event):
        """Handle double click on tree item"""
        item = self.files_tree.selection()[0]
        self.open_selected_item()

    def navigate_to_folder(self, folder_id):
        """Navigate to a specific folder"""
        self.folder_stack.append(folder_id)
        self.current_folder_id = folder_id
        self.update_navigation_buttons()
        self.load_files_list()

    def navigate_back(self):
        """Navigate back in folder history"""
        if len(self.folder_stack) > 1:
            self.folder_stack.pop()
            self.current_folder_id = self.folder_stack[-1]
            self.update_navigation_buttons()
            self.load_files_list()

    def navigate_up(self):
        """Navigate to parent folder"""
        self.navigate_to_folder("root")

    def update_navigation_buttons(self):
        """Update navigation button states"""
        self.back_btn['state'] = tk.NORMAL if len(self.folder_stack) > 1 else tk.DISABLED

    def download_file(self):
        """Download selected file"""
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        item_id = self.files_tree.item(selected[0], 'values')[5]
        item_name = self.files_tree.item(selected[0], 'values')[0]

        save_path = filedialog.asksaveasfilename(
            title="Save File",
            initialfile=item_name,
            defaultextension=".*"
        )

        if not save_path:
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            with requests.get(
                    f"https://www.googleapis.com/drive/v3/files/{item_id}?alt=media",
                    headers=headers,
                    stream=True
            ) as response:

                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                percent = (downloaded / total_size) * 100
                                self.root.after(0, lambda: self.progress.config(value=percent))
                                self.root.after(0, lambda: self.progress_label.config(
                                    text=f"Downloading {item_name}: {self.format_size(downloaded)} of {self.format_size(total_size)}"
                                ))

                    self.root.after(0, lambda: messagebox.showinfo("Success", "File downloaded successfully"))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error",
                        f"Download failed: {response.status_code}\n{response.text}"
                    ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))

    def delete_file(self):
        """Delete selected file"""
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        item_id = self.files_tree.item(selected[0], 'values')[5]
        item_name = self.files_tree.item(selected[0], 'values')[0]

        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete '{item_name}'?"):
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            response = requests.delete(
                f"https://www.googleapis.com/drive/v3/files/{item_id}",
                headers=headers
            )

            if response.status_code == 204:
                self.root.after(0, lambda: messagebox.showinfo("Success", "File deleted successfully"))
                self.load_files_list()
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Delete failed: {response.status_code}\n{response.text}"
                ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Delete failed: {str(e)}"))

    def rename_file(self):
        """Rename selected file"""
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        item_id = self.files_tree.item(selected[0], 'values')[5]
        old_name = self.files_tree.item(selected[0], 'values')[0]

        new_name = simpledialog.askstring(
            "Rename File",
            "Enter new name:",
            initialvalue=old_name
        )

        if not new_name or new_name == old_name:
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        data = {
            'name': new_name
        }

        try:
            response = requests.patch(
                f"https://www.googleapis.com/drive/v3/files/{item_id}",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                self.root.after(0, lambda: messagebox.showinfo("Success", "File renamed successfully"))
                self.load_files_list()
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Rename failed: {response.status_code}\n{response.text}"
                ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Rename failed: {str(e)}"))

    def share_file(self):
        """Share selected file"""
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        item_id = self.files_tree.item(selected[0], 'values')[5]
        item_name = self.files_tree.item(selected[0], 'values')[0]

        share_type = simpledialog.askstring(
            "Share File",
            f"Share '{item_name}' with:\n"
            "1. Specific user (enter email)\n"
            "2. Anyone with link (enter 'public')\n"
            "3. Cancel (leave blank)"
        )

        if not share_type:
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        if share_type.lower() == 'public':
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
        else:
            permission = {
                'type': 'user',
                'role': 'reader',
                'emailAddress': share_type
            }

        try:
            response = requests.post(
                f"https://www.googleapis.com/drive/v3/files/{item_id}/permissions",
                headers=headers,
                json=permission
            )

            if response.status_code in (200, 204):
                self.root.after(0, lambda: messagebox.showinfo("Success", "Sharing settings updated"))
                self.load_files_list()
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Sharing failed: {response.status_code}\n{response.text}"
                ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Sharing failed: {str(e)}"))

    def copy_file_link(self):
        """Copy file link to clipboard"""
        selected = self.files_tree.selection()
        if not selected:
            return

        item_id = self.files_tree.item(selected[0], 'values')[5]
        file_link = f"https://drive.google.com/file/d/{item_id}/view"

        try:
            pyperclip.copy(file_link)
            self.root.after(0, lambda: messagebox.showinfo("Success", "File link copied to clipboard"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Could not copy to clipboard: {str(e)}"))

    def show_file_properties(self):
        """Show properties of selected file"""
        selected = self.files_tree.selection()
        if not selected:
            return

        item = self.files_tree.item(selected[0])
        values = item['values']

        prop_window = tk.Toplevel(self.root)
        prop_window.title("File Properties")
        prop_window.geometry("400x300")

        # Create property display
        prop_frame = ttk.Frame(prop_window, padding=10)
        prop_frame.pack(fill=tk.BOTH, expand=True)

        # Basic info
        ttk.Label(prop_frame, text="Name:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.E, pady=2)
        ttk.Label(prop_frame, text=values[0]).grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(prop_frame, text="Size:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.E, pady=2)
        ttk.Label(prop_frame, text=values[1]).grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(prop_frame, text="Type:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky=tk.E, pady=2)
        ttk.Label(prop_frame, text=values[2]).grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(prop_frame, text="Modified:", font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky=tk.E,
                                                                                     pady=2)
        ttk.Label(prop_frame, text=values[3]).grid(row=3, column=1, sticky=tk.W, pady=2)

        ttk.Label(prop_frame, text="Shared:", font=('Helvetica', 10, 'bold')).grid(row=4, column=0, sticky=tk.E, pady=2)
        ttk.Label(prop_frame, text=values[4]).grid(row=4, column=1, sticky=tk.W, pady=2)

        ttk.Label(prop_frame, text="ID:", font=('Helvetica', 10, 'bold')).grid(row=5, column=0, sticky=tk.E, pady=2)
        ttk.Label(prop_frame, text=values[5]).grid(row=5, column=1, sticky=tk.W, pady=2)

        # Close button
        ttk.Button(
            prop_window,
            text="Close",
            command=prop_window.destroy,
            style='Accent.TButton'
        ).pack(pady=10)

    def search_files(self):
        """Search for files in Drive"""
        query = self.search_entry.get().strip()
        if not query or not self.access_token:
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        params = {
            'pageSize': 100,
            'fields': "files(id,name,size,mimeType,modifiedTime,shared)",
            'q': f"name contains '{query}' and trashed=false"
        }

        try:
            response = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                files = response.json().get('files', [])
                self.update_files_tree(files)
                self.status_var.set(f"Found {len(files)} matching files")
            else:
                self.status_var.set("Search failed")

        except Exception as e:
            logging.error(f"Search error: {e}")
            self.status_var.set(f"Search error: {str(e)}")

    def save_settings(self):
        """Save application settings"""
        self.client_config["installed"]["client_id"] = self.client_id_entry.get()
        self.client_config["installed"]["client_secret"] = self.client_secret_entry.get()
        self.client_config["installed"]["redirect_uris"][0] = self.redirect_entry.get()

        # Save to config file
        try:
            with open('config.json', 'w') as f:
                json.dump(self.client_config, f)

            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")

    def load_settings(self):
        """Load application settings"""
        try:
            with open('config.json', 'r') as f:
                self.client_config = json.load(f)

            # Update UI
            self.client_id_entry.delete(0, tk.END)
            self.client_id_entry.insert(0, self.client_config["installed"]["client_id"])

            self.client_secret_entry.delete(0, tk.END)
            self.client_secret_entry.insert(0, self.client_config["installed"]["client_secret"])

            self.redirect_entry.delete(0, tk.END)
            self.redirect_entry.insert(0, self.client_config["installed"]["redirect_uris"][0])

            messagebox.showinfo("Success", "Settings loaded successfully")
        except FileNotFoundError:
            messagebox.showinfo("Info", "No saved settings found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load settings: {str(e)}")

    def test_connection(self):
        """Test connection to Google API"""
        self.start_auth()

    def quick_upload(self):
        """Quick upload without opening upload tab"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path = file_path
            self.upload_file()

    def new_upload(self):
        """Start a new upload session"""
        self.main_notebook.select(self.upload_tab)
        self.file_path = ""
        self.file_entry.delete(0, tk.END)
        self.file_info_label.config(text="No file selected")

    def open_local_folder(self):
        """Open local folder in file explorer"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            try:
                os.startfile(folder_path)
            except:
                messagebox.showerror("Error", "Could not open folder")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About SfileColud",
            "SfileColud Professional\n"
            "Version 2.0.0\n\n"
            "A powerful Google Drive management application\n\n"
            "© 2023 Your Company. All rights reserved."
        )

    @staticmethod
    def format_size(size_bytes):
        """Format file size in human-readable format"""
        if not size_bytes:
            return "0 B"

        size_bytes = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def format_date(date_str):
        """Format date string to more readable format"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str


if __name__ == "__main__":
    # Initialize logging
    logging.info("Starting SfileColud Professional")

    # Create and run application
    root = tk.Tk()

    # Set theme
    sv_ttk.set_theme("light")

    # Create application
    app = SfileColud(root)

    # Run main loop
    root.mainloop()
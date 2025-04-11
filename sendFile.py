import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import webbrowser
import json
import os
from urllib.parse import urlparse, parse_qs
import pyperclip  
class DriveUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("آپلودر گوگل درایو")
        self.root.geometry("500x400")
        
        # تنظیمات کلاینت
        self.CLIENT_ID = "182925562813-toa3tg2frd623803n6dbdtpuo1bkibds.apps.googleusercontent.com"
        self.CLIENT_SECRET = "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"
        self.REDIRECT_URI = "http://localhost:8080"
        self.SCOPE = "https://www.googleapis.com/auth/drive.file"
        
        self.access_token = None
        self.auth_window = None
        
        # ایجاد ویجت‌ها
        self.create_widgets()
    def test_drive_access(access_token):
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            "https://www.googleapis.com/drive/v3/about",
            headers=headers,
            params={'fields': 'storageQuota'})
        
        if response.status_code == 200:
            print("\n🔹 اتصال به Drive موفقیت‌آمیز بود")
            print(f"حجم استفاده شده: {response.json()['storageQuota']['usage']} بایت")
            return True
        else:
            print("\n🔴 خطا در دسترسی به Drive:")
            print(response.text)
            return False
    
    def create_widgets(self):
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان برنامه
        title_label = ttk.Label(
            main_frame, 
            text="برنامه آپلود فایل به گوگل درایو",
            font=("Tahoma", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # دکمه انتخاب فایل
        self.file_path = tk.StringVar()
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="فایل انتخاب شده:").pack(side=tk.RIGHT)
        ttk.Entry(file_frame, textvariable=self.file_path, width=40).pack(side=tk.RIGHT, padx=5)
        ttk.Button(
            file_frame, 
            text="انتخاب فایل", 
            command=self.select_file
        ).pack(side=tk.RIGHT)
        
        # دکمه احراز هویت
        ttk.Button(
            main_frame,
            text="اتصال به گوگل درایو",
            command=self.start_auth,
            style="Accent.TButton"
        ).pack(pady=15)
        
        # دکمه آپلود
        self.upload_btn = ttk.Button(
            main_frame,
            text="آپلود فایل",
            command=self.upload_file,
            state=tk.DISABLED
        )
        self.upload_btn.pack(pady=10)
        
        # نوار پیشرفت
        self.progress = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # وضعیت برنامه
        self.status_var = tk.StringVar()
        self.status_var.set("آماده به کار")
        ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            foreground="gray"
        ).pack(pady=5)
        
        # استایل‌های سفارشی
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#1a73e8")
    
    def select_file(self):
        """انتخاب فایل برای آپلود"""
        file_path = filedialog.askopenfilename(
            title="لطفا فایل مورد نظر را انتخاب کنید",
            filetypes=[("همه فایل‌ها", "*.*")]
        )
        
        if file_path:
            self.file_path.set(file_path)
            if self.access_token:
                self.upload_btn['state'] = tk.NORMAL
    
    def start_auth(self):
        """شروع فرآیند احراز هویت"""
        if not self.file_path.get():
            messagebox.showwarning("هشدار", "لطفا ابتدا یک فایل انتخاب کنید")
            return
            
        auth_url = (f"https://accounts.google.com/o/oauth2/auth?"
                   f"client_id={self.CLIENT_ID}&"
                   f"redirect_uri={self.REDIRECT_URI}&"
                   f"scope={self.SCOPE}&"
                   f"response_type=code&"
                   f"access_type=offline&"
                   f"prompt=consent")
        
        self.status_var.set("در حال باز کردن مرورگر برای احراز هویت...")
        webbrowser.open(auth_url)
        
        # پنجره برای دریافت کد احراز هویت
        self.show_auth_code_window()
    
    def show_auth_code_window(self):
        """نمایش پنجره دریافت کد احراز هویت"""
        if self.auth_window:
            self.auth_window.destroy()
            
        self.auth_window = tk.Toplevel(self.root)
        self.auth_window.title("کد احراز هویت")
        self.auth_window.geometry("500x200")
        
        ttk.Label(
            self.auth_window,
            text="پس از ورود به سیستم، به یک صفحه محلی هدایت می‌شوید.\n"
                 "لطفا آدرس کامل URL را از نوار آدرس مرورگر کپی کرده و اینجا وارد کنید:",
            wraplength=400,
            justify=tk.RIGHT
        ).pack(pady=10)
        
        self.auth_code_entry = ttk.Entry(self.auth_window, width=60)
        self.auth_code_entry.pack(pady=5)
        
        ttk.Button(
            self.auth_window,
            text="تایید",
            command=self.process_auth_code
        ).pack(pady=10)
        try:
            clipboard_content = pyperclip.paste()
            if "http://localhost" in clipboard_content:
                self.auth_code_entry.insert(0, clipboard_content)
        except:
            pass
    
    def process_auth_code(self):
        """پردازش کد احراز هویت و دریافت توکن"""
        redirect_response = self.auth_code_entry.get().strip()
        
        try:
            parsed = urlparse(redirect_response)
            auth_code = parse_qs(parsed.query)['code'][0]
        except (KeyError, IndexError):
            messagebox.showerror("خطا", "کد احراز هویت در URL یافت نشد")
            return
        
        self.status_var.set("در حال دریافت توکن دسترسی...")
        self.auth_window.destroy()
        self.root.update()
        
        # دریافت توکن دسترسی
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': auth_code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'redirect_uri': self.REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(token_url, data=data)
            if response.status_code != 200:
                messagebox.showerror("خطا", f"دریافت توکن دسترسی ناموفق بود:\n{response.text}")
                self.status_var.set("خطا در دریافت توکن")
                return
                
            self.access_token = response.json()['access_token']
            self.status_var.set("اتصال با موفقیت برقرار شد")
            self.upload_btn['state'] = tk.NORMAL
            messagebox.showinfo("موفقیت", "اتصال به گوگل درایو با موفقیت انجام شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ارتباط با سرور:\n{str(e)}")
            self.status_var.set("خطا در ارتباط")
    
    def upload_file(self):
        """آپلود فایل به گوگل درایو"""
        if not self.access_token:
            messagebox.showerror("خطا", "ابتدا باید به گوگل درایو متصل شوید")
            return
            
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("خطا", "لطفا یک فایل معتبر انتخاب کنید")
            return
        
        file_name = os.path.basename(file_path)
        mime_type = 'application/octet-stream'
        
        # تشخیص نوع MIME
        try:
            import mimetypes
            mime_type = mimetypes.guess_type(file_path)[0] or mime_type
        except ImportError:
            pass
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        metadata = {
            'name': file_name,
            'mimeType': mime_type
        }
        
        self.status_var.set(f"در حال آپلود {file_name}...")
        self.progress['value'] = 0
        self.root.update()
        
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'data': ('metadata', json.dumps(metadata), 'application/json'),
                    'file': (file_name, file, mime_type)
                }
                
                response = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers=headers,
                    files=files,
                    stream=True
                )
                
                if response.status_code == 200:
                    self.progress['value'] = 100
                    self.status_var.set("آپلود با موفقیت انجام شد")
                    messagebox.showinfo(
                        "موفقیت", 
                        f"فایل با موفقیت آپلود شد!\nشناسه فایل: {response.json().get('id')}"
                    )
                else:
                    self.status_var.set("خطا در آپلود")
                    messagebox.showerror(
                        "خطا", 
                        f"آپلود فایل ناموفق بود\nکد وضعیت: {response.status_code}\n{response.text}"
                    )
                    
        except Exception as e:
            self.status_var.set("خطا در آپلود")
            messagebox.showerror("خطا", f"خطا در آپلود فایل:\n{str(e)}")

# اجرای برنامه
if __name__ == "__main__":
    root = tk.Tk()
    app = DriveUploaderApp(root)
    root.mainloop()
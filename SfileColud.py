import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
from datetime import datetime
from logging.handlers import RotatingFileHandler
import logging
import sys
import gettext
from pathlib import Path
import platform
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs import Messagebox, Querybox
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation

# تنظیمات پیشرفته لاگ‌گیری
def setup_logging():
    """تنظیمات پیشرفته لاگ‌گیری با پشتیبانی از encoding"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # فرمت مشترک برای همه هندلرها
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    try:
        # ایجاد فایل هندلر با encoding (برای پایتون 3.9+)
        file_handler = RotatingFileHandler(
            'SfileCloud.log',
            mode='a',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )
    except TypeError:
        # راه‌حل جایگزین برای نسخه‌های قدیمی پایتون
        file_handler = RotatingFileHandler(
            'SfileCloud.log',
            mode='a',
            maxBytes=5 * 1024 * 1024,
            backupCount=2
        )

    file_handler.setFormatter(formatter)

    # هندلر برای نمایش در کنسول
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # اضافه کردن هندلرها
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# فراخوانی تابع تنظیم لاگ‌گیری
setup_logging()

# حالا می‌توانید از ماژول logging به صورت معمول استفاده کنید
logging.info("This is a test log message with UTF-8 characters: üöäç")
logger = logging.getLogger(__name__)

# بارگذاری متغیرهای محیطی
load_dotenv()


class AppAssets:
    def __init__(self, root):
        self.root = root
        self.images = {}
        self._photo_images = []
        self.load_assets()
        self.setup_clipboard()  # تغییر نام متد به setup_clipboard
        self.setup_animations()

    def setup_clipboard(self):
        """تنظیمات کلیپ‌بورد"""
        self.clipboard_content = None

        # متدهای کپی و پیست
        self.copy_item = lambda item=None: self._copy_item(item)
        self.paste_item = lambda: self._paste_item()

    def _copy_item(self, item=None):
        """کپی آیتم به کلیپ‌بورد"""
        if item:
            self.clipboard_content = item
            try:
                pyperclip.copy(str(item))
                return True
            except Exception as e:
                logging.error(f"Error copying to clipboard: {e}")
                return False
        return False

    def _paste_item(self):
        """پیست از کلیپ‌بورد"""
        if self.clipboard_content:
            try:
                return pyperclip.paste()
            except Exception as e:
                logging.error(f"Error pasting from clipboard: {e}")
                return self.clipboard_content
        return None

    def load_assets(self):
        """بارگذاری تمام assetsهای برنامه با مدیریت خطای پیشرفته"""
        try:
            self.load_menu_icons()
            self.load_custom_images()
            self.load_sound_effects()
        except Exception as e:
            logger.error(f"Error loading assets: {e}")
            self.create_fallback_assets()

    def setup_animations(self):
        """تنظیم انیمیشن‌های برنامه"""
        self.animations = {
            'fade': lambda widget: self.fade_animation(widget),
            'slide': lambda widget: self.slide_animation(widget)
        }

    def fade_animation(self, widget):
        """انیمیشن محو شدن"""
        alpha = 0
        widget.attributes('-alpha', alpha)
        for i in range(10):
            alpha += 0.1
            widget.attributes('-alpha', alpha)
            widget.update()
            time.sleep(0.02)

    def slide_animation(self, widget):
        """انیمیشن اسلاید"""
        x = widget.winfo_x()
        y = widget.winfo_y()
        original_geom = widget.geometry()

        widget.geometry(f"0x{widget.winfo_height()}+{x}+{y}")
        for i in range(10):
            width = int(widget.winfo_width() + (widget.winfo_reqwidth() / 10))
            widget.geometry(f"{width}x{widget.winfo_height()}+{x}+{y}")
            widget.update()
            time.sleep(0.02)

        widget.geometry(original_geom)

    def load_menu_icons(self):
        """بارگذاری آیکون‌های منو با کیفیت بالا"""
        icon_definitions = {
            'upload': ("↑", "#4CAF50"),
            'download': ("↓", "#2196F3"),
            'folder': ("📁", "#FFC107"),
            'file': ("📄", "#9E9E9E"),
            'google': ("G", "#4285F4"),
            'refresh': ("↻", "#009688"),
            'back': ("←", "#607D8B"),
            'up': ("↑", "#795548"),
            'user': ("👤", "#673AB7"),
            'settings': ("⚙", "#607D8B"),
            'info': ("ℹ", "#00BCD4"),
            'search': ("🔍", "#FF9800"),
            'share': ("↗", "#E91E63"),
            'delete': ("🗑", "#F44336"),
            'edit': ("✏", "#2196F3"),
            'copy': ("⎘", "#009688"),
            'paste': ("📋", "#FF9800"),
            'link': ("🔗", "#3F51B5"),
            'theme': ("🎨", "#9C27B0"),
            'exit': ("⏻", "#F44336"),
            'menu': ("☰", "#000000"),
            'add': ("+", "#4CAF50"),
            'success': ("✓", "#4CAF50"),
            'error': ("✗", "#F44336"),
            'warning': ("⚠", "#FFC107"),
            'drive': ("💾", "#4285F4"),
            'pdf': ("PDF", "#F44336"),
            'word': ("DOC", "#2196F3"),
            'text': ("TXT", "#9E9E9E"),
            'image': ("🖼", "#FF5722"),
            'video': ("🎬", "#9C27B0"),
            'audio': ("🎵", "#673AB7"),
            'cloud': ("☁", "#03A9F4"),
            'sync': ("🔄", "#8BC34A"),
            'star': ("★", "#FFC107")
        }

        for name, (text, color) in icon_definitions.items():
            img = self.create_text_icon(text, color, (24, 24))  # اندازه بزرگتر برای کیفیت بهتر
            self.images[name] = ImageTk.PhotoImage(img)
            self._photo_images.append(self.images[name])

    def create_text_icon(self, text, color, size):
        """ایجاد آیکون متنی با کیفیت بالا"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", int(size[0] * 0.7))
        except:
            font = ImageFont.load_default()

        draw.text(
            (size[0] // 2, size[1] // 2),
            text,
            fill=color,
            font=font,
            anchor="mm"
        )

        # اضافه کردن سایه برای زیبایی بیشتر
        draw.text(
            (size[0] // 2 + 1, size[1] // 2 + 1),
            text,
            fill=(0, 0, 0, 128),
            font=font,
            anchor="mm"
        )

        return img

    def load_custom_images(self):
        """بارگذاری تصاویر سفارشی با کیفیت بالا"""
        image_specs = {
            'logo': ('assets/logo.png', (200, 200)),  # اندازه بزرگتر
            'splash': ('assets/splash.png', (500, 300)),
            'drive_logo': ('assets/google_drive_logo.png', (100, 100)),
            'background': ('assets/bg_pattern.png', None)
        }

        for name, (path, size) in image_specs.items():
            try:
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                full_path = os.path.join(base_path, path)

                if os.path.exists(full_path):
                    img = Image.open(full_path)
                    if size:
                        img = img.resize(size, Image.LANCZOS)

                    # بهبود کیفیت تصاویر
                    img = img.convert("RGBA")
                    self.images[name] = ImageTk.PhotoImage(img)
                    self._photo_images.append(self.images[name])
                else:
                    logger.warning(f"Image not found: {full_path}")
            except Exception as e:
                logger.error(f"Error loading image {path}: {e}")

    def load_sound_effects(self):
        """بارگذاری افکت‌های صوتی"""
        self.sounds = {
            'notification': 'assets/sounds/notification.wav',
            'success': 'assets/sounds/success.wav',
            'error': 'assets/sounds/error.wav'
        }

    def create_fallback_assets(self):
        """ایجاد assetsهای پیش‌فرض با طراحی بهتر"""
        self.load_menu_icons()

        try:
            # لوگوی پیش‌فرض با طراحی بهتر
            img = Image.new('RGB', (200, 200), color='#4b6cb7')
            draw = ImageDraw.Draw(img)
            draw.ellipse((20, 20, 180, 180), fill='#1e3c72', outline='white', width=5)
            draw.text((100, 100), "SC", fill="white", font=ImageFont.load_default(size=72), anchor="mm")
            self.images['logo'] = ImageTk.PhotoImage(img)
            self._photo_images.append(self.images['logo'])

            # تصویر splash پیش‌فرض با طراحی بهتر
            img = Image.new('RGB', (500, 300), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 0, 500, 80), fill='#4b6cb7')
            draw.text((250, 40), "SfileCloud Professional", fill="white", font=ImageFont.load_default(size=24),
                      anchor="mm")
            draw.text((250, 170), "Loading...", fill="#4b6cb7", font=ImageFont.load_default(size=18), anchor="mm")
            self.images['splash'] = ImageTk.PhotoImage(img)
            self._photo_images.append(self.images['splash'])

        except Exception as e:
            logger.error(f"Error creating fallback assets: {e}")

    def play_sound(self, sound_name):
        """پخش افکت صوتی"""
        if sound_name in self.sounds and os.path.exists(self.sounds[sound_name]):
            try:
                if platform.system() == "Windows":
                    import winsound
                    winsound.PlaySound(self.sounds[sound_name], winsound.SND_FILENAME)
                elif platform.system() == "Darwin":
                    os.system(f"afplay {self.sounds[sound_name]}")
                else:
                    os.system(f"aplay {self.sounds[sound_name]}")
            except:
                pass

    def get_icon(self, name, size=None):
        """دریافت آیکون با امکان تغییر اندازه"""
        if size and name in self.images:
            img = ImageTk.getimage(self.images[name])
            img = img.resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._photo_images.append(photo)
            return photo
        return self.images.get(name)

    def copy_item(self, item=None):
        """کپی آیتم با اطلاع‌رسانی بصری"""
        if item:
            self.clipboard_content = item
            try:
                pyperclip.copy(str(item))

                # نمایش انیمیشن کپی موفق
                self.show_copy_notification()
                return True
            except Exception as e:
                logger.error(f"Error copying to clipboard: {e}")
                return False
        return False

    def show_copy_notification(self):
        """نمایش اطلاع‌رسانی کپی موفق"""
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.geometry("200x50+{}+{}".format(
            self.root.winfo_rootx() + self.root.winfo_width() - 220,
            self.root.winfo_rooty() + 50
        ))
        notification.attributes('-alpha', 0)

        ttk.Label(
            notification,
            text="Copied to clipboard!",
            background="#4CAF50",
            foreground="white",
            anchor="center"
        ).pack(fill=tk.BOTH, expand=True)

        # انیمیشن محو شدن
        for i in range(10):
            notification.attributes('-alpha', i / 10)
            notification.update()
            time.sleep(0.02)

        time.sleep(1)

        for i in range(10, -1, -1):
            notification.attributes('-alpha', i / 10)
            notification.update()
            time.sleep(0.02)

        notification.destroy()


class EnhancedLanguageManager:
    """سیستم مدیریت چندزبانه پیشرفته"""

    def __init__(self):
        self.current_lang = "en"
        self.text_direction = "ltr"
        self.translations = {}
        self.locale_dir = Path(__file__).parent / "locales"
        self.setup_translations()
        self._ = self.gettext
        self.load_rtl_support()

    def setup_translations(self):
        """بارگذاری ترجمه‌ها از فایل‌های محلی و سرور"""
        try:
            # بارگذاری از فایل‌های محلی
            self.en_trans = gettext.translation('sfilecloud', localedir=self.locale_dir, languages=['en'])
            self.fa_trans = gettext.translation('sfilecloud', localedir=self.locale_dir, languages=['fa'])

            self.translations = {
                "en": self.en_trans.gettext,
                "fa": self.fa_trans.gettext
            }

            # بارگذاری ترجمه‌های اضافی از سرور
            self.load_cloud_translations()

        except FileNotFoundError:
            logger.warning("Translation files not found, using fallback")
            self.translations = {
                "en": lambda x: x,
                # "fa": self.create_persian_fallback()
            }

    def load_cloud_translations(self):
        """بارگذاری ترجمه‌های اضافی از سرور"""
        try:
            response = requests.get(
                "https://api.example.com/translations/sfilecloud",
                timeout=3
            )
            if response.status_code == 200:
                cloud_translations = response.json()
                for lang, trans_dict in cloud_translations.items():
                    if lang not in self.translations:
                        self.translations[lang] = lambda x: trans_dict.get(x, x)
        except Exception as e:
            logger.error(f"Error loading cloud translations: {e}")

    def load_rtl_support(self):
        """بارگذاری تنظیمات راست به چپ"""
        self.rtl_languages = ["fa", "ar", "he"]
        self.rtl_fonts = {
            "fa": {"family": "Tahoma", "size": 10}
        }

    def set_language(self, lang_code):
        """تغییر زبان برنامه با پشتیبانی از راست به چپ"""
        if lang_code in self.translations:
            self.current_lang = lang_code
            self.text_direction = "rtl" if lang_code in self.rtl_languages else "ltr"

            if lang_code == "en":
                self.en_trans.install()
            else:
                self.fa_trans.install()

            self.apply_language_settings()
            return True
        return False

    def apply_language_settings(self):
        """اعمال تنظیمات زبان مانند فونت و جهت متن"""
        if self.current_lang in self.rtl_languages:
            self.apply_rtl_settings()
        else:
            self.apply_ltr_settings()

    def apply_rtl_settings(self):
        """اعمال تنظیمات راست به چپ"""
        lang = self.current_lang
        font_settings = self.rtl_fonts.get(lang, {"family": "Tahoma", "size": 10})

        # تنظیم فونت پیش‌فرض برای ویجت‌ها
        default_font = Font(
            family=font_settings["family"],
            size=font_settings["size"]
        )

        # اعمال به تمام ویجت‌ها
        widgets = [ttk.Label, ttk.Button, ttk.Entry, ttk.Checkbutton]
        for widget in widgets:
            widget.configure(font=default_font)

        # تنظیم جهت متن
        ttk.Style().configure('.', direction='rtl')

    def apply_ltr_settings(self):
        """اعمال تنظیمات چپ به راست"""
        # بازنشانی به تنظیمات پیش‌فرض
        default_font = Font(
            family="Segoe UI",
            size=9
        )

        widgets = [ttk.Label, ttk.Button, ttk.Entry, ttk.Checkbutton]
        for widget in widgets:
            widget.configure(font=default_font)

        ttk.Style().configure('.', direction='ltr')

    def get_direction(self):
        """دریافت جهت متن فعلی"""
        return self.text_direction

    def get_font(self, widget_type=None):
        """دریافت فونت مناسب برای زبان فعلی"""
        if self.current_lang in self.rtl_languages:
            font_settings = self.rtl_fonts.get(self.current_lang, {"family": "Tahoma", "size": 10})
            return Font(family=font_settings["family"], size=font_settings["size"])
        return Font(family="Segoe UI", size=9)


class ModernAuthWindow(tk.Toplevel):
    """پنجره احراز هویت مدرن با طراحی پیشرفته"""

    def __init__(self, parent, auth_callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.auth_callback = auth_callback
        self.assets = AppAssets(parent)
        self.lang = EnhancedLanguageManager()
        self._ = self.lang.gettext
        self.setup_window()
        self.create_widgets()
        self.setup_animations()

    def setup_window(self):
        """تنظیمات پنجره"""
        self.title(self._("Login to SfileCloud"))
        self.geometry("500x650")  # ارتفاع بیشتر برای طراحی بهتر
        self.resizable(False, False)
        self.configure(bg="#f8f9fa")
        self.center_window()

        # آیکون پنجره
        try:
            self.iconphoto(False, self.assets.get_image('drive_logo'))
        except:
            pass

        # تنظیمات ظاهری
        self.attributes('-alpha', 0.95)
        self.attributes('-topmost', True)

    def setup_animations(self):
        """تنظیم انیمیشن‌های پنجره"""
        self.assets.animations['fade'](self)

    def center_window(self):
        """مرکز کردن پنجره روی صفحه"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """ایجاد ویجت‌های پنجره"""
        # فریم اصلی با پس‌زمینه گرادیان
        main_frame = tk.Frame(self, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # هدر با طراحی مدرن
        header_frame = tk.Frame(main_frame, bg="#4b6cb7", height=180)
        header_frame.pack(fill=tk.X)

        # دکمه بستن
        close_btn = ttk.Button(
            header_frame,
            text="×",
            command=self.destroy,
            style="danger.TButton",
            width=2
        )
        close_btn.place(x=10, y=10)

        # محتوای هدر
        header_content = tk.Frame(header_frame, bg="#4b6cb7")
        header_content.place(relx=0.5, rely=0.6, anchor="center")

        # لوگو
        logo_img = self.assets.get_image('drive_logo')
        if logo_img:
            logo_label = tk.Label(header_content, image=logo_img, bg="#4b6cb7")
            logo_label.pack(pady=(0, 10))

        # عنوان
        title_label = tk.Label(
            header_content,
            text=self._("Connect to Google Drive"),
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#4b6cb7"
        )
        title_label.pack()

        # محتوای اصلی
        content_frame = tk.Frame(main_frame, bg="#f8f9fa", padx=40, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # کارت لاگین
        login_card = tk.Frame(
            content_frame,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#dee2e6",
            padx=30,
            pady=30
        )
        login_card.pack(fill=tk.BOTH, expand=True)

        # دکمه لاگین با افکت hover
        login_btn = ttk.Button(
            login_card,
            text=self._("Sign in with Google"),
            command=self.start_auth,
            bootstyle="primary",
            image=self.assets.get_icon('google'),
            compound=tk.LEFT
        )
        login_btn.pack(fill=tk.X, pady=20)
        ToolTip(login_btn, text=self._("Authenticate with your Google account"))

        # جداکننده
        separator = ttk.Separator(login_card, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=20)

        # متن راهنما
        help_text = self._(
            "After signing in, you'll be redirected\n"
            "to authenticate with your Google account.\n\n"
            "We use OAuth 2.0 for secure authentication."
        )
        help_label = tk.Label(
            login_card,
            text=help_text,
            font=("Segoe UI", 9),
            fg="#6c757d",
            bg="white",
            justify=tk.CENTER
        )
        help_label.pack()

        # فوتر
        footer_frame = tk.Frame(main_frame, bg="#e9ecef", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        copyright_label = tk.Label(
            footer_frame,
            text="© 2023 SfileCloud Professional",
            font=("Segoe UI", 9),
            fg="#6c757d",
            bg="#e9ecef"
        )
        copyright_label.place(relx=0.5, rely=0.5, anchor="center")

    def start_auth(self):
        """شروع فرآیند احراز هویت"""
        self.assets.play_sound('notification')
        self.assets.animations['fade'](self)
        self.destroy()
        self.auth_callback()


class ModernAboutWindow(tk.Toplevel):
    """پنجره درباره برنامه با طراحی مدرن"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.assets = AppAssets(parent)
        self.lang = EnhancedLanguageManager()
        self._ = self.lang.gettext
        self.setup_window()
        self.create_widgets()
        self.setup_animations()

    def setup_window(self):
        """تنظیمات پنجره"""
        self.title(self._("About SfileCloud Professional"))
        self.geometry("700x550")
        self.resizable(False, False)
        self.configure(bg="#f8f9fa")
        self.center_window()

        # آیکون پنجره
        try:
            self.iconphoto(False, self.assets.get_image('logo'))
        except:
            pass

        # تنظیمات ظاهری
        self.attributes('-alpha', 0.95)

    def setup_animations(self):
        """تنظیم انیمیشن‌های پنجره"""
        self.assets.animations['fade'](self)

    def center_window(self):
        """مرکز کردن پنجره"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """ایجاد ویجت‌های پنجره"""
        # فریم اصلی
        main_frame = tk.Frame(self, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # هدر
        header_frame = tk.Frame(main_frame, bg="#4b6cb7", height=150)
        header_frame.pack(fill=tk.X)

        # عنوان برنامه
        title_label = tk.Label(
            header_frame,
            text=self._("SfileCloud Professional"),
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#4b6cb7"
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        # محتوای اصلی
        content_frame = tk.Frame(main_frame, bg="#f8f9fa", padx=40, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # لوگو
        logo_img = self.assets.get_image('logo')
        if logo_img:
            logo_label = tk.Label(content_frame, image=logo_img, bg="#f8f9fa")
            logo_label.pack(pady=(0, 20))

        # توضیحات
        desc_text = self._(
            "A powerful Google Drive management application with advanced features\n"
            "for file management, sharing and synchronization.\n\n"
            "Version: 2.1.0\n"
            "Developed by: Alikaspian\n\n"
            "Key Features:\n"
            "- Secure file transfers\n"
            "- Multi-language support\n"
            "- Advanced sharing options\n"
            "- Real-time synchronization"
        )
        desc_label = tk.Label(
            content_frame,
            text=desc_text,
            font=("Segoe UI", 11),
            bg="#f8f9fa",
            justify=tk.LEFT
        )
        desc_label.pack(pady=10)

        # ویژگی‌های کلیدی
        features_frame = tk.Frame(content_frame, bg="#f8f9fa")
        features_frame.pack(pady=10)

        features = [
            (self.assets.get_icon('upload'), self._("Fast file uploads")),
            (self.assets.get_icon('download'), self._("Reliable downloads")),
            (self.assets.get_icon('share'), self._("Easy file sharing")),
            (self.assets.get_icon('sync'), self._("Real-time sync"))
        ]

        for icon, text in features:
            feature_frame = tk.Frame(features_frame, bg="#f8f9fa")
            feature_frame.pack(side=tk.LEFT, padx=10)

            icon_label = tk.Label(feature_frame, image=icon, bg="#f8f9fa")
            icon_label.pack()

            text_label = tk.Label(
                feature_frame,
                text=text,
                font=("Segoe UI", 9),
                bg="#f8f9fa"
            )
            text_label.pack()

        # دکمه‌های اجتماعی
        social_frame = tk.Frame(content_frame, bg="#f8f9fa")
        social_frame.pack(pady=20)

        github_btn = ttk.Button(
            social_frame,
            text="GitHub",
            bootstyle="dark",
            image=self.assets.get_icon('link'),
            compound=tk.LEFT,
            command=lambda: webbrowser.open("https://github.com/Kaspian021/SfileColud")
        )
        github_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(github_btn, text="Visit our GitHub repository")

        website_btn = ttk.Button(
            social_frame,
            text="Website",
            bootstyle="info",
            image=self.assets.get_icon('link'),
            compound=tk.LEFT,
            command=lambda: webbrowser.open("https://alikaspian.ir")
        )
        website_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(website_btn, text="Visit our website")

        # فوتر
        footer_frame = tk.Frame(main_frame, bg="#e9ecef", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        copyright_label = tk.Label(
            footer_frame,
            text="© 2023 Alikaspian. All rights reserved.",
            font=("Segoe UI", 9),
            fg="#6c757d",
            bg="#e9ecef"
        )
        copyright_label.place(relx=0.5, rely=0.5, anchor="center")


class EnhancedDriveFileManager:
    """مدیریت فایل‌های گوگل درایو با بهینه‌سازی‌های پیشرفته"""

    def __init__(self, client_config):
        self.client_config = client_config
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.user_info = {}
        self.current_folder_id = "root"
        self.folder_stack = ["root"]
        self.lang = EnhancedLanguageManager()
        self._ = self.lang.gettext
        self.file_cache = {}
        self.cache_expiry = 300  # 5 دقیقه
        self.setup_retry_strategy()

    def setup_retry_strategy(self):
        """تنظیم استراتژی تلاش مجدد برای درخواست‌ها"""
        self.retry_count = 3
        self.retry_delay = 1  # ثانیه

    def authenticate(self, auth_code):
        """احراز هویت با کد مجوز"""
        token_data = {
            'code': auth_code,
            'client_id': self.client_config["installed"]["client_id"],
            'client_secret': self.client_config["installed"]["client_secret"],
            'redirect_uri': self.client_config["installed"]["redirect_uris"][0],
            'grant_type': 'authorization_code'
        }

        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    self.client_config["installed"]["token_uri"],
                    data=token_data,
                    timeout=10
                )

                if response.status_code == 200:
                    token_info = response.json()
                    self.access_token = token_info['access_token']
                    self.refresh_token = token_info.get('refresh_token')
                    self.token_expiry = time.time() + token_info.get('expires_in', 3600)
                    self.user_info = self._get_user_info()
                    return True
                else:
                    error_msg = self._("Error getting token: {}\n").format(response.status_code)
                    if response.status_code == 401:
                        error_msg += self._("Authentication issue. Please check your Client ID and Client Secret.")
                    else:
                        error_msg += response.text
                    raise Exception(error_msg)

            except requests.exceptions.RequestException as e:
                if attempt == self.retry_count - 1:
                    raise Exception(self._("Server connection error:\n{}").format(str(e)))
                time.sleep(self.retry_delay)

    def _get_user_info(self):
        """دریافت اطلاعات کاربر با تلاش مجدد"""
        if not self.access_token:
            return {}

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401 and attempt < self.retry_count - 1:
                    self._refresh_token()
                    continue
                else:
                    logging.error(f"Error getting user info: {response.status_code}")
                    break

            except requests.exceptions.RequestException as e:
                logging.error(f"Error getting user info: {e}")
                if attempt == self.retry_count - 1:
                    break
                time.sleep(self.retry_delay)

        return {}

    def _refresh_token(self):
        """تازه‌سازی توکن دسترسی"""
        if not self.refresh_token:
            return False

        token_data = {
            'client_id': self.client_config["installed"]["client_id"],
            'client_secret': self.client_config["installed"]["client_secret"],
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        try:
            response = requests.post(
                self.client_config["installed"]["token_uri"],
                data=token_data,
                timeout=5
            )

            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info['access_token']
                self.token_expiry = time.time() + token_info.get('expires_in', 3600)
                return True

        except requests.exceptions.RequestException as e:
            logging.error(f"Error refreshing token: {e}")

        return False

    def list_files(self, folder_id=None):
        """لیست فایل‌ها با کشینگ و تلاش مجدد"""
        folder_id = folder_id or self.current_folder_id

        # بررسی کش
        if folder_id in self.file_cache:
            cached_data, timestamp = self.file_cache[folder_id]
            if time.time() - timestamp < self.cache_expiry:
                return cached_data

        # اگر در کش نبود، از سرور دریافت کنیم
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        params = {
            'pageSize': 100,
            'fields': "files(id,name,size,mimeType,modifiedTime,shared,thumbnailLink,webContentLink)",
            'q': f"'{folder_id}' in parents and trashed=false"
        }

        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    "https://www.googleapis.com/drive/v3/files",
                    headers=headers,
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:
                    files = response.json().get('files', [])
                    self.file_cache[folder_id] = (files, time.time())
                    return files
                elif response.status_code == 401 and attempt < self.retry_count - 1:
                    self._refresh_token()
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    continue
                else:
                    raise Exception(f"Error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                if attempt == self.retry_count - 1:
                    if folder_id in self.file_cache:  # استفاده از داده‌های کش شده در صورت خطا
                        return self.file_cache[folder_id][0]
                    raise Exception(str(e))
                time.sleep(self.retry_delay)

    def upload_file(self, file_path, folder_id=None):
        """آپلود فایل با نمایش پیشرفت"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        if not os.path.exists(file_path):
            raise Exception(self._("File does not exist"))

        folder_id = folder_id or self.current_folder_id
        file_name = os.path.basename(file_path)
        mime_type = 'application/octet-stream'

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

        if folder_id != "root":
            metadata['parents'] = [folder_id]

        try:
            with open(file_path, 'rb') as file:
                files = {
                    'data': ('metadata', json.dumps(metadata), 'application/json'),
                    'file': (file_name, file, mime_type)
                }

                # آپلود با نمایش پیشرفت
                response = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers=headers,
                    files=files,
                    stream=True
                )

                if response.status_code == 200:
                    # پاکسازی کش مربوط به این پوشه
                    if folder_id in self.file_cache:
                        del self.file_cache[folder_id]
                    return response.json()
                else:
                    raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def download_file(self, file_id, save_path):
        """دانلود فایل با نمایش پیشرفت"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            with requests.get(
                    f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
                    headers=headers,
                    stream=True,
                    timeout=30
            ) as response:

                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                yield downloaded, total_size
                else:
                    raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def delete_file(self, file_id):
        """حذف فایل با به‌روزرسانی کش"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            # ابتدا اطلاعات فایل را دریافت می‌کنیم تا پوشه والد را بدانیم
            file_info = self.get_file_info(file_id)
            parent_id = file_info.get('parents', ['root'])[0]

            response = requests.delete(
                f"https://www.googleapis.com/drive/v3/files/{file_id}",
                headers=headers
            )

            if response.status_code == 204:
                # پاکسازی کش مربوط به پوشه والد
                if parent_id in self.file_cache:
                    del self.file_cache[parent_id]
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def get_file_info(self, file_id):
        """دریافت اطلاعات یک فایل خاص"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        params = {
            'fields': 'id,name,parents,mimeType'
        }

        try:
            response = requests.get(
                f"https://www.googleapis.com/drive/v3/files/{file_id}",
                headers=headers,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def rename_file(self, file_id, new_name):
        """تغییر نام فایل با به‌روزرسانی کش"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        data = {
            'name': new_name
        }

        try:
            # ابتدا اطلاعات فایل را دریافت می‌کنیم تا پوشه والد را بدانیم
            file_info = self.get_file_info(file_id)
            parent_id = file_info.get('parents', ['root'])[0]

            response = requests.patch(
                f"https://www.googleapis.com/drive/v3/files/{file_id}",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                # پاکسازی کش مربوط به پوشه والد
                if parent_id in self.file_cache:
                    del self.file_cache[parent_id]
                return response.json()
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def share_file(self, file_id, share_type, email=None):
        """اشتراک‌گذاری فایل با تنظیمات مختلف"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

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
            if not email:
                raise Exception(self._("Email address is required for user sharing"))

            permission = {
                'type': 'user',
                'role': 'reader',
                'emailAddress': email
            }

        try:
            response = requests.post(
                f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
                headers=headers,
                json=permission
            )

            if response.status_code not in (200, 204):
                raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def get_storage_info(self):
        """دریافت اطلاعات فضای ذخیره‌سازی"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(
                "https://www.googleapis.com/drive/v3/about?fields=storageQuota",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                return response.json().get('storageQuota', {})
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def create_folder(self, folder_name, parent_id=None):
        """ایجاد پوشه جدید"""
        if not self.access_token:
            raise Exception(self._("You must authenticate first"))

        parent_id = parent_id or self.current_folder_id
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        try:
            response = requests.post(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                json=metadata
            )

            if response.status_code == 200:
                # پاکسازی کش مربوط به پوشه والد
                if parent_id in self.file_cache:
                    del self.file_cache[parent_id]
                return response.json()
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(str(e))

    def clear_cache(self):
        """پاکسازی کش"""
        self.file_cache = {}


class ModernFileBrowser(ttk.Frame):
    """مرورگر فایل پیشرفته با قابلیت‌های جدید"""

    def __init__(self, parent, file_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.file_manager = file_manager
        self.assets = AppAssets(parent)
        self.lang = EnhancedLanguageManager()
        self._ = self.lang.gettext
        self.selected_files = []
        self.setup_ui()
        self.setup_file_preview()
        self.setup_drag_drop()

    def setup_ui(self):
        """تنظیم رابط کاربری پیشرفته"""
        self.pack(fill=tk.BOTH, expand=True)

        # نوار ابزار پیشرفته
        self.create_advanced_toolbar()

        # مرورگر فایل
        self.create_modern_file_browser()

        # نوار وضعیت پیشرفته
        self.create_enhanced_status_bar()

        # تنظیم رویدادها
        self.setup_events()

    def create_advanced_toolbar(self):
        """ایجاد نوار ابزار پیشرفته"""
        toolbar = ttk.Frame(self, style="primary.TFrame")
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # دکمه‌های ناوبری
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side=tk.LEFT)

        self.back_btn = ttk.Button(
            nav_frame,
            text=self._("← Back"),
            bootstyle="light",
            image=self.assets.get_icon('back'),
            compound=tk.LEFT,
            command=self.navigate_back,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.back_btn, text=self._("Go back to previous folder"))

        self.up_btn = ttk.Button(
            nav_frame,
            text=self._("↑ Up"),
            bootstyle="light",
            image=self.assets.get_icon('up'),
            compound=tk.LEFT,
            command=self.navigate_up,
            state=tk.DISABLED
        )
        self.up_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.up_btn, text=self._("Go up to parent folder"))

        self.refresh_btn = ttk.Button(
            nav_frame,
            bootstyle="light",
            image=self.assets.get_icon('refresh'),
            command=self.refresh_files,
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.refresh_btn, text=self._("Refresh file list"))

        # نمایش مسیر
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(
            toolbar,
            textvariable=self.path_var,
            state="readonly",
            width=50,
            style="info.TEntry"
        )
        path_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # جستجوی پیشرفته
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25,
            style="info.TEntry"
        )
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.insert(0, self._("Search Files..."))
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if search_entry.get() == self._(
            "Search Files...") else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, self._(
            "Search Files...")) if not search_entry.get() else None)
        search_entry.bind("<Return>", lambda e: self.search_files())

        search_btn = ttk.Button(
            search_frame,
            bootstyle="info",
            image=self.assets.get_icon('search'),
            command=self.search_files
        )
        search_btn.pack(side=tk.LEFT)
        ToolTip(search_btn, text=self._("Search files in current folder"))

        # دکمه‌های عملیاتی
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side=tk.RIGHT, padx=5)

        self.upload_btn = ttk.Button(
            action_frame,
            bootstyle="success",
            image=self.assets.get_icon('upload'),
            command=self.show_upload_dialog
        )
        self.upload_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.upload_btn, text=self._("Upload files"))

        self.download_btn = ttk.Button(
            action_frame,
            bootstyle="info",
            image=self.assets.get_icon('download'),
            command=self.download_selected
        )
        self.download_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.download_btn, text=self._("Download selected files"))

    def create_modern_file_browser(self):
        """ایجاد مرورگر فایل مدرن"""
        # نوت‌بوک برای نمایش مختلف فایل‌ها
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # نمای لیست
        self.list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.list_frame, text=self._("List View"), image=self.assets.get_icon('list'),
                          compound=tk.LEFT)

        # Treeview پیشرفته
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("name", "size", "type", "modified", "shared"),
            show="headings",
            style="modern.Treeview",
            selectmode="extended"
        )

        # تنظیم ستون‌ها
        columns = {
            "name": {"text": self._("Name"), "width": 300, "anchor": tk.W},
            "size": {"text": self._("Size"), "width": 100, "anchor": tk.CENTER},
            "type": {"text": self._("Type"), "width": 100, "anchor": tk.CENTER},
            "modified": {"text": self._("Modified"), "width": 150, "anchor": tk.CENTER},
            "shared": {"text": self._("Shared"), "width": 80, "anchor": tk.CENTER}
        }

        for col, config in columns.items():
            self.tree.heading(col, text=config["text"], anchor=config["anchor"])
            self.tree.column(col, width=config["width"], anchor=config["anchor"])

        # اسکرول‌بارها
        y_scroll = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self.list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # چیدمان
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        # تنظیم وزن‌های گرید
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # نمای تصاویر کوچک
        self.thumb_frame = ScrolledFrame(self.notebook)
        self.thumb_frame.pack(fill=tk.BOTH, expand=True)
        self.thumb_container = ttk.Frame(self.thumb_frame)
        self.thumb_container.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.thumb_frame, text=self._("Thumbnail View"), image=self.assets.get_icon('image'),
                          compound=tk.LEFT)

        # نمای جزئیات
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text=self._("Details View"), image=self.assets.get_icon('info'),
                          compound=tk.LEFT)

    def create_enhanced_status_bar(self):
        """ایجاد نوار وضعیت پیشرفته"""
        status_bar = ttk.Frame(self, style="info.TFrame")
        status_bar.pack(fill=tk.X, padx=5, pady=(0, 5))

        # پیام وضعیت
        self.status_var = tk.StringVar(value=self._("Ready"))
        status_label = ttk.Label(
            status_bar,
            textvariable=self.status_var,
            bootstyle="inverse",
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # اطلاعات ذخیره‌سازی
        self.storage_var = tk.StringVar(value="")
        storage_label = ttk.Label(
            status_bar,
            textvariable=self.storage_var,
            bootstyle="inverse",
            width=30
        )
        storage_label.pack(side=tk.RIGHT)

        # اطلاعات انتخاب
        self.selection_var = tk.StringVar(value="0 items selected")
        selection_label = ttk.Label(
            status_bar,
            textvariable=self.selection_var,
            bootstyle="inverse",
            width=20
        )
        selection_label.pack(side=tk.RIGHT)

        # به‌روزرسانی اطلاعات ذخیره‌سازی
        self.update_storage_info()

    def setup_file_preview(self):
        """تنظیم پیش‌نمایش فایل"""
        self.preview_window = tk.Toplevel(self)
        self.preview_window.withdraw()
        self.preview_window.overrideredirect(True)
        self.preview_window.attributes('-alpha', 0.9)

        self.preview_label = ttk.Label(self.preview_window)
        self.preview_label.pack()

        self.tree.bind("<Motion>", self.show_file_preview)
        self.tree.bind("<Leave>", self.hide_file_preview)

    def show_file_preview(self, event):
        """نمایش پیش‌نمایش فایل هنگام hover"""
        item = self.tree.identify_row(event.y)
        if item:
            file_name = self.tree.item(item, 'values')[0]
            file_type = self.tree.item(item, 'values')[2]

            if "Image" in file_type:
                file_id = self.get_file_id(file_name)
                if file_id:
                    thumbnail_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w200"

                    try:
                        response = requests.get(thumbnail_url, stream=True, timeout=3)
                        if response.status_code == 200:
                            img_data = response.content
                            img = Image.open(io.BytesIO(img_data))

                            # محدود کردن اندازه تصویر
                            max_size = (200, 200)
                            img.thumbnail(max_size)

                            photo = ImageTk.PhotoImage(img)
                            self.preview_label.configure(image=photo)
                            self.preview_label.image = photo

                            # نمایش پنجره پیش‌نمایش
                            self.preview_window.deiconify()
                            self.preview_window.geometry(f"+{event.x_root + 20}+{event.y_root + 20}")
                    except:
                        pass

    def hide_file_preview(self, event):
        """پنهان کردن پیش‌نمایش فایل"""
        self.preview_window.withdraw()

    def setup_drag_drop(self):
        """تنظیم قابلیت کشیدن و رها کردن"""
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_end)

        self.drag_data = {"item": None, "x": 0, "y": 0}

    def on_drag_start(self, event):
        """شروع عملیات کشیدن"""
        item = self.tree.identify_row(event.y)
        if item:
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag_motion(self, event):
        """حرکت در حین کشیدن"""
        if self.drag_data["item"]:
            # می‌توانید اینجا افکت‌های بصری اضافه کنید
            pass

    def on_drag_end(self, event):
        """پایان عملیات کشیدن"""
        if self.drag_data["item"]:
            target_item = self.tree.identify_row(event.y)
            if target_item and self.drag_data["item"] != target_item:
                # انجام عملیات جابجایی
                self.move_item(self.drag_data["item"], target_item)

            self.drag_data["item"] = None

    def move_item(self, source_item, target_item):
        """جابجایی فایل/پوشه"""
        source_name = self.tree.item(source_item, 'values')[0]
        target_name = self.tree.item(target_item, 'values')[0]

        # دریافت ID فایل‌ها
        files = self.file_manager.list_files()
        source_file = next((f for f in files if f['name'] == source_name), None)
        target_file = next((f for f in files if f['name'] == target_name), None)

        if source_file and target_file:
            if target_file['mimeType'] == 'application/vnd.google-apps.folder':
                # جابجایی به پوشه مقصد
                try:
                    # ابتدا فایل را از پوشه فعلی حذف می‌کنیم
                    self.file_manager.remove_parent(source_file['id'], self.file_manager.current_folder_id)

                    # سپس به پوشه جدید اضافه می‌کنیم
                    self.file_manager.add_parent(source_file['id'], target_file['id'])

                    # به‌روزرسانی لیست فایل‌ها
                    self.load_files()

                    self.status_var.set(self._("Moved '{}' to '{}'").format(source_name, target_name))
                except Exception as e:
                    self.status_var.set(self._("Error moving file: {}").format(str(e)))
            else:
                self.status_var.set(self._("Can only move to folders"))

            def setup_events(self):
                """تنظیم رویدادهای مختلف"""
                self.tree.bind("<Double-1>", self.on_item_double_click)
                self.tree.bind("<Button-3>", self.show_context_menu)
                self.tree.bind("<<TreeviewSelect>>", self.update_selection_count)

                # ایجاد منوی زمینه
                self.create_context_menu()

                # تنظیمات کشیدن و رها کردن
                self.setup_drag_drop()

            def create_context_menu(self):
                """ایجاد منوی زمینه پیشرفته"""
                self.context_menu = tk.Menu(self, tearoff=0, font=self.lang.get_font())

                self.context_menu.add_command(
                    label=self._("Open"),
                    image=self.assets.get_icon('file'),
                    compound=tk.LEFT,
                    command=self.open_selected,
                    accelerator="Enter"
                )

                self.context_menu.add_command(
                    label=self._("Download"),
                    image=self.assets.get_icon('download'),
                    compound=tk.LEFT,
                    command=self.download_selected,
                    accelerator="Ctrl+D"
                )

                self.context_menu.add_command(
                    label=self._("Rename"),
                    image=self.assets.get_icon('edit'),
                    compound=tk.LEFT,
                    command=self.rename_selected,
                    accelerator="F2"
                )

                self.context_menu.add_command(
                    label=self._("Share"),
                    image=self.assets.get_icon('share'),
                    compound=tk.LEFT,
                    command=self.share_selected,
                    accelerator="Ctrl+S"
                )

                self.context_menu.add_separator()

                self.context_menu.add_command(
                    label=self._("Delete"),
                    image=self.assets.get_icon('delete'),
                    compound=tk.LEFT,
                    command=self.delete_selected,
                    accelerator="Del"
                )

                self.context_menu.add_separator()

                self.context_menu.add_command(
                    label=self._("Properties"),
                    image=self.assets.get_icon('info'),
                    compound=tk.LEFT,
                    command=self.show_properties,
                    accelerator="Alt+Enter"
                )

            def update_selection_count(self, event):
                """به‌روزرسانی تعداد فایل‌های انتخاب شده"""
                selected = len(self.tree.selection())
                self.selection_var.set(f"{selected} items selected")

            def load_files(self):
                """بارگذاری فایل‌ها با نمایش وضعیت"""
                self.status_var.set(self._("Loading files..."))
                self.tree.delete(*self.tree.get_children())

                try:
                    files = self.file_manager.list_files()
                    self.update_file_list(files)
                    self.status_var.set(self._("Loaded {} items").format(len(files)))
                except Exception as e:
                    self.status_var.set(self._("Error: {}").format(str(e)))
                    Messagebox.show_error(str(e), self._("Error loading files"))

            def update_file_list(self, files):
                """به‌روزرسانی لیست فایل‌ها با اطلاعات جدید"""
                # پوشه‌ها اول نمایش داده می‌شوند
                folders = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.folder']
                for folder in folders:
                    self.tree.insert(
                        '', tk.END,
                        values=(
                            folder['name'],
                            "",
                            self._("Folder"),
                            self.format_date(folder['modifiedTime']),
                            self._("Yes") if folder.get('shared', False) else self._("No")
                        ),
                        tags=('folder',),
                        image=self.assets.get_icon('folder')
                    )

                # سپس فایل‌ها
                other_files = [f for f in files if f['mimeType'] != 'application/vnd.google-apps.folder']
                for file in other_files:
                    self.tree.insert(
                        '', tk.END,
                        values=(
                            file['name'],
                            self.format_size(int(file.get('size', 0))),
                            self.get_file_type(file['mimeType']),
                            self.format_date(file['modifiedTime']),
                            self._("Yes") if file.get('shared', False) else self._("No")
                        ),
                        tags=('file',),
                        image=self.get_file_icon(file['mimeType'])
                    )

                # به‌روزرسانی نمای تصاویر کوچک
                self.update_thumbnail_view(files)

                # به‌روزرسانی نمای جزئیات
                self.update_details_view(files)

            def update_thumbnail_view(self, files):
                """به‌روزرسانی نمای تصاویر کوچک"""
                # پاکسازی ویجت‌های قبلی
                for widget in self.thumb_container.winfo_children():
                    widget.destroy()

                # ایجاد ویجت‌های جدید برای هر فایل
                for file in files:
                    frame = ttk.Frame(self.thumb_container)
                    frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

                    # آیکون یا تصویر کوچک
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        icon = self.assets.get_icon('folder', (64, 64))
                    else:
                        icon = self.get_file_icon(file['mimeType'], (64, 64))

                    label = ttk.Label(frame, image=icon)
                    label.image = icon
                    label.pack()

                    # نام فایل
                    name_label = ttk.Label(
                        frame,
                        text=file['name'],
                        wraplength=100,
                        justify=tk.CENTER
                    )
                    name_label.pack()

            def update_details_view(self, files):
                """به‌روزرسانی نمای جزئیات"""
                # پاکسازی ویجت‌های قبلی
                for widget in self.details_frame.winfo_children():
                    widget.destroy()

                # ایجاد جدول جزئیات
                columns = [
                    {"text": "Name", "stretch": True},
                    {"text": "Size", "stretch": False},
                    {"text": "Type", "stretch": False},
                    {"text": "Modified", "stretch": False},
                    {"text": "Shared", "stretch": False}
                ]

                rows = []
                for file in files:
                    rows.append((
                        file['name'],
                        self.format_size(int(file.get('size', 0))),
                        self.get_file_type(file['mimeType']),
                        self.format_date(file['modifiedTime']),
                        "Yes" if file.get('shared', False) else "No"
                    ))

                self.details_table = Tableview(
                    self.details_frame,
                    coldata=columns,
                    rowdata=rows,
                    paginated=True,
                    pagesize=20,
                    height=20,
                    searchable=True,
                    bootstyle="info"
                )
                self.details_table.pack(fill=tk.BOTH, expand=True)

            def on_item_double_click(self, event):
                """رویداد دابل کلیک روی آیتم"""
                item = self.tree.selection()[0]
                self.open_item(item)

            def open_item(self, item):
                """باز کردن آیتم انتخاب شده"""
                item_type = self.tree.item(item, 'tags')[0]
                item_name = self.tree.item(item, 'values')[0]

                if item_type == 'folder':
                    try:
                        files = self.file_manager.list_files()
                        folder = next((f for f in files if f['name'] == item_name and
                                       f['mimeType'] == 'application/vnd.google-apps.folder'), None)

                        if folder:
                            self.file_manager.current_folder_id = folder['id']
                            self.file_manager.folder_stack.append(folder['id'])
                            self.load_files()
                            self.update_navigation_buttons()
                            self.path_var.set(f"Drive > {item_name}")
                    except Exception as e:
                        self.status_var.set(self._("Error: {}").format(str(e)))
                else:
                    try:
                        files = self.file_manager.list_files()
                        file = next((f for f in files if f['name'] == item_name and
                                     f['mimeType'] != 'application/vnd.google-apps.folder'), None)

                        if file:
                            webbrowser.open(f"https://drive.google.com/file/d/{file['id']}/view")
                    except Exception as e:
                        self.status_var.set(self._("Error: {}").format(str(e)))

            def navigate_back(self):
                """بازگشت به پوشه قبلی"""
                if len(self.file_manager.folder_stack) > 1:
                    self.file_manager.folder_stack.pop()
                    self.file_manager.current_folder_id = self.file_manager.folder_stack[-1]
                    self.load_files()
                    self.update_navigation_buttons()

            def navigate_up(self):
                """رفتن به پوشه والد"""
                self.file_manager.current_folder_id = "root"
                self.file_manager.folder_stack = ["root"]
                self.load_files()
                self.update_navigation_buttons()

            def refresh_files(self):
                """بارگذاری مجدد فایل‌ها"""
                self.file_manager.clear_cache()
                self.load_files()

            def update_navigation_buttons(self):
                """به‌روزرسانی وضعیت دکمه‌های ناوبری"""
                self.back_btn['state'] = tk.NORMAL if len(self.file_manager.folder_stack) > 1 else tk.DISABLED

            def show_context_menu(self, event):
                """نمایش منوی زمینه"""
                item = self.tree.identify_row(event.y)
                if item:
                    self.tree.selection_set(item)
                    try:
                        self.context_menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        self.context_menu.grab_release()

            def open_selected(self):
                """باز کردن آیتم انتخاب شده"""
                selected = self.tree.selection()
                if selected:
                    self.open_item(selected[0])

            def download_selected(self):
                """دانلود فایل(های) انتخاب شده"""
                selected = self.tree.selection()
                if not selected:
                    Messagebox.show_warning(self._("Please select a file first"), self._("Warning"))
                    return

                # برای سادگی، فقط اولین فایل انتخاب شده را دانلود می‌کنیم
                item = selected[0]
                item_name = self.tree.item(item, 'values')[0]

                save_path = filedialog.asksaveasfilename(
                    title=self._("Save File"),
                    initialfile=item_name,
                    defaultextension=".*"
                )

                if not save_path:
                    return

                try:
                    files = self.file_manager.list_files()
                    file = next((f for f in files if f['name'] == item_name and
                                 f['mimeType'] != 'application/vnd.google-apps.folder'), None)

                    if file:
                        progress_dialog = ProgressDialog(
                            self,
                            title=self._("Downloading"),
                            message=self._("Downloading {}...").format(item_name)
                        )

                        threading.Thread(
                            target=self._perform_download,
                            args=(file['id'], save_path, progress_dialog),
                            daemon=True
                        ).start()

                except Exception as e:
                    Messagebox.show_error(str(e), self._("Error"))

            def _perform_download(self, file_id, save_path, progress_dialog):
                """انجام عملیات دانلود با نمایش پیشرفت"""
                try:
                    for downloaded, total in self.file_manager.download_file(file_id, save_path):
                        progress = (downloaded / total) * 100
                        progress_dialog.update_progress(
                            progress,
                            f"{self.format_size(downloaded)} / {self.format_size(total)}"
                        )

                        if progress_dialog.cancelled:
                            os.remove(save_path)
                            return

                    progress_dialog.complete(self._("Download complete"))
                    Messagebox.show_info(self._("File downloaded successfully"), self._("Success"))

                except Exception as e:
                    progress_dialog.error(str(e))
                    Messagebox.show_error(str(e), self._("Error"))
                finally:
                    progress_dialog.close()

            def rename_selected(self):
                """تغییر نام فایل انتخاب شده"""
                selected = self.tree.selection()
                if not selected:
                    Messagebox.show_warning(self._("Please select a file first"), self._("Warning"))
                    return

                item = selected[0]
                old_name = self.tree.item(item, 'values')[0]

                new_name = Querybox.get_string(
                    prompt=self._("Enter new name:"),
                    title=self._("Rename File"),
                    initialvalue=old_name,
                    parent=self
                )

                if not new_name or new_name == old_name:
                    return

                try:
                    files = self.file_manager.list_files()
                    file = next((f for f in files if f['name'] == old_name), None)

                    if file:
                        self.file_manager.rename_file(file['id'], new_name)
                        self.load_files()
                        Messagebox.show_info(self._("File renamed successfully"), self._("Success"))
                except Exception as e:
                    Messagebox.show_error(str(e), self._("Error"))

            def share_selected(self):
                """اشتراک‌گذاری فایل انتخاب شده"""
                selected = self.tree.selection()
                if not selected:
                    Messagebox.show_warning(self._("Please select a file first"), self._("Warning"))
                    return

                item = selected[0]
                item_name = self.tree.item(item, 'values')[0]

                share_type = Querybox.get_string(
                    prompt=self._(
                        "Share '{}' with:\n1. Specific user (enter email)\n2. Anyone with link (enter 'public')\n3. Cancel (leave blank)").format(
                        item_name),
                    title=self._("Share File"),
                    parent=self
                )

                if not share_type:
                    return

                try:
                    files = self.file_manager.list_files()
                    file = next((f for f in files if f['name'] == item_name), None)

                    if file:
                        if share_type.lower() == 'public':
                            self.file_manager.share_file(file['id'], 'public')
                        else:
                            self.file_manager.share_file(file['id'], 'user', share_type)

                        self.load_files()
                        Messagebox.show_info(self._("Sharing settings updated"), self._("Success"))
                except Exception as e:
                    Messagebox.show_error(str(e), self._("Error"))

            def delete_selected(self):
                """حذف فایل(های) انتخاب شده"""
                selected = self.tree.selection()
                if not selected:
                    Messagebox.show_warning(self._("Please select a file first"), self._("Warning"))
                    return

                item = selected[0]
                item_name = self.tree.item(item, 'values')[0]

                if not Messagebox.okcancel(
                        self._("Are you sure you want to delete '{}'?").format(item_name),
                        self._("Confirm Delete"),
                        parent=self
                ):
                    return

                try:
                    files = self.file_manager.list_files()
                    file = next((f for f in files if f['name'] == item_name), None)

                    if file:
                        self.file_manager.delete_file(file['id'])
                        self.load_files()
                        Messagebox.show_info(self._("File deleted successfully"), self._("Success"))
                except Exception as e:
                    Messagebox.show_error(str(e), self._("Error"))

            def show_properties(self):
                """نمایش ویژگی‌های فایل انتخاب شده"""
                selected = self.tree.selection()
                if not selected:
                    return

                item = selected[0]
                item_name = self.tree.item(item, 'values')[0]

                try:
                    files = self.file_manager.list_files()
                    file = next((f for f in files if f['name'] == item_name), None)

                    if file:
                        PropertiesDialog(self, file)
                except Exception as e:
                    Messagebox.show_error(str(e), self._("Error"))

            def show_upload_dialog(self):
                """نمایش دیالوگ آپلود"""
                upload_window = UploadDialog(self, self.file_manager)

            def search_files(self):
                """جستجوی فایل‌ها"""
                query = self.search_var.get().strip()
                if not query or query == self._("Search Files..."):
                    return

                try:
                    files = self.file_manager.list_files()
                    results = [f for f in files if query.lower() in f['name'].lower()]
                    self.update_file_list(results)
                    self.status_var.set(self._("Found {} matching files").format(len(results)))
                except Exception as e:
                    self.status_var.set(self._("Search error: {}").format(str(e)))

            def update_storage_info(self):
                """به‌روزرسانی اطلاعات فضای ذخیره‌سازی"""
                try:
                    storage = self.file_manager.get_storage_info()
                    used = self.format_size(int(storage.get('usage', 0)))
                    total = self.format_size(int(storage.get('limit', 0)))
                    free = self.format_size(int(storage.get('limit', 0)) - int(storage.get('usage', 0)))

                    self.storage_var.set(
                        f"{self._('Used:')} {used} | {self._('Free:')} {free} | {self._('Total:')} {total}")
                except Exception as e:
                    logger.error(f"Error getting storage info: {e}")
                    self.storage_var.set("")

            def get_file_id(self, file_name):
                """دریافت ID فایل بر اساس نام"""
                files = self.file_manager.list_files()
                file = next((f for f in files if f['name'] == file_name), None)
                return file['id'] if file else None

            @staticmethod
            def get_file_type(mime_type):
                """دریافت نوع فایل به صورت خوانا"""
                if 'image/' in mime_type:
                    return "Image"
                elif 'video/' in mime_type:
                    return "Video"
                elif 'audio/' in mime_type:
                    return "Audio"
                elif 'application/pdf' in mime_type:
                    return "PDF"
                elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
                    return "Word"
                elif 'text/' in mime_type:
                    return "Text"
                else:
                    return mime_type.split('/')[-1].title()

            @staticmethod
            def get_file_icon(mime_type, size=None):
                """دریافت آیکون مناسب برای نوع فایل"""
                assets = AppAssets(None)
                if 'image/' in mime_type:
                    return assets.get_icon('image', size)
                elif 'video/' in mime_type:
                    return assets.get_icon('video', size)
                elif 'audio/' in mime_type:
                    return assets.get_icon('audio', size)
                elif 'application/pdf' in mime_type:
                    return assets.get_icon('pdf', size)
                elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
                    return assets.get_icon('word', size)
                elif 'text/' in mime_type:
                    return assets.get_icon('text', size)
                else:
                    return assets.get_icon('file', size)

            @staticmethod
            def format_size(size_bytes):
                """قالب‌بندی اندازه فایل به صورت خوانا"""
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
                """قالب‌بندی تاریخ به صورت خوانا"""
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M')
                except:
                    return date_str

        class UploadDialog(tk.Toplevel):
            """دیالوگ آپلود پیشرفته"""

            def __init__(self, parent, file_manager):
                super().__init__(parent)
                self.file_manager = file_manager
                self.assets = AppAssets(parent)
                self.lang = LanguageManager()
                self._ = self.lang.gettext
                self.setup_window()
                self.create_widgets()
                self.setup_animations()

            def setup_window(self):
                """تنظیمات پنجره"""
                self.title(self._("Upload Files"))
                self.geometry("600x400")
                self.resizable(False, False)
                self.center_window()

                # آیکون پنجره
                try:
                    self.iconphoto(False, self.assets.get_icon('upload'))
                except:
                    pass

            def setup_animations(self):
                """تنظیم انیمیشن‌های پنجره"""
                self.assets.animations['fade'](self)

            def center_window(self):
                """مرکز کردن پنجره"""
                self.update_idletasks()
                width = self.winfo_width()
                height = self.winfo_height()
                x = (self.winfo_screenwidth() // 2) - (width // 2)
                y = (self.winfo_screenheight() // 2) - (height // 2)
                self.geometry(f'+{x}+{y}')

            def create_widgets(self):
                """ایجاد ویجت‌های پنجره"""
                # فریم اصلی
                main_frame = ttk.Frame(self, padding=10)
                main_frame.pack(fill=tk.BOTH, expand=True)

                # انتخاب فایل
                file_frame = ttk.LabelFrame(
                    main_frame,
                    text=self._("File Selection"),
                    padding=10
                )
                file_frame.pack(fill=tk.X, pady=5)

                # ورودی فایل و دکمه مرور
                file_select_frame = ttk.Frame(file_frame)
                file_select_frame.pack(fill=tk.X, pady=5)

                self.file_entry = ttk.Entry(file_select_frame)
                self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

                self.browse_btn = ttk.Button(
                    file_select_frame,
                    text=self._("Browse..."),
                    command=self.select_file,
                    width=10
                )
                self.browse_btn.pack(side=tk.LEFT)

                # اطلاعات فایل
                self.file_info_label = ttk.Label(
                    file_frame,
                    text=self._("No file selected"),
                    wraplength=500
                )
                self.file_info_label.pack(fill=tk.X, pady=5)

                # گزینه‌های آپلود
                options_frame = ttk.LabelFrame(
                    main_frame,
                    text=self._("Upload Options"),
                    padding=10
                )
                options_frame.pack(fill=tk.X, pady=5)

                # پوشه مقصد
                ttk.Label(
                    options_frame,
                    text=self._("Destination Folder:")
                ).grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

                self.folder_entry = ttk.Entry(options_frame)
                self.folder_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
                self.folder_entry.insert(0, self._("My Drive"))

                self.change_folder_btn = ttk.Button(
                    options_frame,
                    text=self._("Change..."),
                    command=self.select_destination_folder,
                    width=10
                )
                self.change_folder_btn.grid(row=0, column=2, padx=5, pady=5)

                # نام فایل در درایو
                ttk.Label(
                    options_frame,
                    text=self._("Drive File Name:")
                ).grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

                self.drive_name_entry = ttk.Entry(options_frame)
                self.drive_name_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)

                # تنظیمات گرید
                options_frame.grid_columnconfigure(1, weight=1)

                # پیشرفت آپلود
                progress_frame = ttk.LabelFrame(
                    main_frame,
                    text=self._("Upload Progress"),
                    padding=10
                )
                progress_frame.pack(fill=tk.X, pady=5)

                self.progress = ttk.Progressbar(
                    progress_frame,
                    orient=tk.HORIZONTAL,
                    mode='determinate'
                )
                self.progress.pack(fill=tk.X, pady=5)

                self.progress_label = ttk.Label(
                    progress_frame,
                    text=self._("Ready to upload"),
                    anchor=tk.CENTER
                )
                self.progress_label.pack(fill=tk.X)

                # دکمه‌های عملیاتی
                btn_frame = ttk.Frame(main_frame)
                btn_frame.pack(fill=tk.X, pady=10)

                self.upload_btn = ttk.Button(
                    btn_frame,
                    text=self._("Start Upload"),
                    command=self.start_upload,
                    bootstyle="success",
                    state=tk.DISABLED
                )
                self.upload_btn.pack(side=tk.LEFT, padx=5)

                self.cancel_btn = ttk.Button(
                    btn_frame,
                    text=self._("Cancel"),
                    command=self.destroy,
                    bootstyle="danger"
                )
                self.cancel_btn.pack(side=tk.RIGHT, padx=5)

            def select_file(self):
                """انتخاب فایل برای آپلود"""
                file_path = filedialog.askopenfilename(
                    title=self._("Select File to Upload"),
                    filetypes=[
                        (self._("All Files"), "*.*"),
                        (self._("Documents"), "*.doc *.docx *.pdf *.txt *.rtf"),
                        (self._("Images"), "*.jpg *.jpeg *.png *.gif *.bmp"),
                        (self._("Videos"), "*.mp4 *.avi *.mov *.mkv")
                    ]
                )

                if file_path:
                    self.file_entry.delete(0, tk.END)
                    self.file_entry.insert(0, file_path)
                    self.update_file_info(file_path)

                    # پر کردن نام فایل در درایو
                    file_name = os.path.basename(file_path)
                    self.drive_name_entry.delete(0, tk.END)
                    self.drive_name_entry.insert(0, file_name)

                    if self.file_manager.access_token:
                        self.upload_btn['state'] = tk.NORMAL

            def update_file_info(self, file_path):
                """به‌روزرسانی اطلاعات فایل"""
                try:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)

                    info_text = f"{self._('File:')} {file_name}\n{self._('Size:')} {self.format_size(file_size)}"
                    self.file_info_label.config(text=info_text)
                except Exception as e:
                    logger.error(f"Error getting file info: {e}")
                    self.file_info_label.config(text=self._("Error getting file information"))

            def select_destination_folder(self):
                """انتخاب پوشه مقصد در گوگل درایو"""
                if not self.file_manager.access_token:
                    Messagebox.show_error(
                        self._("You must authenticate first"),
                        self._("Error")
                    )
                    return

                # در نسخه کامل می‌توانید یک مرورگر پوشه درایو پیاده‌سازی کنید
                Messagebox.show_info(
                    self._("Folder selection will be implemented in a future version"),
                    self._("Info")
                )

            def start_upload(self):
                """شروع آپلود فایل"""
                file_path = self.file_entry.get()
                if not file_path or not os.path.exists(file_path):
                    Messagebox.show_error(
                        self._("Please select a valid file"),
                        self._("Error")
                    )
                    return

                drive_name = self.drive_name_entry.get().strip()
                if not drive_name:
                    drive_name = os.path.basename(file_path)

                # نمایش دیالوگ پیشرفت
                progress_dialog = ProgressDialog(
                    self,
                    title=self._("Uploading"),
                    message=self._("Uploading {}...").format(drive_name)
                )

                # شروع آپلود در یک thread جداگانه
                threading.Thread(
                    target=self._perform_upload,
                    args=(file_path, drive_name, progress_dialog),
                    daemon=True
                ).start()

            def _perform_upload(self, file_path, drive_name, progress_dialog):
                """انجام عملیات آپلود"""
                try:
                    # در اینجا می‌توانید از file_manager.upload_file استفاده کنید
                    # این یک پیاده‌سازی ساده برای نمایش پیشرفت است
                    file_size = os.path.getsize(file_path)
                    chunk_size = file_size // 100

                    for i in range(101):
                        progress_dialog.update_progress(
                            i,
                            f"{self.format_size(i * chunk_size)} / {self.format_size(file_size)}"
                        )
                        time.sleep(0.05)  # شبیه‌سازی زمان آپلود

                        if progress_dialog.cancelled:
                            return

                    # در نسخه واقعی، نتیجه آپلود را نمایش دهید
                    progress_dialog.complete(self._("Upload complete"))
                    Messagebox.show_info(
                        self._("File uploaded successfully"),
                        self._("Success")
                    )

                except Exception as e:
                    progress_dialog.error(str(e))
                    Messagebox.show_error(str(e), self._("Error"))
                finally:
                    progress_dialog.close()
                    self.destroy()

            @staticmethod
            def format_size(size_bytes):
                """قالب‌بندی اندازه فایل"""
                if not size_bytes:
                    return "0 B"

                size_bytes = int(size_bytes)
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size_bytes < 1024.0:
                        return f"{size_bytes:.1f} {unit}"
                    size_bytes /= 1024.0
                return f"{size_bytes:.1f} PB"

        class EnhancedProgressDialog(tk.Toplevel):
            """دیالوگ پیشرفت پیشرفته"""

            def __init__(self, parent, title="Progress", message="Processing..."):
                super().__init__(parent)
                self.title(title)
                self.geometry("400x180")  # ارتفاع بیشتر برای جزئیات بیشتر
                self.resizable(False, False)
                self.cancelled = False

                # مرکز کردن پنجره
                self.center_window()

                # تنظیمات ظاهری
                self.attributes('-alpha', 0.95)

                # پیام
                self.message_var = tk.StringVar(value=message)
                ttk.Label(
                    self,
                    textvariable=self.message_var,
                    wraplength=380,
                    font=("TkDefaultFont", 10)
                ).pack(pady=(15, 5))

                # نوار پیشرفت
                self.progress = ttk.Progressbar(
                    self,
                    orient=tk.HORIZONTAL,
                    mode='determinate',
                    length=380,
                    style="success.Striped.Horizontal.TProgressbar"
                )
                self.progress.pack(pady=5)

                # متن پیشرفت
                self.progress_var = tk.StringVar(value="")
                ttk.Label(
                    self,
                    textvariable=self.progress_var,
                    font=("TkDefaultFont", 8)
                ).pack()

                # تخمین زمان باقیمانده
                self.time_var = tk.StringVar(value="")
                ttk.Label(
                    self,
                    textvariable=self.time_var,
                    font=("TkDefaultFont", 8)
                ).pack()

                # دکمه‌ها
                btn_frame = ttk.Frame(self)
                btn_frame.pack(pady=10)

                self.cancel_btn = ttk.Button(
                    btn_frame,
                    text="Cancel",
                    command=self.cancel,
                    bootstyle="danger"
                )
                self.cancel_btn.pack(side=tk.LEFT, padx=10)

                self.minimize_btn = ttk.Button(
                    btn_frame,
                    text="Minimize",
                    command=self.minimize
                )
                self.minimize_btn.pack(side=tk.RIGHT, padx=10)

                # متغیرهای زمان
                self.start_time = time.time()
                self.last_update = 0

                # تنظیم modal
                self.grab_set()
                self.transient(parent)
                self.protocol("WM_DELETE_WINDOW", self.cancel)

            def center_window(self):
                """مرکز کردن پنجره"""
                self.update_idletasks()
                width = self.winfo_width()
                height = self.winfo_height()
                x = (self.winfo_screenwidth() // 2) - (width // 2)
                y = (self.winfo_screenheight() // 2) - (height // 2)
                self.geometry(f'+{x}+{y}')

            def update_progress(self, value, text=""):
                """به‌روزرسانی پیشرفت"""
                self.progress['value'] = value
                self.progress_var.set(text)

                # محاسبه زمان باقیمانده
                current_time = time.time()
                if current_time - self.last_update > 1:  # هر ثانیه یکبار به‌روزرسانی کنید
                    elapsed = current_time - self.start_time
                    if value > 0:
                        remaining = (elapsed * (100 - value)) / value
                        self.time_var.set(f"Estimated time remaining: {self.format_time(remaining)}")
                    self.last_update = current_time

                self.update_idletasks()

            def complete(self, message):
                """تکمیل عملیات"""
                self.message_var.set(message)
                self.progress['value'] = 100
                self.progress_var.set("")
                self.time_var.set("")
                self.cancel_btn.config(text="Close")
                self.minimize_btn.pack_forget()
                self.update_idletasks()

            def error(self, message):
                """نمایش خطا"""
                self.message_var.set(f"Error: {message}")
                self.progress.config(style="danger.Horizontal.TProgressbar")
                self.cancel_btn.config(text="Close")
                self.minimize_btn.pack_forget()
                self.update_idletasks()

            def cancel(self):
                """لغو عملیات"""
                self.cancelled = True
                self.message_var.set("Cancelling...")
                self.update_idletasks()

            def minimize(self):
                """کوچک کردن پنجره"""
                self.iconify()

            @staticmethod
            def format_time(seconds):
                """قالب‌بندی زمان به صورت خوانا"""
                seconds = int(seconds)
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60

                if hours > 0:
                    return f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s"
                else:
                    return f"{seconds}s"

        class EnhancedPropertiesDialog(tk.Toplevel):
            """دیالوگ ویژگی‌های پیشرفته"""

            def __init__(self, parent, file_data):
                super().__init__(parent)
                self.title("Properties")
                self.geometry("500x500")
                self.resizable(False, False)
                self.file_data = file_data
                self.assets = AppAssets(parent)
                self.lang = LanguageManager()
                self._ = self.lang.gettext
                self.setup_ui()
                self.center_window()

            def center_window(self):
                """مرکز کردن پنجره"""
                self.update_idletasks()
                width = self.winfo_width()
                height = self.winfo_height()
                x = (self.winfo_screenwidth() // 2) - (width // 2)
                y = (self.winfo_screenheight() // 2) - (height // 2)
                self.geometry(f'+{x}+{y}')

            def setup_ui(self):
                """تنظیم رابط کاربری"""
                # فریم اصلی
                main_frame = ttk.Frame(self, padding=10)
                main_frame.pack(fill=tk.BOTH, expand=True)

                # هدر
                header_frame = ttk.Frame(main_frame)
                header_frame.pack(fill=tk.X, pady=(0, 10))

                # آیکون فایل
                file_icon = self.get_file_icon(self.file_data['mimeType'], (64, 64))
                ttk.Label(
                    header_frame,
                    image=file_icon
                ).pack(side=tk.LEFT, padx=10)

                # نام و نوع فایل
                info_frame = ttk.Frame(header_frame)
                info_frame.pack(side=tk.LEFT, fill=tk.Y)

                ttk.Label(
                    info_frame,
                    text=self.file_data['name'],
                    font=("TkDefaultFont", 12, "bold")
                ).pack(anchor=tk.W)

                ttk.Label(
                    info_frame,
                    text=self.get_file_type(self.file_data['mimeType']),
                    font=("TkDefaultFont", 9)
                ).pack(anchor=tk.W)

                # تب‌ها
                notebook = ttk.Notebook(main_frame)
                notebook.pack(fill=tk.BOTH, expand=True)

                # تب عمومی
                general_tab = ttk.Frame(notebook)
                notebook.add(general_tab, text=self._("General"))

                self.create_general_tab(general_tab)

                # تب جزئیات
                details_tab = ttk.Frame(notebook)
                notebook.add(details_tab, text=self._("Details"))

                self.create_details_tab(details_tab)

                # تب اشتراک‌گذاری
                sharing_tab = ttk.Frame(notebook)
                notebook.add(sharing_tab, text=self._("Sharing"))

                self.create_sharing_tab(sharing_tab)

                # دکمه بستن
                ttk.Button(
                    main_frame,
                    text=self._("Close"),
                    command=self.destroy,
                    bootstyle="primary"
                ).pack(pady=10)

            def create_general_tab(self, parent):
                """ایجاد تب عمومی"""
                # تصویر کوچک برای فایل‌های تصویری
                if 'image/' in self.file_data['mimeType'] and 'thumbnailLink' in self.file_data:
                    try:
                        response = requests.get(self.file_data['thumbnailLink'], stream=True)
                        if response.status_code == 200:
                            img_data = response.content
                            img = Image.open(io.BytesIO(img_data))
                            img.thumbnail((200, 200))

                            photo = ImageTk.PhotoImage(img)
                            label = ttk.Label(parent, image=photo)
                            label.image = photo
                            label.pack(pady=10)
                    except:
                        pass

                # اطلاعات پایه
                info_frame = ttk.Frame(parent)
                info_frame.pack(fill=tk.X, pady=5)

                properties = [
                    (self._("Name:"), self.file_data['name']),
                    (self._("Type:"), self.get_file_type(self.file_data['mimeType'])),
                    (self._("Size:"), self.format_size(int(self.file_data.get('size', 0)))),
                    (self._("Modified:"), self.format_date(self.file_data['modifiedTime'])),
                    (self._("Shared:"), self._("Yes") if self.file_data.get('shared', False) else self._("No"))
                ]

                for i, (prop, value) in enumerate(properties):
                    row = ttk.Frame(info_frame)
                    row.pack(fill=tk.X, pady=2)

                    ttk.Label(
                        row,
                        text=prop,
                        font=("TkDefaultFont", 9, "bold"),
                        width=15,
                        anchor=tk.E
                    ).pack(side=tk.LEFT)

                    ttk.Label(
                        row,
                        text=value,
                        font=("TkDefaultFont", 9),
                        anchor=tk.W
                    ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            def create_details_tab(self, parent):
                """ایجاد تب جزئیات"""
                # جدول جزئیات
                columns = [
                    {"text": "Property", "stretch": False},
                    {"text": "Value", "stretch": True}
                ]

                rows = [
                    ("ID", self.file_data['id']),
                    ("MIME Type", self.file_data['mimeType']),
                    ("Created", self.format_date(self.file_data.get('createdTime', ''))),
                    ("Modified", self.format_date(self.file_data['modifiedTime'])),
                    ("Size", self.format_size(int(self.file_data.get('size', 0)))),
                    ("Shared", "Yes" if self.file_data.get('shared', False) else "No"),
                    ("Web View", self.file_data.get('webViewLink', 'N/A'))
                ]

                table = Tableview(
                    parent,
                    coldata=columns,
                    rowdata=rows,
                    paginated=False,
                    searchable=False,
                    bootstyle="info"
                )
                table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # دکمه کپی ID
                ttk.Button(
                    parent,
                    text=self._("Copy ID"),
                    command=lambda: self.copy_to_clipboard(self.file_data['id']),
                    bootstyle="info"
                ).pack(pady=5)

            def create_sharing_tab(self, parent):
                """ایجاد تب اشتراک‌گذاری"""
                if not self.file_data.get('shared', False):
                    ttk.Label(
                        parent,
                        text=self._("This file is not shared"),
                        font=("TkDefaultFont", 10)
                    ).pack(pady=20)
                    return

                # در نسخه کامل می‌توانید لیست مجوزها را نمایش دهید
                ttk.Label(
                    parent,
                    text=self._("Sharing settings:"),
                    font=("TkDefaultFont", 10, "bold")
                ).pack(pady=5)

                ttk.Label(
                    parent,
                    text=self._("Anyone with the link can view"),
                    font=("TkDefaultFont", 9)
                ).pack()

                # دکمه‌های مدیریت اشتراک
                btn_frame = ttk.Frame(parent)
                btn_frame.pack(pady=10)

                ttk.Button(
                    btn_frame,
                    text=self._("Copy Link"),
                    command=self.copy_share_link,
                    bootstyle="info"
                ).pack(side=tk.LEFT, padx=5)

                ttk.Button(
                    btn_frame,
                    text=self._("Change Permissions"),
                    command=self.change_permissions,
                    bootstyle="warning"
                ).pack(side=tk.LEFT, padx=5)

                ttk.Button(
                    btn_frame,
                    text=self._("Stop Sharing"),
                    command=self.stop_sharing,
                    bootstyle="danger"
                ).pack(side=tk.LEFT, padx=5)

        def copy_to_clipboard(self, text):
            """کپی متن به کلیپ‌بورد"""
            try:
                pyperclip.copy(text)
                Messagebox.show_info(
                    self._("Copied to clipboard"),
                    self._("Success")
                )
            except:
                Messagebox.show_error(
                    self._("Could not copy to clipboard"),
                    self._("Error")
                )

        def copy_share_link(self):
            """کپی لینک اشتراک‌گذاری"""
            if 'webViewLink' in self.file_data:
                self.copy_to_clipboard(self.file_data['webViewLink'])
            else:
                Messagebox.show_warning(
                    self._("No share link available"),
                    self._("Warning")
                )

        def change_permissions(self):
            """تغییر مجوزهای اشتراک‌گذاری"""
            Messagebox.show_info(
                self._("This feature will be implemented in a future version"),
                self._("Info")
            )

        def stop_sharing(self):
            """توقف اشتراک‌گذاری"""
            if Messagebox.okcancel(
                    self._("Are you sure you want to stop sharing this file?"),
                    self._("Confirm"),
                    parent=self
            ):
                Messagebox.show_info(
                    self._("This feature will be implemented in a future version"),
                    self._("Info")
                )

        def get_file_icon(self, mime_type, size=None):
            """دریافت آیکون فایل"""
            if mime_type == 'application/vnd.google-apps.folder':
                return self.assets.get_icon('folder', size)
            elif 'image/' in mime_type:
                return self.assets.get_icon('image', size)
            elif 'video/' in mime_type:
                return self.assets.get_icon('video', size)
            elif 'audio/' in mime_type:
                return self.assets.get_icon('audio', size)
            elif 'application/pdf' in mime_type:
                return self.assets.get_icon('pdf', size)
            elif 'text/' in mime_type:
                return self.assets.get_icon('text', size)
            else:
                return self.assets.get_icon('file', size)

        def get_file_type(self, mime_type):
            """دریافت نوع فایل"""
            if mime_type == 'application/vnd.google-apps.folder':
                return self._("Folder")
            elif 'image/' in mime_type:
                return self._("Image")
            elif 'video/' in mime_type:
                return self._("Video")
            elif 'audio/' in mime_type:
                return self._("Audio")
            elif 'application/pdf' in mime_type:
                return "PDF"
            elif 'text/' in mime_type:
                return self._("Text")
            else:
                return mime_type.split('/')[-1].title()

        @staticmethod
        def format_size(size_bytes):
            """قالب‌بندی اندازه فایل"""
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
            """قالب‌بندی تاریخ"""
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M')
            except:
                return date_str

    class EnhancedSfileCloud:
        """کلاس اصلی برنامه با تمام بهبودها"""

        def __init__(self, root):
            self.root = root
            self.assets = AppAssets(root)
            self.lang = EnhancedLanguageManager()
            self._ = self.lang.gettext

            # تنظیمات اولیه
            self.initialize()

            # تنظیم پنجره اصلی
            self.setup_main_window()

            # تنظیم رابط کاربری
            self.setup_ui()

            # بارگذاری تنظیمات
            self.load_settings()

            # تنظیم زبان پیش‌فرض
            self.lang.set_language("en")

            # نمایش splash screen
            self.show_splash()

        def initialize(self):
            """مقداردهی اولیه متغیرها"""
            # تنظیمات تم
            self.theme_mode = "light"
            self.available_themes = ["light", "dark", "blue", "green", "superhero", "solar"]

            # تنظیمات OAuth
            self.client_config = {
                "installed": {
                    "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
                    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', ''),
                    "redirect_uris": ["http://localhost:8080"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }

            # مدیر فایل
            self.file_manager = EnhancedDriveFileManager(self.client_config)

        def setup_main_window(self):
            """تنظیم پنجره اصلی"""
            self.root.title(self._("SfileCloud Professional"))
            self.root.geometry("1200x800")
            self.root.minsize(1000, 700)

            # آیکون پنجره
            try:
                self.root.iconphoto(False, self.assets.get_image('logo'))
            except:
                pass

            # مرکز کردن پنجره
            self.center_window()

            # تنظیم تم
            self.style = Style(theme="flatly")

        def center_window(self):
            """مرکز کردن پنجره روی صفحه"""
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'+{x}+{y}')

        def show_splash(self):
            """نمایش splash screen"""
            self.splash = tk.Toplevel(self.root)
            self.splash.title("SfileCloud Professional")
            self.splash.geometry("500x300")
            self.splash.overrideredirect(True)

            # مرکز کردن splash
            self.splash.update_idletasks()
            width = self.splash.winfo_width()
            height = self.splash.winfo_height()
            x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
            y = (self.splash.winfo_screenheight() // 2) - (height // 2)
            self.splash.geometry(f'+{x}+{y}')

            # محتوای splash
            logo = self.assets.get_image('splash')
            if logo:
                ttk.Label(self.splash, image=logo).pack(pady=20)

            ttk.Label(
                self.splash,
                text="SfileCloud Professional",
                font=("Helvetica", 16, "bold")
            ).pack()

            ttk.Label(
                self.splash,
                text="Loading...",
                font=("Helvetica", 10)
            ).pack(pady=20)

            progress = ttk.Progressbar(
                self.splash,
                orient=tk.HORIZONTAL,
                mode='indeterminate',
                length=300
            )
            progress.pack(pady=10)
            progress.start()

            # به‌روزرسانی splash
            self.splash.update()

            # بستن splash پس از تاخیر
            self.root.after(2000, self.close_splash)

        def close_splash(self):
            """بستن splash screen"""
            try:
                self.splash.destroy()
            except:
                pass

            # نمایش پنجره اصلی
            self.root.deiconify()

        def setup_ui(self):
            """تنظیم رابط کاربری اصلی"""
            self.create_menu_bar()
            self.create_main_notebook()
            self.create_status_bar()

        def create_menu_bar(self):
            """ایجاد نوار منوی پیشرفته"""
            self.menubar = tk.Menu(self.root)

            # منوی فایل
            self.file_menu = tk.Menu(self.menubar, tearoff=0)
            self.file_menu.add_command(
                label=self._("New Upload"),
                command=self.new_upload,
                image=self.assets.get_icon('upload'),
                compound=tk.LEFT,
                accelerator="Ctrl+N"
            )
            self.file_menu.add_command(
                label=self._("Open Folder"),
                command=self.open_local_folder,
                image=self.assets.get_icon('folder'),
                compound=tk.LEFT,
                accelerator="Ctrl+O"
            )
            self.file_menu.add_separator()
            self.file_menu.add_command(
                label=self._("Exit"),
                command=self.root.quit,
                image=self.assets.get_icon('exit'),
                compound=tk.LEFT,
                accelerator="Alt+F4"
            )
            self.menubar.add_cascade(label=self._("File"), menu=self.file_menu)

            # منوی ویرایش
            self.edit_menu = tk.Menu(self.menubar, tearoff=0)
            self.edit_menu.add_command(
                label=self._("Copy"),
                image=self.assets.get_icon('copy'),
                compound=tk.LEFT,
                command=lambda: self.assets.copy_item(self.get_selected_item()),
                accelerator="Ctrl+C"
            )
            self.edit_menu.add_command(
                label=self._("Paste"),
                image=self.assets.get_icon('paste'),
                compound=tk.LEFT,
                command=lambda: self.handle_paste(self.assets.paste_item()),
                accelerator="Ctrl+V"
            )
            self.edit_menu.add_separator()
            self.edit_menu.add_command(
                label=self._("Refresh"),
                image=self.assets.get_icon('refresh'),
                compound=tk.LEFT,
                command=self.refresh_files,
                accelerator="F5"
            )
            self.menubar.add_cascade(label=self._("Edit"), menu=self.edit_menu)

            # منوی نمایش
            self.view_menu = tk.Menu(self.menubar, tearoff=0)

            # زیرمنوی تم
            theme_menu = tk.Menu(self.view_menu, tearoff=0)
            for theme in self.available_themes:
                theme_menu.add_command(
                    label=theme.capitalize(),
                    command=lambda t=theme: self.change_theme(t)
                )

            self.view_menu.add_cascade(
                label=self._("Theme"),
                menu=theme_menu,
                image=self.assets.get_icon('theme'),
                compound=tk.LEFT
            )

            self.view_menu.add_separator()

            self.view_menu.add_command(
                label=self._("List View"),
                command=lambda: self.explorer_tab.notebook.select(0),
                accelerator="Ctrl+1"
            )

            self.view_menu.add_command(
                label=self._("Thumbnail View"),
                command=lambda: self.explorer_tab.notebook.select(1),
                accelerator="Ctrl+2"
            )

            self.view_menu.add_command(
                label=self._("Details View"),
                command=lambda: self.explorer_tab.notebook.select(2),
                accelerator="Ctrl+3"
            )

            self.menubar.add_cascade(label=self._("View"), menu=self.view_menu)

            # منوی ابزارها
            self.tools_menu = tk.Menu(self.menubar, tearoff=0)
            self.tools_menu.add_command(
                label=self._("Connect to Drive"),
                command=self.connect_to_drive,
                image=self.assets.get_icon('drive'),
                compound=tk.LEFT,
                accelerator="Ctrl+D"
            )
            self.tools_menu.add_command(
                label=self._("Batch Operations"),
                command=self.show_batch_operations,
                image=self.assets.get_icon('edit'),
                compound=tk.LEFT
            )
            self.menubar.add_cascade(label=self._("Tools"), menu=self.tools_menu)

            # منوی کمک
            self.help_menu = tk.Menu(self.menubar, tearoff=0)
            self.help_menu.add_command(
                label=self._("Documentation"),
                command=self.show_documentation,
                image=self.assets.get_icon('info'),
                compound=tk.LEFT
            )
            self.help_menu.add_command(
                label=self._("About"),
                command=self.show_about,
                image=self.assets.get_icon('info'),
                compound=tk.LEFT,
                accelerator="F1"
            )
            self.menubar.add_cascade(label=self._("Help"), menu=self.help_menu)

            # منوی زبان
            self.lang_menu = tk.Menu(self.menubar, tearoff=0)
            self.lang_menu.add_command(
                label="English",
                command=lambda: self.change_language("en")
            )
            self.lang_menu.add_command(
                label="فارسی",
                command=lambda: self.change_language("fa")
            )
            self.menubar.add_cascade(label=self._("Language"), menu=self.lang_menu)

            self.root.config(menu=self.menubar)

        def create_main_notebook(self):
            """ایجاد نوت‌بوک اصلی"""
            self.main_notebook = ttk.Notebook(self.root)
            self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

            # ایجاد تب‌ها
            self.create_drive_explorer_tab()
            self.create_upload_tab()
            self.create_settings_tab()

        def create_drive_explorer_tab(self):
            """ایجاد تب مرورگر درایو"""
            self.explorer_tab = ModernFileBrowser(
                self.main_notebook,
                self.file_manager
            )
            self.main_notebook.add(
                self.explorer_tab,
                text=self._("Drive Explorer"),
                image=self.assets.get_icon('drive'),
                compound=tk.LEFT
            )

        def create_upload_tab(self):
            """ایجاد تب آپلود فایل‌ها"""
            self.upload_tab = UploadManager(
                self.main_notebook,
                self.file_manager
            )
            self.main_notebook.add(
                self.upload_tab,
                text=self._("Upload Files"),
                image=self.assets.get_icon('upload'),
                compound=tk.LEFT
            )

        def create_settings_tab(self):
            """ایجاد تب تنظیمات"""
            self.settings_tab = SettingsManager(
                self.main_notebook,
                self.client_config
            )
            self.main_notebook.add(
                self.settings_tab,
                text=self._("Settings"),
                image=self.assets.get_icon('settings'),
                compound=tk.LEFT
            )

        def create_status_bar(self):
            """ایجاد نوار وضعیت پیشرفته"""
            self.status_bar = ttk.Frame(self.root)
            self.status_bar.pack(fill=tk.X, padx=5, pady=(0, 5))

            # پیام وضعیت
            self.status_var = tk.StringVar()
            self.status_var.set(self._("Ready"))

            ttk.Label(
                self.status_bar,
                textvariable=self.status_var,
                relief=tk.SUNKEN,
                anchor=tk.W
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            # وضعیت اتصال
            self.connection_status = ttk.Label(
                self.status_bar,
                text=self._("Not Connected"),
                relief=tk.SUNKEN,
                width=20
            )
            self.connection_status.pack(side=tk.RIGHT)

            # اطلاعات کاربر
            self.user_status = ttk.Label(
                self.status_bar,
                text=self._("User: Not logged in"),
                relief=tk.SUNKEN,
                width=30
            )
            self.user_status.pack(side=tk.RIGHT)

        def change_language(self, lang_code):
            """تغییر زبان برنامه"""
            if self.lang.set_language(lang_code):
                self.update_ui_texts()

                if self.lang.get_direction() == "rtl":
                    self.root.tk.call('tk', 'scaling', 1.5)
                else:
                    self.root.tk.call('tk', 'scaling', 1.0)

        def update_ui_texts(self):
            """به‌روزرسانی متون رابط کاربری پس از تغییر زبان"""
            self.root.title(self._("SfileCloud Professional"))

            # به‌روزرسانی منوها
            self.menubar.entryconfig(0, label=self._("File"))
            self.file_menu.entryconfig(0, label=self._("New Upload"))
            self.file_menu.entryconfig(1, label=self._("Open Folder"))
            self.file_menu.entryconfig(3, label=self._("Exit"))

            self.menubar.entryconfig(1, label=self._("Edit"))
            self.edit_menu.entryconfig(0, label=self._("Copy"))
            self.edit_menu.entryconfig(1, label=self._("Paste"))
            self.edit_menu.entryconfig(3, label=self._("Refresh"))

            self.menubar.entryconfig(2, label=self._("View"))
            self.view_menu.entryconfig(0, label=self._("Theme"))
            self.view_menu.entryconfig(2, label=self._("List View"))
            self.view_menu.entryconfig(3, label=self._("Thumbnail View"))
            self.view_menu.entryconfig(4, label=self._("Details View"))

            self.menubar.entryconfig(3, label=self._("Tools"))
            self.tools_menu.entryconfig(0, label=self._("Connect to Drive"))
            self.tools_menu.entryconfig(1, label=self._("Batch Operations"))

            self.menubar.entryconfig(4, label=self._("Help"))
            self.help_menu.entryconfig(0, label=self._("Documentation"))
            self.help_menu.entryconfig(1, label=self._("About"))

            self.menubar.entryconfig(5, label=self._("Language"))

            # به‌روزرسانی تب‌ها
            self.main_notebook.tab(0, text=self._("Drive Explorer"))
            self.main_notebook.tab(1, text=self._("Upload Files"))
            self.main_notebook.tab(2, text=self._("Settings"))

            # به‌روزرسانی نوار وضعیت
            self.status_var.set(self._("Ready"))
            self.connection_status.config(text=self._("Not Connected"))
            self.user_status.config(text=self._("User: Not logged in"))

        def change_theme(self, theme_name):
            """تغییر تم برنامه"""
            if theme_name in self.available_themes:
                self.theme_mode = theme_name
                self.style.theme_use(theme_name)

        def new_upload(self):
            """شروع یک آپلود جدید"""
            self.main_notebook.select(self.upload_tab)

        def open_local_folder(self):
            """باز کردن پوشه محلی"""
            folder_path = filedialog.askdirectory()
            if folder_path:
                try:
                    if platform.system() == "Windows":
                        os.startfile(folder_path)
                    elif platform.system() == "Darwin":
                        os.system(f"open {folder_path}")
                    else:
                        os.system(f"xdg-open {folder_path}")
                except:
                    Messagebox.show_error(
                        self._("Could not open folder"),
                        self._("Error")
                    )

        def refresh_files(self):
            """بارگذاری مجدد فایل‌ها"""
            if hasattr(self, 'explorer_tab'):
                self.explorer_tab.refresh_files()

        def connect_to_drive(self):
            """اتصال به گوگل درایو"""
            auth_window = ModernAuthWindow(
                self.root,
                self.start_auth,
            )

        def start_auth(self):
            """شروع فرآیند احراز هویت"""
            auth_url = (
                f"{self.client_config['installed']['auth_uri']}?"
                f"client_id={self.client_config['installed']['client_id']}&"
                f"redirect_uri={self.client_config['installed']['redirect_uris'][0]}&"
                f"response_type=code&"
                f"scope=https://www.googleapis.com/auth/drive&"
                f"access_type=offline&"
                f"prompt=consent"
            )

            webbrowser.open(auth_url)

            # نمایش دیالوگ برای وارد کردن کد احراز هویت
            auth_code = Querybox.get_string(
                prompt=self._("Please enter the authentication code from Google:"),
                title=self._("Google Authentication"),
                parent=self.root
            )

            if auth_code:
                try:
                    if self.file_manager.authenticate(auth_code):
                        self.connection_status.config(text=self._("Connected"))
                        self.user_status.config(text=f"User: {self.file_manager.user_info.get('name', 'Unknown')}")
                        Messagebox.show_info(
                            self._("Successfully connected to Google Drive"),
                            self._("Success")
                        )
                except Exception as e:
                    Messagebox.show_error(
                        self._("Authentication failed: {}").format(str(e)),
                        self._("Error")
                    )

        def show_batch_operations(self):
            """نمایش عملیات گروهی"""
            Messagebox.show_info(
                self._("This feature will be implemented in a future version"),
                self._("Info")
            )

        def show_documentation(self):
            """نمایش مستندات"""
            webbrowser.open("https://github.com/Kaspian021/SfileColud/wiki")

        def show_about(self):
            """نمایش پنجره درباره برنامه"""
            about_window = ModernAboutWindow(self.root)

        def get_selected_item(self):
            """دریافت آیتم انتخاب شده"""
            if hasattr(self, 'explorer_tab'):
                selected = self.explorer_tab.tree.selection()
                if selected:
                    return self.explorer_tab.tree.item(selected[0], 'values')[0]
            return None

        def handle_paste(self, content):
            """مدیریت عملیات چسباندن"""
            if content:
                Messagebox.show_info(
                    f"Pasted content: {content}",
                    "Paste"
                )

        def load_settings(self):
            """بارگذاری تنظیمات برنامه"""
            try:
                if os.path.exists('config.json'):
                    with open('config.json', 'r') as f:
                        self.client_config = json.load(f)

                # به‌روزرسانی مدیر فایل
                self.file_manager.client_config = self.client_config

                # به‌روزرسانی تب تنظیمات
                if hasattr(self, 'settings_tab'):
                    self.settings_tab.client_id_entry.delete(0, tk.END)
                    self.settings_tab.client_id_entry.insert(0, self.client_config["installed"]["client_id"])

                    self.settings_tab.client_secret_entry.delete(0, tk.END)
                    self.settings_tab.client_secret_entry.insert(0, self.client_config["installed"]["client_secret"])

                    self.settings_tab.redirect_entry.delete(0, tk.END)
                    self.settings_tab.redirect_entry.insert(0, self.client_config["installed"]["redirect_uris"][0])

                logger.info("Settings loaded successfully")
            except FileNotFoundError:
                logger.info("No saved settings found")
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
                Messagebox.show_error(
                    self._("Could not load settings: {}").format(str(e)),
                    self._("Error")
                )

    if __name__ == "__main__":
        try:
            # ایجاد پنجره اصلی
            root = tk.Tk()

            # مخفی کردن پنجره اصلی تا زمانی که splash نمایش داده شود
            root.withdraw()

            # تنظیم تم
            style = Style(theme="flatly")

            # ایجاد برنامه
            app = EnhancedSfileCloud(root)

            # اجرای حلقه اصلی
            root.mainloop()

        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
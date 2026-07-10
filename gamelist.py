import ctypes
import json
import os
import shutil
import sys
import pypinyin
import re
import tkinter as tk
import winreg
from tkinter import ttk, filedialog
import xml.etree.ElementTree as ET
from tkinter.messagebox import showwarning
from xml.dom import minidom
import datetime
from typing import Dict

ver = "v1.5.0"  # 更新版本号


class CommonUtils:
    """公共工具类"""

    @staticmethod
    def get_available_font(font_list, test_widget=None):
        """从字体列表中获取第一个可用的字体"""
        if test_widget is None:
            test_widget = tk.Tk()
            test_widget.withdraw()  # 隐藏测试窗口

        try:
            for font_name in font_list:
                try:
                    # 尝试创建一个临时标签来测试字体
                    temp = tk.Label(test_widget, text="测试", font=(font_name, 10))
                    temp.destroy()
                    return font_name
                except tk.TclError:
                    continue
            return "Arial"  # 默认回退字体
        except:
            return "Arial"
        finally:
            if test_widget:
                test_widget.destroy()

    @staticmethod
    def setup_multilingual_font(lang_code):
        """设置多语言支持的字体"""
        # 根据系统语言选择字体优先级
        if lang_code == "zh-CN":  # 简体中文
            font_families = ["Microsoft YaHei UI", "Microsoft YaHei", "SimSun", "Arial"]
        elif lang_code == "zh-TW":  # 繁体中文
            font_families = ["Microsoft JhengHei UI", "Microsoft JhengHei", "PMingLiU", "Arial"]
        else:  # 其他语言
            font_families = ["Segoe UI", "Microsoft YaHei UI", "Arial"]

        # 找到第一个可用的字体
        return CommonUtils.get_available_font(font_families)

    @staticmethod
    def setup_common_styles(font_family):
        """设置通用样式"""
        style = ttk.Style()

        # 清除现有样式
        style.theme_use('clam')

        # 配置通用样式
        style.configure(".", font=(font_family, 9))
        style.configure("Title.TLabel", font=(font_family, 16, "bold"), foreground="#2c3e50")
        style.configure("Subtitle.TLabel", font=(font_family, 9), foreground="#7f8c8d")
        style.configure("Action.TButton", font=(font_family, 9, "bold"))
        style.configure("Section.TLabelframe", font=(font_family, 10, "bold"))
        style.configure("Section.TLabelframe.Label", font=(font_family, 10, "bold"))
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor='#ecf0f1',
                        background='#3498db',
                        thickness=12)
        style.configure("Success.TButton", font=(font_family, 9, "bold"),
                        background="#27ae60", foreground="white")
        style.configure("Warning.TButton", font=(font_family, 9, "bold"),
                        background="#e74c3c", foreground="white")

        return style

    @staticmethod
    def fix_xml_special_chars(content):
        """修复XML中的特殊字符"""
        # 首先修复 & 字符（必须最先处理）
        content = content.replace('&', '&amp;')

        # 修复双重转义的问题
        content = content.replace('&amp;amp;', '&amp;')

        return content

    @staticmethod
    def escape_xml_text(text):
        """转义XML文本中的特殊字符"""
        if not text:
            return text

        try:
            # 先尝试使用xml.sax的转义方法
            import xml.sax.saxutils
            escaped_text = xml.sax.saxutils.escape(text)
            return escaped_text
        except:
            # 备用方法：手动转义
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            text = text.replace('"', '&quot;')
            text = text.replace("'", '&apos;')
            return text

    @staticmethod
    def unescape_xml_text(text):
        """反转义XML文本"""
        if not text:
            return text

        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        return text

    @staticmethod
    def center_window(window, width, height):
        """使窗口在屏幕中央显示"""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        width = min(width, screen_width)
        height = min(height, screen_height)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def center_dialog(dialog, parent_window):
        """居中显示对话框"""
        dialog.update_idletasks()
        try:
            prog_path = os.path.abspath(__file__)
            ico_path = os.path.join(os.path.dirname(prog_path), 'icon', 'icon.ico')
            dialog.iconbitmap(ico_path)
        except:
            pass

        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()

        # 使用父窗口的尺寸和位置来计算居中位置
        x = (parent_window.winfo_width() // 2) - (width // 2) + parent_window.winfo_x()
        y = (parent_window.winfo_height() // 2) - (height // 2) + parent_window.winfo_y()

        dialog.geometry(f"+{x}+{y}")


class Translator:
    def __init__(self):
        self.lang_data: Dict[str, str] = {}
        self.lang_code = "en-US"  # 默认语言
        self.available_languages = self.get_available_languages()

    def get_available_languages(self):
        """获取可用的语言列表"""
        base_dir = self.get_base_directory()
        lang_dir = os.path.join(base_dir, "lang")

        # 如果 languages 文件夹不存在，尝试创建
        if not os.path.exists(lang_dir):
            try:
                os.makedirs(lang_dir, exist_ok=True)
            except:
                pass

        languages = []

        if os.path.exists(lang_dir):
            for file in os.listdir(lang_dir):
                if file.endswith('.json'):
                    lang_code = file.replace('.json', '')
                    # 获取语言显示名称
                    display_name = self.get_language_display_name(lang_code)
                    languages.append((lang_code, display_name))

        # 如果没有找到任何语言文件，添加默认的英语
        if not languages:
            languages = [("en-US", "English")]

        return languages

    def get_base_directory(self):
        """获取程序所在的基础目录"""
        try:
            # 如果是打包后的可执行文件
            if getattr(sys, 'frozen', False):
                # 可执行文件所在的目录
                base_path = os.path.dirname(sys.executable)
            else:
                # 脚本文件所在的目录
                base_path = os.path.dirname(os.path.abspath(__file__))
            return base_path
        except:
            # 如果以上方法都失败，使用当前工作目录
            return os.getcwd()

    def get_language_display_name(self, lang_code):
        """获取语言的显示名称"""
        language_names = {
            "en-US": "English",
            "zh-CN": "简体中文",
            "zh-TW": "繁體中文",
            "ja-JP": "日本語",
            "ko-KR": "한국어",
            "fr-FR": "Français",
            "ru-RU": "Русский",
            "de-DE": "Deutsch",
            "pt-BR": "Português-BR",
            "es-ES": "Español"
        }
        return language_names.get(lang_code, lang_code)

    def load_language(self, lang_code: str) -> None:
        base_dir = self.get_base_directory()
        lang_file = os.path.join(base_dir, "lang", f"{lang_code}.json")

        # 如果指定的语言文件不存在，尝试加载英语
        if not os.path.exists(lang_file):
            lang_file = os.path.join(base_dir, "lang", "en-US.json")

        # 如果英语文件也不存在，使用内置的默认语言
        if not os.path.exists(lang_file):
            self._load_default_language()
            return

        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                self.lang_data = json.load(f)
            self.lang_code = lang_code
        except Exception as e:
            print(f"Error loading language file: {e}")
            # 加载失败时使用默认语言
            self._load_default_language()

    def _load_default_language(self):
        """加载内置的默认语言（英语）"""
        self.lang_data = {
            "File Operations": "File Operations",
            "Game Information": "Game Information",
            "Search:": "Search:",
            "Reset": "Reset",
            "Name": "Name",
            "Path": "Path",
            "Image": "Image",
            "Video": "Video",
            "Description": "Description",
            "Edit Game": "Edit Game",
            "Browse...": "Browse...",
            "Update": "Update",
            "Add New": "Add New",
            "Delete": "Delete",
            "Clear": "Clear",
            "Ready": "Ready",
            # 添加其他必要的翻译键...
        }
        self.lang_code = "en-US"

    def t(self, key: str, **kwargs) -> str:
        message = self.lang_data.get(key, key)
        try:
            return message.format(**kwargs)
        except KeyError as e:
            return message


class SettingsManager:
    def __init__(self):
        # 注册表路径
        self.reg_path = r"Software\GameToolCollection"
        self.settings = self.load_settings()

    def load_settings(self):
        """从注册表加载设置"""
        default_settings = {
            "language": "en-US"
        }

        try:
            # 尝试打开注册表键
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path)

            settings = default_settings.copy()
            try:
                i = 0
                while True:
                    # 枚举所有值
                    name, value, type = winreg.EnumValue(key, i)
                    if name in settings:
                        settings[name] = value
                    i += 1
            except WindowsError:
                # 枚举结束
                pass

            winreg.CloseKey(key)
            return settings

        except WindowsError:
            # 键不存在，返回默认设置
            return default_settings.copy()

    def save_settings(self):
        """保存设置到注册表"""
        try:
            # 创建或打开注册表键
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.reg_path)

            # 保存每个设置项
            for setting_key, value in self.settings.items():
                winreg.SetValueEx(key, setting_key, 0, winreg.REG_SZ, str(value))

            winreg.CloseKey(key)
            return True

        except Exception as e:
            print(f"Error saving settings to registry: {e}")
            return False

    def get(self, key, default=None):
        """获取设置值"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """设置值"""
        self.settings[key] = value
        return self.save_settings()


class ToolTip:
    def __init__(self, widget, text, font_family="Arial"):
        self.widget = widget
        self.text = text
        self.font_family = font_family
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

        # 绑定事件
        widget.bind('<Enter>', self.enter)
        widget.bind('<Leave>', self.leave)
        widget.bind('<Motion>', self.motion)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def motion(self, event=None):
        self.x = event.x_root + 20
        self.y = event.y_root + 10

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)  # 500ms后显示

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self):
        if self.tip_window:
            return

        # 创建提示窗口
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # 无边框
        tw.wm_geometry(f"+{self.x}+{self.y}")

        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=(self.font_family, 10))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class BaseFrame(ttk.Frame):
    """基础框架类，提供通用功能"""

    def __init__(self, parent, translator: Translator):
        super().__init__(parent)
        self.t = translator
        self.parent = parent
        self.font_family = CommonUtils.setup_multilingual_font(self.t.lang_code)
        CommonUtils.setup_common_styles(self.font_family)

    def create_centered_dialog(self, title, message, dialog_type="info"):
        """创建居中对话框"""
        t = self.t
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient()
        dialog.resizable(False, False)

        # 设置对话框样式
        if dialog_type == "info":
            icon = "ℹ️"
            bg_color = "#e8f5e8"
            title_color = "#2e7d32"
        elif dialog_type == "warning":
            icon = "⚠️"
            bg_color = "#fff8e1"
            title_color = "#f57c00"
        elif dialog_type == "error":
            icon = "❌"
            bg_color = "#ffebee"
            title_color = "#c62828"
        else:  # askyesno
            icon = "❓"
            bg_color = "#e3f2fd"
            title_color = "#1565c0"

        dialog.configure(bg=bg_color)

        # 创建内容框架
        content_frame = ttk.Frame(dialog, padding="20")
        content_frame.pack(fill='both', expand=True)

        # 图标和标题
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 15))

        icon_label = ttk.Label(header_frame, text=icon, font=(self.font_family, 15),
                               foreground=title_color)
        icon_label.pack(side='left', padx=(0, 10))

        title_label = ttk.Label(header_frame, text=title, font=(self.font_family, 12, "bold"),
                                foreground=title_color)
        title_label.pack(side='left')

        # 消息内容
        message_frame = ttk.Frame(content_frame)
        message_frame.pack(fill='x', pady=(0, 20))

        message_label = ttk.Label(message_frame, text=message, font=(self.font_family, 10),
                                  justify='left', wraplength=400)
        message_label.pack(anchor='w')

        # 按钮区域
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x')

        if dialog_type == "askyesno":
            self.dialog_result = None
            btn_no = ttk.Button(button_frame, text=t.t("Cancel"),
                                command=lambda: self.set_dialog_result(dialog, False),
                                width=10)
            btn_no.pack(side='right', padx=(10, 0))
            btn_yes = ttk.Button(button_frame, text=t.t("Ok"),
                                 command=lambda: self.set_dialog_result(dialog, True),
                                 width=10)
            btn_yes.pack(side='right')
        else:
            ok_button = ttk.Button(button_frame, text=t.t("Ok"),
                                   command=dialog.destroy, width=12)
            ok_button.pack(side='right')

        # 居中对话框
        CommonUtils.center_dialog(dialog, self.winfo_toplevel())

        # 设置对话框模态
        dialog.grab_set()

        if dialog_type == "askyesno":
            self.wait_window(dialog)
            return self.dialog_result
        else:
            self.wait_window(dialog)

    def set_dialog_result(self, dialog, result):
        """设置对话框结果并关闭"""
        self.dialog_result = result
        dialog.destroy()


class GamelistEditorFrame(BaseFrame):
    def __init__(self, parent, translator: Translator):
        super().__init__(parent, translator)
        self.current_file = None
        self.games = []
        self.filtered_games = []
        self.tree = None
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        t = self.t
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 文件操作区域
        file_section = ttk.LabelFrame(main_frame, text=f"{t.t('File Operations')}", padding="10",
                                      style="Section.TLabelframe")
        file_section.pack(fill='x', pady=(0, 10))

        file_frame = ttk.Frame(file_section)
        file_frame.pack(fill='x', pady=5)

        ttk.Label(file_frame, text=f"{t.t('Open gamelist.xml')}:").pack(side='left', padx=5)
        self.open_entry = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.open_entry, state='disable').pack(side='left', fill='x', expand=True, padx=5)

        ttk.Button(file_frame, text=f"{t.t('Open')}",
                   command=self.open_file, width=15, style="Action.TButton").pack(side='left', padx=5)
        ttk.Button(file_frame, text=f"{t.t('Save')}",
                   command=self.save_file, width=15, style="Action.TButton").pack(side='left', padx=5)
        ttk.Button(file_frame, text=f"{t.t('Save As')}",
                   command=self.save_as_file, width=15, style="Action.TButton").pack(side='left', padx=5)

        # 编辑区域
        edit_section = ttk.LabelFrame(main_frame, text=f"{t.t('Edit Game')}", padding="10",
                                      style="Section.TLabelframe")
        edit_section.pack(fill='x', pady=(0, 10))

        # 名称
        name_frame = ttk.Frame(edit_section)
        name_frame.pack(fill='x', pady=2)
        ttk.Label(name_frame, text=t.t("Name:"), width=10).pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var).pack(side='left', fill='x', expand=True, padx=5)

        # 路径
        path_frame = ttk.Frame(edit_section)
        path_frame.pack(fill='x', pady=2)
        ttk.Label(path_frame, text=t.t("Path:"), width=10).pack(side='left')
        self.path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.path_var).pack(side='left', fill='x', expand=True, padx=5)

        # 图片
        image_frame = ttk.Frame(edit_section)
        image_frame.pack(fill='x', pady=2)
        ttk.Label(image_frame, text=t.t("Image:"), width=10).pack(side='left')
        self.image_var = tk.StringVar()
        ttk.Entry(image_frame, textvariable=self.image_var).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(image_frame, text=f"{t.t('Browse...')}",
                   command=self.browse_image, width=15).pack(side='right')

        # 视频
        video_frame = ttk.Frame(edit_section)
        video_frame.pack(fill='x', pady=2)
        ttk.Label(video_frame, text=t.t("Video:"), width=10).pack(side='left')
        self.video_var = tk.StringVar()
        ttk.Entry(video_frame, textvariable=self.video_var).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(video_frame, text=f"{t.t('Browse...')}",
                   command=self.browse_video, width=15).pack(side='right')

        # 分类
        genre_frame = ttk.Frame(edit_section)
        genre_frame.pack(fill='x', pady=2)
        ttk.Label(genre_frame, text=t.t("Genre:"), width=10).pack(side='left')
        self.genre_var = tk.StringVar()
        ttk.Entry(genre_frame, textvariable=self.genre_var).pack(side='left', fill='x', expand=True, padx=5)

        # 描述
        desc_frame = ttk.Frame(edit_section)
        desc_frame.pack(fill='x', pady=2)
        ttk.Label(desc_frame, text=t.t("Description:"), width=10).pack(side='left')
        self.desc_var = tk.StringVar()
        ttk.Entry(desc_frame, textvariable=self.desc_var).pack(side='left', fill='x', expand=True, padx=5)

        # 按钮区域
        button_frame = ttk.Frame(edit_section)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text=f"{t.t('Update')}",
                   command=self.update_game, width=15, style="Action.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text=f"{t.t('Add New')}",
                   command=self.add_game, width=15, style="Action.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text=f"{t.t('Delete')}",
                   command=self.delete_game, width=15, style="Action.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text=f"{t.t('Clear')}",
                   command=self.clear_form, width=15, style="Action.TButton").pack(side='left')
        ttk.Button(button_frame, text=f"{t.t('Integrity Check')}",
                   command=self.check_integrity, width=15, style="Action.TButton").pack(side='left', padx=5)

        # 游戏信息区域
        info_section = ttk.LabelFrame(main_frame, text=f"{t.t('Game Information')}", padding="10",
                                      style="Section.TLabelframe")
        info_section.pack(fill='both', expand=True)

        # 搜索框
        search_frame = ttk.Frame(info_section)
        search_frame.pack(fill='x', pady=5)

        ttk.Label(search_frame, text=f"{t.t('Search:')}").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.search_games)

        ttk.Button(search_frame, text=f"{t.t('Reset')}",
                   command=self.refresh_list).pack(side='left', padx=5)

        # 游戏列表
        list_frame = ttk.Frame(info_section)
        list_frame.pack(fill='both', expand=True, pady=5)

        # 创建树形视图
        columns = ('name', 'path', 'image', 'video', 'genre', 'desc')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        # 定义列
        self.tree.heading('name', text=t.t('Name'))
        self.tree.heading('path', text=t.t('Path'))
        self.tree.heading('image', text=t.t('Image'))
        self.tree.heading('video', text=t.t('Video'))
        self.tree.heading('genre', text=t.t('Genre'))
        self.tree.heading('desc', text=t.t('Description'))

        # 设置列宽
        self.tree.column('name', width=150)
        self.tree.column('path', width=150)
        self.tree.column('image', width=150)
        self.tree.column('video', width=150)
        self.tree.column('genre', width=100)
        self.tree.column('desc', width=200)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

        # 状态栏
        self.status_var = tk.StringVar(value=t.t("Ready"))
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken', anchor='w')
        status_label.pack(fill='x', side='bottom')

    def open_file(self):
        """打开gamelist.xml文件"""
        t = self.t
        filename = filedialog.askopenfilename(
            title=t.t("Open gamelist.xml"),
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.current_file = filename
                self.parse_gamelist(filename)
                self.open_entry.set(self.current_file)
                self.status_var.set(f"{t.t('Loaded:')} {os.path.basename(filename)} - {len(self.games)} {t.t('games')}")
            except Exception as e:
                self.create_centered_dialog(t.t("Error"), f"{t.t('Error loading file:')} {str(e)}", "error")

    def parse_gamelist(self, filename):
        """解析gamelist.xml文件，处理XML特殊字符"""
        t = self.t
        try:
            # 预处理XML文件，转义特殊字符
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # 临时修复常见的未转义字符
            content = CommonUtils.fix_xml_special_chars(content)

            # 使用修复后的内容进行解析
            root = ET.fromstring(content)

            self.games = []
            for game_elem in root.findall('game'):
                game = {
                    'name': self.get_safe_text(game_elem.find('name')),
                    'path': self.get_safe_text(game_elem.find('path')),
                    'image': self.get_safe_text(game_elem.find('image')),
                    'video': self.get_safe_text(game_elem.find('video')),
                    'genre': self.get_safe_text(game_elem.find('genre')),
                    'desc': self.get_safe_text(game_elem.find('desc')),
                    'element': game_elem  # 保存原始元素引用
                }
                self.games.append(game)

            self.filtered_games = self.games.copy()
            self.refresh_treeview()

        except ET.ParseError as e:
            # 如果解析失败，尝试更宽松的解析方式
            self.try_alternative_parsing(filename, e)
        except Exception as e:
            self.create_centered_dialog(t.t("Error"), f"{t.t('Error parsing XML file:')} {str(e)}", "error")

    def get_safe_text(self, element):
        """安全获取元素文本，处理None情况"""
        if element is not None and element.text is not None:
            return element.text
        return ""

    def try_alternative_parsing(self, filename, original_error):
        """尝试替代的解析方法"""
        t = self.t
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 手动修复内容
            content = self.manual_xml_repair(content)

            # 再次尝试解析
            root = ET.fromstring(content)

            self.games = []
            for game_elem in root.findall('game'):
                game = {
                    'name': self.get_safe_text(game_elem.find('name')),
                    'path': self.get_safe_text(game_elem.find('path')),
                    'image': self.get_safe_text(game_elem.find('image')),
                    'video': self.get_safe_text(game_elem.find('video')),
                    'genre': self.get_safe_text(game_elem.find('genre')),
                    'desc': self.get_safe_text(game_elem.find('desc')),
                    'element': game_elem
                }
                self.games.append(game)

            self.filtered_games = self.games.copy()
            self.refresh_treeview()

            # 提示用户文件已被修复
            self.status_var.set(f"{t.t('File loaded with automatic repairs')} - {len(self.games)} {t.t('games')}")

        except Exception as e:
            # 如果所有方法都失败，显示详细错误信息
            error_msg = f"{t.t('Failed to parse XML file:')}\n\n{t.t('Original error:')} {original_error}\n{t.t('Repair error:')} {e}"
            self.create_centered_dialog(t.t("Error"), error_msg, "error")

    def manual_xml_repair(self, content):
        """手动修复XML内容"""
        # 移除XML声明之前的任何内容
        if '<?xml' in content:
            content = content[content.find('<?xml'):]

        # 确保根元素正确
        if '<gameList>' not in content:
            # 尝试找到第一个game元素并包装在gameList中
            if '<game>' in content:
                content = f"<gameList>\n{content}\n</gameList>"

        # 修复未闭合的标签
        lines = content.split('\n')
        repaired_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 修复简单的标签问题
            if line.startswith('<game>') and not line.endswith('</game>'):
                # 这是一个开始标签，需要找到对应的结束标签
                repaired_lines.append(line)
            elif line.startswith('</game>'):
                repaired_lines.append(line)
            elif line.startswith('<') and '>' in line and not line.startswith('</'):
                # 这是一个完整的标签
                repaired_lines.append(line)
            elif any(tag in line for tag in ['<name>', '<path>', '<image>', '<video>', '<genre>', '<desc>']):
                # 内容行，确保特殊字符被转义
                line = CommonUtils.fix_xml_special_chars(line)
                repaired_lines.append(line)

        return '\n'.join(repaired_lines)

    def update_game(self):
        """更新游戏信息（添加XML转义）"""
        t = self.t
        if not hasattr(self, 'selected_game'):
            self.create_centered_dialog(t.t("Warning"), t.t("Please select a game to update"), 'warning')
            return

        # 获取并转义表单数据
        name = CommonUtils.escape_xml_text(self.name_var.get())
        path = CommonUtils.escape_xml_text(self.path_var.get())
        image = CommonUtils.escape_xml_text(self.image_var.get())
        video = CommonUtils.escape_xml_text(self.video_var.get())
        genre = CommonUtils.escape_xml_text(self.genre_var.get())
        desc = CommonUtils.escape_xml_text(self.desc_var.get())

        # 更新游戏数据（存储转义后的值）
        self.selected_game['name'] = name
        self.selected_game['path'] = path
        self.selected_game['image'] = image
        self.selected_game['video'] = video
        self.selected_game['genre'] = genre
        self.selected_game['desc'] = desc

        # 更新XML元素
        game_elem = self.selected_game['element']

        # 更新name
        name_elem = game_elem.find('name')
        if name_elem is None:
            name_elem = ET.SubElement(game_elem, 'name')
        name_elem.text = name

        # 更新path
        path_elem = game_elem.find('path')
        if path_elem is None:
            path_elem = ET.SubElement(game_elem, 'path')
        path_elem.text = path

        # 更新图片（如果存在）
        image_elem = game_elem.find('image')
        if image:
            if image_elem is None:
                image_elem = ET.SubElement(game_elem, 'image')
            image_elem.text = image
        elif image_elem is not None:
            game_elem.remove(image_elem)

        # 更新视频（如果存在）
        video_elem = game_elem.find('video')
        if video:
            if video_elem is None:
                video_elem = ET.SubElement(game_elem, 'video')
            video_elem.text = video
        elif video_elem is not None:
            game_elem.remove(video_elem)

        # 更新分类
        genre_elem = game_elem.find('genre')
        if genre_elem is None:
            genre_elem = ET.SubElement(game_elem, 'genre')
        genre_elem.text = genre

        # 更新描述
        desc_elem = game_elem.find('desc')
        if desc_elem is None:
            desc_elem = ET.SubElement(game_elem, 'desc')
        desc_elem.text = desc

        self.refresh_treeview()
        self.status_var.set(t.t("Game updated successfully"))

    def add_game(self):
        """添加新游戏（添加XML转义）"""
        t = self.t

        # 获取并转义表单数据
        name = CommonUtils.escape_xml_text(self.name_var.get())
        path = CommonUtils.escape_xml_text(self.path_var.get())
        image = CommonUtils.escape_xml_text(self.image_var.get())
        video = CommonUtils.escape_xml_text(self.video_var.get())
        genre = CommonUtils.escape_xml_text(self.genre_var.get())
        desc = CommonUtils.escape_xml_text(self.desc_var.get())

        if not name or not path:
            self.create_centered_dialog(t.t("Warning"), t.t("Name and Path are required"), "warning")
            return

        # 创建新的游戏元素
        game_elem = ET.Element('game')
        ET.SubElement(game_elem, 'name').text = name
        ET.SubElement(game_elem, 'path').text = path

        if image:
            ET.SubElement(game_elem, 'image').text = image

        if video:
            ET.SubElement(game_elem, 'video').text = video

        if genre:
            ET.SubElement(game_elem, 'genre').text = genre

        if desc:
            ET.SubElement(game_elem, 'desc').text = desc

        # 添加到数据列表
        new_game = {
            'name': name,
            'path': path,
            'image': image,
            'video': video,
            'genre': genre,
            'desc': desc,
            'element': game_elem
        }

        self.games.append(new_game)
        self.filtered_games = self.games.copy()
        self.refresh_treeview()
        self.clear_form()
        self.status_var.set(t.t("Game added successfully"))

    def on_item_select(self, event):
        """当选择树形视图中的项目时（添加XML反转义）"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')

            # 找到对应的游戏数据
            index = self.tree.index(item)
            if index < len(self.filtered_games):
                self.selected_game = self.filtered_games[index]

                # 更新表单（显示反转义后的值）
                self.name_var.set(CommonUtils.unescape_xml_text(self.selected_game['name']))
                self.path_var.set(CommonUtils.unescape_xml_text(self.selected_game['path']))
                self.image_var.set(CommonUtils.unescape_xml_text(self.selected_game['image']))
                self.video_var.set(CommonUtils.unescape_xml_text(self.selected_game['video']))
                self.genre_var.set(CommonUtils.unescape_xml_text(self.selected_game['genre']))
                self.desc_var.set(CommonUtils.unescape_xml_text(self.selected_game['desc']))

    def refresh_treeview(self):
        """刷新树形视图（显示反转义后的值）"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加新数据（显示给用户的是反转义后的值）
        for game in self.filtered_games:
            self.tree.insert('', 'end', values=(
                CommonUtils.unescape_xml_text(game['name']),
                CommonUtils.unescape_xml_text(game['path']),
                CommonUtils.unescape_xml_text(game['image']),
                CommonUtils.unescape_xml_text(game['video']),
                CommonUtils.unescape_xml_text(game['genre']),
                CommonUtils.unescape_xml_text(game['desc'])
            ))

    def search_games(self, event=None):
        """搜索游戏"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filtered_games = self.games.copy()
        else:
            self.filtered_games = [
                game for game in self.games
                if search_term in game['name'].lower() or search_term in game['desc'].lower()
            ]
        self.refresh_treeview()

    def refresh_list(self):
        """刷新列表"""
        self.filtered_games = self.games.copy()
        self.refresh_treeview()
        self.search_var.set("")

    def browse_image(self):
        """浏览图片文件"""
        filename = filedialog.askopenfilename(
            title=self.t.t("Select image file"),
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        if filename:
            self.image_var.set(f"./{os.path.basename(filename)}")

    def browse_video(self):
        """浏览视频文件"""
        filename = filedialog.askopenfilename(
            title=self.t.t("Select video file"),
            filetypes=[("Video files", "*.mp4 *.avi *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.video_var.set(f"./{os.path.basename(filename)}")

    def delete_game(self):
        """删除游戏"""
        t = self.t
        if not hasattr(self, 'selected_game'):
            self.create_centered_dialog(t.t("Warning"), t.t("Please select a game to delete"), "warning")
            return

        # 确认删除
        result = self.create_centered_dialog(t.t("Confirm Delete"),
            f"{t.t('Are you sure you want to delete the game:')} {self.selected_game['name']}?",
            "askyesno")

        if result:
            try:
                # 从数据列表中移除
                self.games.remove(self.selected_game)
                self.filtered_games = self.games.copy()

                # 刷新显示
                self.refresh_treeview()
                self.clear_form()
                self.status_var.set(t.t("Game deleted successfully"))

            except Exception as e:
                self.create_centered_dialog(t.t("Error"), f"{t.t('Error deleting game:')} {str(e)}", "error")

    def clear_form(self):
        """清空表单"""
        self.name_var.set("")
        self.path_var.set("")
        self.image_var.set("")
        self.video_var.set("")
        self.genre_var.set("")
        self.desc_var.set("")
        if hasattr(self, 'selected_game'):
            del self.selected_game

    def check_integrity(self):
        """完整性检测：扫描所有游戏，列出缺失文件的项目"""
        t = self.t
        if not self.current_file:
            self.create_centered_dialog(t.t("Warning"), t.t("Please open a gamelist.xml file first"), "warning")
            return

        base_dir = os.path.dirname(self.current_file)
        issues = []
        for idx, game in enumerate(self.games):
            missing = []
            # 检查路径
            if 'path' in game and game['path']:
                full_path = os.path.normpath(os.path.join(base_dir, game['path']))
                if not os.path.exists(full_path):
                    missing.append('path')
            # 检查图片
            if 'image' in game and game['image']:
                full_path = os.path.normpath(os.path.join(base_dir, game['image']))
                if not os.path.exists(full_path):
                    missing.append('image')
            # 检查视频
            if 'video' in game and game['video']:
                full_path = os.path.normpath(os.path.join(base_dir, game['video']))
                if not os.path.exists(full_path):
                    missing.append('video')
            if missing:
                issues.append((idx, game, missing))

        if not issues:
            self.create_centered_dialog(t.t("Info"), t.t("All games are complete!"), "info")
            return

        self.show_fix_dialog(issues, base_dir)

    def show_fix_dialog(self, issues, base_dir):
        """显示修复对话框，列出问题游戏，双击行触发修复，修复后刷新列表"""
        t = self.t
        dialog = tk.Toplevel(self)
        dialog.title(t.t("Integrity Check Results"))
        dialog.transient(self)
        dialog.geometry("800x500")
        CommonUtils.center_dialog(dialog, self.winfo_toplevel())

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 显示剩余数量的标签（可变）
        remaining_label = ttk.Label(main_frame, text=f"{t.t('Found')} {len(issues)} {t.t('incomplete games')}",
                                    font=(self.font_family, 12, "bold"))
        remaining_label.pack(anchor='w', pady=(0, 10))

        columns = ('game', 'missing', 'actions')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        tree.heading('game', text=t.t('Game Name'))
        tree.heading('missing', text=t.t('Missing Items'))
        tree.heading('actions', text=t.t('Actions'))

        tree.column('game', width=200)
        tree.column('missing', width=200)
        tree.column('actions', width=150)

        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 存储数据供双击事件使用
        tree.issues_data = issues  # issues 是可变列表
        tree.base_dir = base_dir
        tree.dialog = dialog
        tree.remaining_label = remaining_label  # 保存标签引用

        # 插入所有行
        for idx, (_, game, missing) in enumerate(issues):
            missing_text = ', '.join(missing)
            tree.insert('', 'end', iid=str(idx), values=(game['name'], missing_text, t.t("Double-click to fix")))

        # 双击事件处理
        def on_double_click(event):
            selection = tree.selection()
            if not selection:
                return
            item_id = selection[0]
            try:
                row_index = int(item_id)
            except ValueError:
                return
            if row_index < len(issues):
                idx, game, missing = issues[row_index]
                # 修复该游戏，传入 tree 和 issues 以便动态更新
                self.fix_game_missing(idx, game, missing, base_dir, dialog, tree, issues)

        tree.bind('<Double-1>', on_double_click)

        close_btn = ttk.Button(main_frame, text=t.t("Close"), command=dialog.destroy)
        close_btn.pack(pady=10)

    def fix_game_missing(self, idx, game, missing, base_dir, parent_dialog, tree, issues):
        """修复单个游戏的缺失项，允许选择性修复，取消的项保留"""
        t = self.t

        selected = {}  # miss_type -> new_file_path
        # 遍历当前缺失项，每个都弹出选择
        for miss_type in missing[:]:  # 使用副本
            if miss_type == 'path':
                new_file = filedialog.askopenfilename(
                    title=f"{t.t('Select ROM file for')} {game['name']}",
                    filetypes=[("All files", "*.*")]
                )
                if new_file:
                    selected['path'] = new_file

            elif miss_type == 'image':
                new_file = filedialog.askopenfilename(
                    title=f"{t.t('Select image file for')} {game['name']}",
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
                )
                if new_file:
                    selected['image'] = new_file

            elif miss_type == 'video':
                new_file = filedialog.askopenfilename(
                    title=f"{t.t('Select video file for')} {game['name']}",
                    filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
                )
                if new_file:
                    selected['video'] = new_file

        # 如果没有任何选择，视为取消
        if not selected:
            self.create_centered_dialog(t.t("Info"), t.t("Fix cancelled, no changes made."), "info")
            return

        # 执行复制和更新，只针对 selected 中的类型
        for miss_type, new_file in selected.items():
            if miss_type == 'path':
                target_dir = os.path.join(base_dir, 'roms')
                os.makedirs(target_dir, exist_ok=True)
                new_name = os.path.basename(new_file)
                target_path = os.path.join(target_dir, new_name)
                try:
                    shutil.copy2(new_file, target_path)
                except Exception as e:
                    self.create_centered_dialog(t.t("Error"), f"{t.t('Copy failed')}: {e}", "error")
                    return
                rel_path = os.path.relpath(target_path, base_dir).replace('\\', '/')
                game['path'] = rel_path
                path_elem = game['element'].find('path')
                if path_elem is None:
                    path_elem = ET.SubElement(game['element'], 'path')
                path_elem.text = rel_path

            elif miss_type == 'image':
                old_image = game.get('image', '')
                if old_image:
                    target_dir = os.path.dirname(os.path.join(base_dir, old_image))
                    base_name = os.path.basename(old_image)
                else:
                    target_dir = os.path.join(base_dir, 'images')
                    base_name = f"{game['name']}{os.path.splitext(new_file)[1]}"
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, base_name)
                try:
                    shutil.copy2(new_file, target_path)
                except Exception as e:
                    self.create_centered_dialog(t.t("Error"), f"{t.t('Copy failed')}: {e}", "error")
                    return
                rel_path = os.path.relpath(target_path, base_dir).replace('\\', '/')
                game['image'] = rel_path
                image_elem = game['element'].find('image')
                if image_elem is None:
                    image_elem = ET.SubElement(game['element'], 'image')
                image_elem.text = rel_path

            elif miss_type == 'video':
                old_video = game.get('video', '')
                if old_video:
                    target_dir = os.path.dirname(os.path.join(base_dir, old_video))
                    base_name = os.path.basename(old_video)
                else:
                    target_dir = os.path.join(base_dir, 'videos')
                    base_name = f"{game['name']}{os.path.splitext(new_file)[1]}"
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, base_name)
                try:
                    shutil.copy2(new_file, target_path)
                except Exception as e:
                    self.create_centered_dialog(t.t("Error"), f"{t.t('Copy failed')}: {e}", "error")
                    return
                rel_path = os.path.relpath(target_path, base_dir).replace('\\', '/')
                game['video'] = rel_path
                video_elem = game['element'].find('video')
                if video_elem is None:
                    video_elem = ET.SubElement(game['element'], 'video')
                video_elem.text = rel_path

        # 所有选中的项都已成功复制和更新
        self.refresh_treeview()  # 刷新主界面

        # 更新 issues：从 missing 中移除已修复的类型
        for item in issues:
            if item[1] is game:
                # 剩余缺失项 = 原缺失项 - 已选修复项
                remaining = [m for m in item[2] if m not in selected]
                item[2][:] = remaining  # 替换原列表
                break

        # 移除 missing 为空的条目
        issues[:] = [item for item in issues if item[2]]

        # 刷新对话框树形视图
        for child in tree.get_children():
            tree.delete(child)
        for i, (_, g, miss) in enumerate(issues):
            missing_text = ', '.join(miss)
            tree.insert('', 'end', iid=str(i), values=(g['name'], missing_text, t.t("Double-click to fix")))

        # 更新剩余数量标签
        if hasattr(tree, 'remaining_label'):
            tree.remaining_label.config(text=f"{t.t('Found')} {len(issues)} {t.t('incomplete games')}")

        # 处理完成状态
        if not issues:
            parent_dialog.destroy()
            self.create_centered_dialog(t.t("Info"), t.t("All games have been fixed!"), "info")
        else:
            parent_dialog.title(f"{t.t('Integrity Check Results')} - {len(issues)} {t.t('remaining')}")

    def save_file(self):
        """保存文件"""
        t = self.t
        if not self.current_file:
            self.save_as_file()
            return

        try:
            # 重新构建XML树
            root = ET.Element('gameList')
            for game in self.games:
                root.append(game['element'])

            # 格式化XML
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")

            # 移除XML声明行
            pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()][1:])

            # 添加自定义注释头
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  gamelist.xml
  Last edited: {timestamp}
  Edited by: Gamelist Editor {ver}
  Total games: {len(self.games)}
-->
{pretty_xml}"""

            # 备份原文件
            if os.path.exists(self.current_file):
                backup_file = self.current_file + '.bak'
                shutil.copy2(self.current_file, backup_file)

            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            self.status_var.set(f"{t.t('File saved successfully:')} {os.path.basename(self.current_file)}")

        except Exception as e:
            self.create_centered_dialog(t.t("Error"), f"{t.t('Error saving file:')} {str(e)}", "error")

    def save_as_file(self):
        """另存为文件"""
        t = self.t
        if not self.current_file:
            self.create_centered_dialog(t.t("Warning"), t.t("Please open a gamelist.xml file first"), "warning")
            return

        filename = filedialog.asksaveasfilename(
            title=f"{t.t('Save As')}...",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            self.current_file = filename
            self.save_file()


class GamelistPinyinFrame(BaseFrame):
    def __init__(self, parent, translator: Translator):
        super().__init__(parent, translator)
        self.current_file = None
        self.games = []
        self.filtered_games = []
        self.tree = None
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        t = self.t
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 文件操作区域
        file_section = ttk.LabelFrame(main_frame, text=f"{t.t('File Operations')}", padding="10",
                                      style="Section.TLabelframe")
        file_section.pack(fill='x', pady=(0, 10))

        file_frame = ttk.Frame(file_section)
        file_frame.pack(fill='x', pady=5)

        self.open_entry = tk.StringVar()
        ttk.Label(file_frame, text=f"{t.t('Open gamelist.xml')}:").pack(side='left', padx=5)
        ttk.Entry(file_frame, textvariable=self.open_entry, state='disabled').pack(side='left', fill='x', expand=True, padx=5)

        ttk.Button(file_frame, text=f"{t.t('Open')}",
                   command=self.open_file, width=15, style="Action.TButton").pack(side='left', padx=5)
        self.save_btn = ttk.Button(file_frame, text=f"{t.t('Save')}",
                   command=self.save_file, width=15, style="Action.TButton")
        self.save_btn.pack(side='left', padx=5)
        ToolTip(self.save_btn, t.t("Tip: Please 'Apply Changes' before saving"), self.font_family)
        self.save_as_btn = ttk.Button(file_frame, text=f"{t.t('Save As')}",
                   command=self.save_as_file, width=15, style="Action.TButton")
        self.save_as_btn.pack(side='left', padx=5)
        ToolTip(self.save_as_btn, t.t("Tip: Please 'Apply Changes' before saving"), self.font_family)

        # 拼音处理区域
        pinyin_section = ttk.LabelFrame(main_frame, text=f"{t.t('Pinyin Processing')}", padding="10",
                                        style="Section.TLabelframe")
        pinyin_section.pack(fill='x', pady=(0, 10))

        # 前缀设置
        prefix_frame = ttk.Frame(pinyin_section)
        prefix_frame.pack(fill='x', pady=5)

        ttk.Label(prefix_frame, text=f"{t.t('Prefix Settings:')}", width=15).pack(side='left')

        self.prefix_action = tk.StringVar(value="none")
        prefix_radio_frame = ttk.Frame(prefix_frame)
        prefix_radio_frame.pack(side='left', padx=5)

        ttk.Radiobutton(prefix_radio_frame, text=t.t("None"),
                        variable=self.prefix_action, value="none").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_radio_frame, text=t.t("Add"),
                        variable=self.prefix_action, value="add").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_radio_frame, text=t.t("Remove"),
                        variable=self.prefix_action, value="remove").pack(side='left', padx=5)

        ttk.Label(prefix_frame, text=t.t("Separator:")).pack(side='left', padx=(20, 5))
        self.prefix_separator = tk.StringVar(value="-")
        prefix_sep_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_separator, width=5)
        prefix_sep_entry.pack(side='left', padx=5)

        # 后缀设置
        suffix_frame = ttk.Frame(pinyin_section)
        suffix_frame.pack(fill='x', pady=5)

        ttk.Label(suffix_frame, text=f"{t.t('Suffix Settings:')}", width=15).pack(side='left')

        self.suffix_action = tk.StringVar(value="none")
        suffix_radio_frame = ttk.Frame(suffix_frame)
        suffix_radio_frame.pack(side='left', padx=5)

        ttk.Radiobutton(suffix_radio_frame, text=t.t("None"),
                        variable=self.suffix_action, value="none").pack(side='left', padx=5)
        ttk.Radiobutton(suffix_radio_frame, text=t.t("Add"),
                        variable=self.suffix_action, value="add").pack(side='left', padx=5)
        ttk.Radiobutton(suffix_radio_frame, text=t.t("Remove"),
                        variable=self.suffix_action, value="remove").pack(side='left', padx=5)

        ttk.Label(suffix_frame, text=t.t("Separator:")).pack(side='left', padx=(20, 5))
        self.suffix_separator = tk.StringVar(value=" ")
        suffix_sep_entry = ttk.Entry(suffix_frame, textvariable=self.suffix_separator, width=5)
        suffix_sep_entry.pack(side='left', padx=5)

        ttk.Label(suffix_frame, text=t.t("Brackets:")).pack(side='left', padx=(20, 5))
        self.suffix_brackets = tk.StringVar(value="[ ]")
        suffix_bracket_entry = ttk.Entry(suffix_frame, textvariable=self.suffix_brackets, width=5)
        suffix_bracket_entry.pack(side='left', padx=5)

        # 处理按钮
        process_frame = ttk.Frame(pinyin_section)
        process_frame.pack(fill='x', pady=10)

        ttk.Button(process_frame, text=f"{t.t('Preview Changes')}",
                   command=self.preview_changes, width=15, style="Action.TButton").pack(side='left', padx=5)
        self.reset_btn = ttk.Button(process_frame, text=f"{t.t('Reset Names')}",
                   command=self.reset_names, width=15, style="Action.TButton")
        self.reset_btn.pack(side='left', padx=5)
        ToolTip(self.reset_btn, t.t("Tip: Used to restore the Modified Name to its Original Name"), self.font_family)
        self.apply_btn = ttk.Button(process_frame, text=f"{t.t('Apply Changes')}",
                   command=self.apply_changes, width=15, style="Action.TButton")
        self.apply_btn.pack(side='left', padx=5)
        ToolTip(self.apply_btn, t.t("Tip: Applying the modified effect to the Original Name\ndoes not actually modify the original file"), self.font_family)

        # 游戏列表区域
        list_section = ttk.LabelFrame(main_frame, text=f"{t.t('Game List')}", padding="10",
                                      style="Section.TLabelframe")
        list_section.pack(fill='both', expand=True, pady=(0, 10))

        # 搜索框
        search_frame = ttk.Frame(list_section)
        search_frame.pack(fill='x', pady=5)

        ttk.Label(search_frame, text=f"{t.t('Search:')}").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.search_games)

        ttk.Button(search_frame, text=f"{t.t('Reset')}",
                   command=self.refresh_list).pack(side='left', padx=5)

        # 游戏列表
        list_inner_frame = ttk.Frame(list_section)
        list_inner_frame.pack(fill='both', expand=True, pady=5)

        # 创建树形视图
        columns = ('original', 'modified', 'status')
        self.tree = ttk.Treeview(list_inner_frame, columns=columns, show='headings', height=12)

        # 定义列
        self.tree.heading('original', text=t.t('Original Name'))
        self.tree.heading('modified', text=t.t('Modified Name'))
        self.tree.heading('status', text=t.t('Status'))

        # 设置列宽
        self.tree.column('original', width=250)
        self.tree.column('modified', width=250)
        self.tree.column('status', width=100)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_inner_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value=t.t("Ready"))
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken', anchor='w')
        status_label.pack(fill='x', side='bottom')

    def open_file(self):
        """打开gamelist.xml文件"""
        t = self.t
        filename = filedialog.askopenfilename(
            title=t.t("Open gamelist.xml"),
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.current_file = filename
                self.parse_gamelist(filename)
                self.open_entry.set(self.current_file)
                self.status_var.set(f"{t.t('Loaded:')} {os.path.basename(filename)} - {len(self.games)} {t.t('games')}")
                self.refresh_treeview()
            except Exception as e:
                self.create_centered_dialog(t.t("Error"), f"{t.t('Error loading file:')} {str(e)}", "error")

    def parse_gamelist(self, filename):
        """解析gamelist.xml文件"""
        t = self.t
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            self.games = []
            for game_elem in root.findall('game'):
                name_elem = game_elem.find('name')
                if name_elem is not None and name_elem.text:
                    game = {
                        'name': name_elem.text,
                        'original_name': name_elem.text,  # 保存原始名称
                        'element': game_elem,
                        'modified': False
                    }
                    self.games.append(game)

            self.filtered_games = self.games.copy()

        except Exception as e:
            self.create_centered_dialog(t.t("Error"), f"{t.t('Error parsing XML file:')} {str(e)}", "error")

    def get_first_char_pinyin(self, text):
        """获取第一个字符的拼音首字母"""
        if not text:
            return ""

        first_char = text[0]
        # 如果是英文或数字，返回空字符串（不处理）
        if first_char.isascii() and first_char.isalnum():
            return ""

        # 获取拼音
        try:
            pinyin_list = pypinyin.pinyin(first_char, style=pypinyin.FIRST_LETTER)
            if pinyin_list and pinyin_list[0]:
                return pinyin_list[0][0].upper()
        except Exception:
            pass

        return ""

    def get_chinese_pinyin_initials(self, text):
        """获取文本中汉字部分的拼音首字母组合"""
        if not text:
            return ""

        # 提取汉字部分
        chinese_chars = ''.join([char for char in text if '\u4e00' <= char <= '\u9fff'])

        if not chinese_chars:
            return ""

        # 获取拼音首字母
        try:
            pinyin_list = pypinyin.pinyin(chinese_chars, style=pypinyin.FIRST_LETTER)
            initials = ''.join([p[0].upper() for p in pinyin_list if p and p[0]])
            return initials
        except Exception:
            pass

        return ""

    def process_name(self, name, prefix_action, prefix_sep, suffix_action, suffix_sep, suffix_brackets):
        """处理游戏名称"""
        original_name = name
        modified_name = name

        # 处理前缀
        if prefix_action == "add":
            first_pinyin = self.get_first_char_pinyin(name)
            if first_pinyin and prefix_sep:
                # 检查是否已经有前缀
                if not name.startswith(first_pinyin + prefix_sep):
                    modified_name = first_pinyin + prefix_sep + modified_name
        elif prefix_action == "remove":
            first_pinyin = self.get_first_char_pinyin(name[2:])
            if first_pinyin and prefix_sep:
                prefix_pattern = re.escape(first_pinyin + prefix_sep)
                if re.match(f"^{prefix_pattern}", modified_name):
                    modified_name = re.sub(f"^{prefix_pattern}", "", modified_name)

        # 处理后缀
        if suffix_action == "add":
            pinyin_initials = self.get_chinese_pinyin_initials(name)
            if pinyin_initials and suffix_brackets:
                # 构建后缀
                suffix = f"{suffix_brackets[0]}{pinyin_initials}{suffix_brackets[1]}"
                if suffix_sep:
                    suffix = suffix_sep + suffix

                # 检查是否已经有类似的后缀
                suffix_pattern = r"[\s\-_]*\[[A-Z]+\]$"  # 匹配类似 [ABC] 的后缀
                if not re.search(suffix_pattern, modified_name):
                    modified_name = modified_name + suffix
        elif suffix_action == "remove":
            # 移除拼音后缀（匹配各种括号）
            bracket_patterns = [
                r"[\s\-_]*\[[A-Z]+\]$",  # [ABC]
                r"[\s\-_]*\([A-Z]+\)$",  # (ABC)
                r"[\s\-_]*\{[A-Z]+\}$",  # {ABC}
                r"[\s\-_]*〈[A-Z]+〉$",  # 〈ABC〉
                r"[\s\-_]*《[A-Z]+》$",  # 《ABC》
            ]

            for pattern in bracket_patterns:
                modified_name = re.sub(pattern, "", modified_name)

        return modified_name

    def preview_changes(self):
        """预览更改"""
        t = self.t
        if not self.games:
            self.create_centered_dialog(t.t("Warning"), t.t("Please open a gamelist.xml file first"), "warning")
            return

        prefix_action = self.prefix_action.get()
        prefix_sep = self.prefix_separator.get()
        suffix_action = self.suffix_action.get()
        suffix_sep = self.suffix_separator.get()
        suffix_brackets = self.suffix_brackets.get().replace(" ", "")

        if len(suffix_brackets) != 2:
            self.create_centered_dialog(t.t("Error"), t.t("Brackets must be exactly 2 characters"), "error")
            return

        changes_count = 0
        for game in self.games:
            original_name = game['original_name']
            modified_name = self.process_name(original_name, prefix_action, prefix_sep,
                                              suffix_action, suffix_sep, suffix_brackets)

            if modified_name != original_name:
                game['name'] = modified_name
                game['modified'] = True
                changes_count += 1
            else:
                game['name'] = original_name
                game['modified'] = False

        self.refresh_treeview()
        self.status_var.set(f"{t.t('Preview completed:')} {changes_count} {t.t('games will be modified')}")

    def apply_changes(self):
        """应用更改到XML"""
        t = self.t
        if not self.games:
            self.create_centered_dialog(t.t("Warning"), t.t("Please open a gamelist.xml file first"), "warning")
            return

        # 确认应用更改
        result = self.create_centered_dialog(t.t("Confirm Apply"),
                                             t.t("Are you sure you want to apply these changes to the gamelist?"),
                                             "askyesno")

        if result:
            changes_count = 0
            for game in self.games:
                if game['modified']:
                    name_elem = game['element'].find('name')
                    if name_elem is not None:
                        name_elem.text = game['name']
                        changes_count += 1

            self.status_var.set(f"{t.t('Changes applied:')} {changes_count} {t.t('games modified')}")

            # 重置修改状态
            for game in self.games:
                game['modified'] = False
                game['original_name'] = game['name']

            self.refresh_treeview()

    def reset_names(self):
        """重置名称到原始状态"""
        t = self.t
        if not self.games:
            return

        for game in self.games:
            game['name'] = game['original_name']
            game['modified'] = False

        self.refresh_treeview()
        self.status_var.set(t.t("All names reset to original"))

    def refresh_treeview(self):
        """刷新树形视图"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加新数据
        for game in self.filtered_games:
            status = "✅ " + self.t.t("Modified") if game['modified'] else "⏺ " + self.t.t("Original")
            self.tree.insert('', 'end', values=(
                game['original_name'],
                game['name'],
                status
            ))

    def search_games(self, event=None):
        """搜索游戏"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filtered_games = self.games.copy()
        else:
            self.filtered_games = [
                game for game in self.games
                if search_term in game['name'].lower() or search_term in game['original_name'].lower()
            ]
        self.refresh_treeview()

    def refresh_list(self):
        """刷新列表"""
        self.filtered_games = self.games.copy()
        self.refresh_treeview()
        self.search_var.set("")

    def save_file(self):
        """保存文件"""
        t = self.t
        if not self.current_file:
            self.save_as_file()
            return

        try:
            # 重新构建XML树
            root = ET.Element('gameList')
            for game in self.games:
                root.append(game['element'])

            # 格式化XML
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")

            # 移除XML声明行
            pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()][1:])

            # 添加自定义注释头
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  gamelist.xml
  Last edited: {timestamp}
  Edited by: Gamelist Update {ver}
  Total games: {len(self.games)}
  make by : G.R.H
-->
{pretty_xml}"""

            # 备份原文件
            if os.path.exists(self.current_file):
                backup_file = self.current_file + '.bak'
                shutil.copy2(self.current_file, backup_file)

            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            self.status_var.set(f"{t.t('File saved successfully:')} {os.path.basename(self.current_file)}")

        except Exception as e:
            self.create_centered_dialog(t.t("Error"), f"{t.t('Error saving file:')} {str(e)}", "error")

    def save_as_file(self):
        """另存为文件"""
        t = self.t
        if not self.current_file:
            self.create_centered_dialog(t.t("Warning"), t.t("Please open a gamelist.xml file first"), "warning")
            return

        filename = filedialog.asksaveasfilename(
            title=f"{t.t('Save As')}...",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            self.current_file = filename
            self.save_file()


class GameRomNameFrame(GamelistPinyinFrame):
    def __init__(self, parent, translator: Translator):
        # 先初始化变量
        self.current_folder = None
        self.files = []
        self.filtered_files = []

        # 新增变量
        self.prefix_type = tk.StringVar(value="none")  # none, number, letter, mixed
        self.prefix_digits = tk.IntVar(value=2)  # 序号位数
        self.by_prefix_digits = tk.IntVar(value=1)  # 移除前缀位数
        self.prefix_start = tk.IntVar(value=1)  # 起始序号
        self.prefix_separator = tk.StringVar(value="-")  # 分隔符
        self.remove_existing_prefix = tk.BooleanVar(value=False)  # 移除现有前缀
        self.by_existing_prefix = tk.BooleanVar(value=False)  # 按位数移除


        # 然后调用父类初始化
        super().__init__(parent, translator)

    def create_widgets(self):
        """创建界面组件"""
        t = self.t
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 文件操作区域
        file_section = ttk.LabelFrame(main_frame, text=f"{t.t('File Operations')}", padding="10",
                                      style="Section.TLabelframe")
        file_section.pack(fill='x', pady=(0, 10))

        file_frame = ttk.Frame(file_section)
        file_frame.pack(fill='x', pady=5)

        self.open_entry = tk.StringVar()
        ttk.Label(file_frame, text=f"{t.t('Select Folder')}:").pack(side='left', padx=5)
        ttk.Entry(file_frame, textvariable=self.open_entry).pack(side='left', fill='x', expand=True,
                                                                                   padx=5)

        ttk.Button(file_frame, text=f"{t.t('Browse...')}",
                   command=self.open_folder, width=15, style="Action.TButton").pack(side='left', padx=5)

        # 扩展名设置
        ext_frame = ttk.Frame(file_section)
        ext_frame.pack(fill='x', pady=5)

        ttk.Label(ext_frame, text=f"{t.t('File Extensions')}:").pack(side='left', padx=5)
        self.extensions_var = tk.StringVar(value=".zip,.png")
        ext_entry = ttk.Entry(ext_frame, textvariable=self.extensions_var, width=50)
        ext_entry.pack(side='left', padx=5, fill='x', expand=True)
        ToolTip(ext_entry, t.t("Tip: Multiple extensions separated by commas"), self.font_family)

        ttk.Button(ext_frame, text=f"{t.t('Scan')}",
                   command=self.scan_files, width=15, style="Action.TButton").pack(side='left', padx=5)


        # 序号前缀区域
        prefix_section = ttk.LabelFrame(main_frame, text=f"{t.t('Serial Number Prefix')}", padding="10",
                                        style="Section.TLabelframe")
        prefix_section.pack(fill='x', pady=(0, 10))

        # 前缀类型
        type_frame = ttk.Frame(prefix_section)
        type_frame.pack(fill='x', pady=5)

        ttk.Label(type_frame, text=f"{t.t('Prefix Type')}:", width=15).pack(side='left')

        prefix_type_frame = ttk.Frame(type_frame)
        prefix_type_frame.pack(side='left', padx=5)

        ttk.Radiobutton(prefix_type_frame, text=t.t("None"),
                        variable=self.prefix_type, value="none").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_type_frame, text=t.t("Number"),
                        variable=self.prefix_type, value="number").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_type_frame, text=t.t("Letter"),
                        variable=self.prefix_type, value="letter").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_type_frame, text=t.t("Mixed"),
                        variable=self.prefix_type, value="mixed").pack(side='left', padx=5)

        # 前缀设置
        settings_frame = ttk.Frame(prefix_section)
        settings_frame.pack(fill='x', pady=5)

        ttk.Label(settings_frame, text=f"{t.t('Digits')}:").pack(side='left')
        digits_spinbox = ttk.Spinbox(settings_frame, from_=1, to=5, width=5,
                                     textvariable=self.prefix_digits)
        digits_spinbox.pack(side='left', padx=20)

        ttk.Label(settings_frame, text=f"{t.t('Start')}:").pack(side='left')
        start_spinbox = ttk.Spinbox(settings_frame, from_=0, to=99999, width=5,
                                    textvariable=self.prefix_start)
        start_spinbox.pack(side='left', padx=20)

        ttk.Label(settings_frame, text=f"{t.t('Separator')}:").pack(side='left')
        separator_entry = ttk.Entry(settings_frame, textvariable=self.prefix_separator, width=5)
        separator_entry.pack(side='left', padx=20)

        ttk.Checkbutton(settings_frame, text=t.t("Remove Existing Prefix"),
                        variable=self.remove_existing_prefix,
                        command=lambda: self.switch_remove(1)).pack(side='left', padx=10)

        self.by_number_checkbtn = ttk.Checkbutton(settings_frame, text=t.t("By number of digits:"),
                                                  variable=self.by_existing_prefix,
                                                  state='disabled',  # 初始状态为禁用
                                                  command=lambda: self.switch_remove(2))
        self.by_number_checkbtn.pack(side='left', padx=10)

        self.by_digits_spinbox = ttk.Spinbox(settings_frame, from_=1, to=99, width=5,
                                             textvariable=self.by_prefix_digits,
                                             state='disabled')  # 初始状态为禁用
        self.by_digits_spinbox.pack(side='left', padx=20)

        # 拼音处理区域（继承自父类）
        pinyin_section = ttk.LabelFrame(main_frame, text=f"{t.t('Pinyin Processing')}", padding="10",
                                        style="Section.TLabelframe")
        pinyin_section.pack(fill='x', pady=(0, 10))

        # 前缀设置（拼音）
        prefix_frame = ttk.Frame(pinyin_section)
        prefix_frame.pack(fill='x', pady=5)

        ttk.Label(prefix_frame, text=f"{t.t('Prefix Settings:')}", width=15).pack(side='left')

        self.prefix_action = tk.StringVar(value="none")
        prefix_radio_frame = ttk.Frame(prefix_frame)
        prefix_radio_frame.pack(side='left', padx=5)

        ttk.Radiobutton(prefix_radio_frame, text=t.t("None"),
                        variable=self.prefix_action, value="none").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_radio_frame, text=t.t("Add"),
                        variable=self.prefix_action, value="add").pack(side='left', padx=5)
        ttk.Radiobutton(prefix_radio_frame, text=t.t("Remove"),
                        variable=self.prefix_action, value="remove").pack(side='left', padx=5)

        ttk.Label(prefix_frame, text=t.t("Separator:")).pack(side='left', padx=(20, 5))
        self.pinyin_prefix_separator = tk.StringVar(value="-")
        prefix_sep_entry = ttk.Entry(prefix_frame, textvariable=self.pinyin_prefix_separator, width=5)
        prefix_sep_entry.pack(side='left', padx=5)

        # 后缀设置（拼音）
        suffix_frame = ttk.Frame(pinyin_section)
        suffix_frame.pack(fill='x', pady=5)

        ttk.Label(suffix_frame, text=f"{t.t('Suffix Settings:')}", width=15).pack(side='left')

        self.suffix_action = tk.StringVar(value="none")
        suffix_radio_frame = ttk.Frame(suffix_frame)
        suffix_radio_frame.pack(side='left', padx=5)

        ttk.Radiobutton(suffix_radio_frame, text=t.t("None"),
                        variable=self.suffix_action, value="none").pack(side='left', padx=5)
        ttk.Radiobutton(suffix_radio_frame, text=t.t("Add"),
                        variable=self.suffix_action, value="add").pack(side='left', padx=5)
        ttk.Radiobutton(suffix_radio_frame, text=t.t("Remove"),
                        variable=self.suffix_action, value="remove").pack(side='left', padx=5)

        ttk.Label(suffix_frame, text=t.t("Separator:")).pack(side='left', padx=(20, 5))
        self.suffix_separator = tk.StringVar(value=" ")
        suffix_sep_entry = ttk.Entry(suffix_frame, textvariable=self.suffix_separator, width=5)
        suffix_sep_entry.pack(side='left', padx=5)

        ttk.Label(suffix_frame, text=t.t("Brackets:")).pack(side='left', padx=(20, 5))
        self.suffix_brackets = tk.StringVar(value="[ ]")
        suffix_bracket_entry = ttk.Entry(suffix_frame, textvariable=self.suffix_brackets, width=5)
        suffix_bracket_entry.pack(side='left', padx=5)

        # 处理按钮
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill='x', pady=10)

        ttk.Button(process_frame, text=f"{t.t('Preview Changes')}",
                   command=self.preview_changes, width=15, style="Action.TButton").pack(side='left', padx=5)
        self.reset_btn = ttk.Button(process_frame, text=f"{t.t('Reset Names')}",
                                    command=self.reset_names, width=15, style="Action.TButton")
        self.reset_btn.pack(side='left', padx=5)
        ToolTip(self.reset_btn, t.t("Tip: Used to restore the Modified Name to its Original Name"), self.font_family)
        self.apply_btn = ttk.Button(process_frame, text=f"{t.t('Apply Changes')}",
                                    command=self.apply_changes, width=15, style="Action.TButton")
        self.apply_btn.pack(side='left', padx=5)
        ToolTip(self.apply_btn, t.t("Tip: Applying the modified effect to the files"), self.font_family)

        # 文件列表区域
        list_section = ttk.LabelFrame(main_frame, text=f"{t.t('File List')}", padding="10",
                                      style="Section.TLabelframe")
        list_section.pack(fill='both', expand=True, pady=(0, 10))

        # 搜索框
        search_frame = ttk.Frame(list_section)
        search_frame.pack(fill='x', pady=5)

        ttk.Label(search_frame, text=f"{t.t('Search:')}").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.search_files)

        ttk.Button(search_frame, text=f"{t.t('Reset')}",
                   command=self.refresh_list).pack(side='left', padx=5)

        # 文件列表
        list_inner_frame = ttk.Frame(list_section)
        list_inner_frame.pack(fill='both', expand=True, pady=5)

        # 创建树形视图
        columns = ('original', 'modified', 'status')
        self.tree = ttk.Treeview(list_inner_frame, columns=columns, show='headings', height=12)

        # 定义列
        self.tree.heading('original', text=t.t('Original Name'))
        self.tree.heading('modified', text=t.t('Modified Name'))
        self.tree.heading('status', text=t.t('Status'))

        # 设置列宽
        self.tree.column('original', width=250)
        self.tree.column('modified', width=250)
        self.tree.column('status', width=100)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_inner_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value=t.t("Ready"))
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken', anchor='w')
        status_label.pack(fill='x', side='bottom')

    def open_folder(self):
        """打开文件夹"""
        t = self.t
        folder = filedialog.askdirectory(title=t.t("Select folder containing game files"))

        if folder:
            try:
                self.current_folder = folder
                self.open_entry.set(self.current_folder)
            except Exception as e:
                self.create_centered_dialog(t.t("Error"), f"{t.t('Error loading folder:')} {str(e)}", "error")

    def scan_files(self):
        """扫描文件夹中的文件"""
        t = self.t
        if not self.current_folder:
            self.open_folder()
            if not self.current_folder:
                self.create_centered_dialog(t.t("Error"), t.t('Please select a folder first'), "error")
                return

        try:
            # 获取扩展名列表
            extensions = [ext.strip().lower() for ext in self.extensions_var.get().replace("，", ",").split(",")]

            self.files = []
            for item in os.listdir(self.current_folder):
                full_path = os.path.join(self.current_folder, item)
                if os.path.isfile(full_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in extensions:
                        file_info = {
                            'filename': item,
                            'original_name': item,
                            'name': os.path.splitext(item)[0],
                            'extension': file_ext,
                            'full_path': full_path,
                            'modified': False
                        }
                        self.files.append(file_info)

            if self.files:
                self.filtered_files = self.files.copy()
                self.refresh_treeview()
                self.status_var.set(f"{t.t('Loaded:')} {os.path.basename(self.current_folder)} - {len(self.files)} {t.t('files')}")
            else:
                self.create_centered_dialog(t.t("Error"), t.t('No valid file found, please check the extension.') , "error")

        except Exception as e:
            self.create_centered_dialog(t.t("Error"), f"{t.t('Error scanning ROM file：%s')} % {str(e)}", "error")

    def generate_prefix(self, index):
        """生成序号前缀"""
        prefix_type = self.prefix_type.get()
        digits = self.prefix_digits.get()
        start = self.prefix_start.get()
        separator = self.prefix_separator.get()

        if prefix_type == "none":
            return ""

        sequence_num = start + index

        if prefix_type == "number":
            prefix = f"{sequence_num:0{digits}d}"
        elif prefix_type == "letter":
            # 将数字转换为字母 (1=A, 2=B, ..., 27=AA, 28=AB, etc.)
            prefix = ""
            num = sequence_num
            while num > 0:
                num -= 1
                prefix = chr(65 + num % 26) + prefix
                num //= 26
        elif prefix_type == "mixed":
            # 混合模式: 字母+数字
            letter_part = ""
            num = (sequence_num - 1) // 10 + 1  # 每10个数字一个字母
            while num > 0:
                num -= 1
                letter_part = chr(65 + num % 26) + letter_part
                num //= 26
            number_part = (sequence_num - 1) % 10 + 1
            prefix = f"{letter_part}{number_part:0{max(1, digits - 1)}d}"

        return f"{prefix}{separator}"

    def switch_remove(self, index: int):
        """切换移除现有前缀相关控件的状态"""
        if index == 1:
            # 当"移除现有前缀"复选框状态改变时
            if self.remove_existing_prefix.get():
                # 启用"按位数移除"复选框和数字输入框
                self.by_number_checkbtn.config(state='normal')
            else:
                # 禁用"按位数移除"复选框和数字输入框
                self.by_number_checkbtn.config(state='disabled')
                self.by_digits_spinbox.config(state='disabled')
                # 同时取消选中"按位数移除"
                self.by_existing_prefix.set(False)

        elif index == 2:
            # 当"按位数移除"复选框状态改变时
            if self.by_existing_prefix.get():
                # 确保数字输入框启用
                self.by_digits_spinbox.config(state='normal')
            else:
                # 禁用数字输入框
                self.by_digits_spinbox.config(state='disabled')

    def remove_existing_prefixes(self, filename):
        """移除现有的序号前缀"""
        if not self.remove_existing_prefix.get():
            return filename

        # 如果启用了按位数移除
        if self.by_existing_prefix.get():
            digits = self.by_prefix_digits.get()
            # 移除指定位数的前缀（数字+分隔符）
            #pattern = rf'^\w{{{digits}}}'
            #filename = re.sub(pattern, '', filename)
            filename = filename[digits:]
        else:
            # 移除常见的序号前缀模式
            patterns = [
                r'^\d+[-_.\s]',  # 数字前缀: "01-", "001.", "1_"
                r'^[A-Z]+[-_.\s]',  # 字母前缀: "A-", "AA.", "B_"
                r'^[A-Z]+\d+[-_.\s]',  # 混合前缀: "A1-", "AB01.", "B2_"
            ]

            for pattern in patterns:
                filename = re.sub(pattern, '', filename)

        return filename

    def process_filename(self, original_name, index):
        """处理文件名"""
        # 移除扩展名
        name_without_ext = os.path.splitext(original_name)[0]
        extension = os.path.splitext(original_name)[1]

        # 移除现有前缀
        cleaned_name = self.remove_existing_prefixes(name_without_ext)

        # 生成新前缀
        new_prefix = self.generate_prefix(index)

        # 处理拼音（调用父类方法）
        processed_name = self.process_name(
            cleaned_name,
            self.prefix_action.get(),
            self.pinyin_prefix_separator.get(),
            self.suffix_action.get(),
            self.suffix_separator.get(),
            self.suffix_brackets.get().replace(" ", "")
        )

        # 组合新文件名
        final_name = f"{new_prefix}{processed_name}{extension}"

        return final_name

    def preview_changes(self):
        """预览更改"""
        t = self.t
        if not self.files:
            self.create_centered_dialog(t.t("Warning"), t.t("Please select a folder first"), "warning")
            return

        # 验证括号设置
        suffix_brackets = self.suffix_brackets.get().replace(" ", "")
        if len(suffix_brackets) != 2 and self.suffix_action.get() == "add":
            self.create_centered_dialog(t.t("Error"), t.t("Brackets must be exactly 2 characters"), "error")
            return

        changes_count = 0
        for i, file_info in enumerate(self.files):
            original_name = file_info['original_name']
            modified_name = self.process_filename(original_name, i)

            if modified_name != original_name:
                file_info['filename'] = modified_name
                file_info['modified'] = True
                changes_count += 1
            else:
                file_info['filename'] = original_name
                file_info['modified'] = False

        self.refresh_treeview()
        self.status_var.set(f"{t.t('Preview completed:')} {changes_count} {t.t('files will be modified')}")

    def apply_changes(self):
        """应用更改到实际文件"""
        t = self.t
        if not self.files:
            self.create_centered_dialog(t.t("Warning"), t.t("Please select a folder first"), "warning")
            return

        # 确认应用更改
        result = self.create_centered_dialog(t.t("Confirm Apply"),
                                             t.t("Are you sure you want to rename these files?"),
                                             "askyesno")

        if result:
            changes_count = 0
            error_files = []

            for file_info in self.files:
                if file_info['modified']:
                    try:
                        original_path = os.path.join(self.current_folder, file_info['original_name'])
                        new_path = os.path.join(self.current_folder, file_info['filename'])

                        # 检查目标文件是否已存在
                        if os.path.exists(new_path) and original_path != new_path:
                            error_files.append(f"{file_info['original_name']}: {t.t('Target file already exists')}")
                            continue

                        # 重命名文件
                        os.rename(original_path, new_path)
                        changes_count += 1

                        # 更新文件信息
                        file_info['original_name'] = file_info['filename']
                        file_info['full_path'] = new_path
                        file_info['modified'] = False

                    except Exception as e:
                        error_files.append(f"{file_info['original_name']}: {str(e)}")

            # 显示结果
            if error_files:
                error_msg = f"{t.t('The following files failed to rename:')}\n\n" + "\n".join(error_files)
                self.create_centered_dialog(t.t("Error"), error_msg, "error")

            self.status_var.set(f"{t.t('Changes applied:')} {changes_count} {t.t('files renamed')}")

            # 重新扫描文件以更新列表
            self.scan_files()

    def reset_names(self):
        """重置名称到原始状态"""
        t = self.t
        if not self.files:
            return

        for file_info in self.files:
            file_info['filename'] = file_info['original_name']
            file_info['modified'] = False

        self.refresh_treeview()
        self.status_var.set(t.t("All names reset to original"))

    def refresh_treeview(self):
        """刷新树形视图"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加新数据
        for file_info in self.filtered_files:
            status = "✅ " + self.t.t("Modified") if file_info['modified'] else "⏺ " + self.t.t("Original")
            self.tree.insert('', 'end', values=(
                file_info['original_name'],
                file_info['filename'],
                status
            ))

    def search_files(self, event=None):
        """搜索文件"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filtered_files = self.files.copy()
        else:
            self.filtered_files = [
                file_info for file_info in self.files
                if search_term in file_info['filename'].lower() or search_term in file_info['original_name'].lower()
            ]
        self.refresh_treeview()

    def refresh_list(self):
        """刷新列表"""
        self.filtered_files = self.files.copy()
        self.refresh_treeview()
        self.search_var.set("")


class GamelistGeneratorFrame(BaseFrame):
    def __init__(self, parent, translator: Translator):
        super().__init__(parent, translator)
        self.dialog_result = None

        # 创建变量
        self.rom_folder = tk.StringVar()
        self.image_folder = tk.StringVar(value="images")
        self.video_folder = tk.StringVar(value="videos")
        self.output_folder = tk.StringVar()
        self.extensions = tk.StringVar(value=".zip,.7z,.nes,.smc,.gb,.gbc,.gba,.nds,.iso,.bin,.chd")
        self.image_ext = tk.StringVar(value=".png,.jpg,.jpeg")
        self.video_ext = tk.StringVar(value=".mp4")
        self.include_images = tk.BooleanVar(value=False)
        self.include_videos = tk.BooleanVar(value=False)
        self.scan_issues = False
        self.rom_files = []
        self.image_files = {}
        self.video_files = {}

        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        t = self.t
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 文件夹设置区域
        folder_section = ttk.LabelFrame(main_frame, text=f"{t.t('ROM Settings')}", padding="10",
                                        style="Section.TLabelframe")
        folder_section.pack(fill='x', pady=(0, 10))

        # ROM文件夹
        rom_frame = ttk.Frame(folder_section)
        rom_frame.pack(fill='x', pady=5)
        ttk.Label(rom_frame, text=t.t("ROM folder:"), width=15).pack(side='left')
        ttk.Entry(rom_frame, textvariable=self.rom_folder, width=50).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(rom_frame, text=t.t("Browse..."), command=self.browse_rom_folder).pack(side='right')

        # 文件扩展名
        ext_frame = ttk.Frame(folder_section)
        ext_frame.pack(fill='x', pady=5)
        ttk.Label(ext_frame, text=t.t("ROM extension:"), width=15).pack(side='left')
        self.entry1 = ttk.Entry(ext_frame, textvariable=self.extensions)
        self.entry1.pack(side='left', padx=5, fill='x', expand=True)
        ToolTip(self.entry1, t.t("Tip: Multiple extensions separated by commas"), self.font_family)

        # 设置区域
        settings_section = ttk.LabelFrame(main_frame, text=f"{t.t('Media settings')}", padding="10",
                                          style="Section.TLabelframe")
        settings_section.pack(fill='x', pady=(0, 10))

        # 选项复选框
        image_frame = ttk.Frame(settings_section)
        image_frame.pack(fill='x', pady=5)

        ttk.Checkbutton(image_frame, text=t.t("Preview images"), command=self.on_image_checkbox_click,
                        variable=self.include_images, width=20, ).pack(side='left', padx=10)

        ttk.Label(image_frame, text=t.t("Extension:")).pack(side='left')

        self.image_ext_entry = ttk.Entry(image_frame, textvariable=self.image_ext, state="disable")
        self.image_ext_entry.pack(side='left', padx=5, fill='x', expand=True)
        ToolTip(self.image_ext_entry, t.t("Tip: Multiple extensions separated by commas"), self.font_family)

        ttk.Label(image_frame, text=t.t("Subfolder:")).pack(side='left')

        self.image_folder_entry = ttk.Entry(image_frame, textvariable=self.image_folder, state="disable")
        self.image_folder_entry.pack(side='left', padx=5, fill='x', expand=True)
        ToolTip(self.image_folder_entry, t.t("Tip: Located in the ROM folder"), self.font_family)

        video_frame = ttk.Frame(settings_section)
        video_frame.pack(fill='x', pady=5)

        ttk.Checkbutton(video_frame, text=t.t("Preview Video"), command=self.on_video_checkbox_click,
                        variable=self.include_videos, width=20).pack(side='left', padx=10)

        ttk.Label(video_frame, text=t.t("Extension:")).pack(side='left')

        self.video_ext_entry = ttk.Entry(video_frame, textvariable=self.video_ext, state="disable")
        self.video_ext_entry.pack(side='left', padx=5, fill='x', expand=True)
        ToolTip(self.video_ext_entry, t.t("Tip: Multiple extensions separated by commas"), self.font_family)

        ttk.Label(video_frame, text=t.t("Subfolder:")).pack(side='left')

        self.video_folder_entry = ttk.Entry(video_frame, textvariable=self.video_folder, state="disable")
        self.video_folder_entry.pack(side='left', padx=5, fill='x', expand=True)
        ToolTip(self.video_folder_entry, t.t("Tip: Located in the ROM folder"))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        button_inner_frame = ttk.Frame(button_frame)
        button_inner_frame.pack()

        self.scan_btn = ttk.Button(button_inner_frame, text=f"{t.t('Scan Preview')}", command=self.scan_files,
                                   style="Action.TButton",
                                   width=20)
        self.scan_btn.pack(side='left', padx=10)
        self.generate_btn = ttk.Button(button_inner_frame, text=f"{t.t('Generate list')}",
                                       command=self.generate_gamelist, style="Action.TButton",
                                       width=20)
        self.generate_btn.pack(side='left', padx=5)
        self.reset_btn = ttk.Button(button_inner_frame, text=f"{t.t('Reset')}", command=self.reset_all,
                                    style="Action.TButton", width=20)
        self.reset_btn.pack(side='left', padx=10)

        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=(0, 10))

        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill='x')
        self.progress_label = ttk.Label(progress_frame, text=t.t("Ready"))
        self.progress_label.pack(anchor='w')

        # 结果区域
        result_section = ttk.LabelFrame(main_frame, text=f"{t.t('Scan results')}", padding="10",
                                        style="Section.TLabelframe")
        result_section.pack(fill='both', expand=True)

        # 创建文本框和滚动条
        text_frame = ttk.Frame(result_section)
        text_frame.pack(fill='both', expand=True)

        self.result_text = tk.Text(text_frame, wrap='word', width=80, height=15)
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.result_text.pack(side='left', fill='both', expand=True)

        # 状态栏
        self.status_label = ttk.Label(main_frame, text=t.t("Ready"), relief='sunken', anchor='w')
        self.status_label.pack(fill='x', side='bottom')

    def browse_rom_folder(self):
        """浏览ROM文件夹"""
        t = self.t
        folder = filedialog.askdirectory(title=t.t("Select game ROM folder"))
        if folder:
            self.rom_folder.set(folder)
            self.output_folder.set(folder)
            self.scan_issues = False

    def on_image_checkbox_click(self):
        if self.include_images.get():
            self.image_ext_entry.config(state="normal")
            self.image_folder_entry.config(state="normal")
        else:
            self.image_ext_entry.config(state="disabled")
            self.image_folder_entry.config(state="disabled")
        self.scan_issues = False

    def on_video_checkbox_click(self):
        if self.include_videos.get():
            self.video_ext_entry.config(state="normal")
            self.video_folder_entry.config(state="normal")
        else:
            self.video_ext_entry.config(state="disabled")
            self.video_folder_entry.config(state="disabled")
        self.scan_issues = False

    def update_progress(self, value, text):
        """更新进度条"""
        self.progress['value'] = value
        self.progress_label.config(text=text)
        self.update()

    def update_status(self, text):
        """更新状态栏"""
        self.status_label.config(text=text)
        self.update()

    def log_message(self, message):
        """在结果文本框中添加消息"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.update()

    def switch_btn(self, button):
        if button:
            self.scan_btn.config(state='normal')
            self.generate_btn.config(state='normal')
            self.reset_btn.config(state='normal')
        else:
            self.scan_btn.config(state='disabled')
            self.generate_btn.config(state='disabled')
            self.reset_btn.config(state='disabled')

    def scan_files(self):
        """扫描文件"""
        t = self.t
        self.switch_btn(False)
        if not self.rom_folder.get():
            self.browse_rom_folder()
            if not self.rom_folder.get():
                self.create_centered_dialog(t.t("Error"), t.t("Please select the game ROM folder first!"), "error")
                self.switch_btn(True)
                return

        # 清空结果文本框
        self.result_text.delete(1.0, tk.END)

        # 获取扩展名列表
        extensions = [ext.strip().lower() for ext in self.extensions.get().replace("，", ",").split(",")]

        self.log_message(f"🔍 {t.t('Start scanning files ...')}")
        self.update_progress(0, t.t("Scanning in progress ..."))

        # 扫描ROM文件
        self.rom_files.clear()
        self.image_files.clear()
        self.video_files.clear()

        try:
            rom_folder_path = self.rom_folder.get()
            for item in os.listdir(rom_folder_path):
                full_path = os.path.join(rom_folder_path, item)
                if os.path.isfile(full_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in extensions:
                        relative_path = os.path.relpath(full_path, rom_folder_path)
                        self.rom_files.append({
                            'filename': item,
                            'path': relative_path,
                            'name': os.path.splitext(item)[0],
                            'full_path': full_path
                        })

        except Exception as e:
            self.create_centered_dialog(t.t("Error"), t.t("Error scanning ROM file：%s") % str(e), "error")
            return

        self.log_message(f"  • {t.t('Found %d ROM files') % len(self.rom_files)}")

        # 扫描图片文件
        if self.include_images.get() and self.image_folder.get():
            self.log_message(f"🔍 {t.t('Scan image files ...')}")
            try:
                image_folder_path = os.path.join(self.rom_folder.get(), self.image_folder.get()).replace('\\', '/')
                if os.path.exists(image_folder_path):
                    for item in os.listdir(image_folder_path):
                        full_path = os.path.join(image_folder_path, item)
                        if os.path.isfile(full_path):
                            file_ext = os.path.splitext(item)[1].lower()
                            if file_ext in [ext.strip().lower() for ext in
                                            self.image_ext.get().replace("，", ",").split(",")]:
                                name_without_ext = os.path.splitext(item)[0]
                                relative_path = os.path.relpath(full_path, self.rom_folder.get())
                                self.image_files[name_without_ext] = relative_path.replace('\\', '/')
                else:
                    self.log_message(f"⚠️ {t.t('The image folder does not exist: %s') % image_folder_path}")
            except Exception as e:
                self.log_message(f"⚠️ {t.t('Error scanning image file：%s') % str(e)}")

        self.log_message(f"  • {t.t('Found %d image files') % len(self.image_files)}")

        # 扫描视频文件
        if self.include_videos.get() and self.video_folder.get():
            self.log_message(f"🔍 {t.t('Scan video files ...')}")
            try:
                video_folder_path = os.path.join(self.rom_folder.get(), self.video_folder.get()).replace('\\', '/')
                if os.path.exists(video_folder_path):
                    for item in os.listdir(video_folder_path):
                        full_path = os.path.join(video_folder_path, item)
                        if os.path.isfile(full_path):
                            file_ext = os.path.splitext(item)[1].lower()
                            if file_ext in [ext.strip().lower() for ext in
                                            self.video_ext.get().replace("，", ",").split(",")]:
                                name_without_ext = os.path.splitext(item)[0]
                                relative_path = os.path.relpath(full_path, self.rom_folder.get())
                                self.video_files[name_without_ext] = relative_path.replace('\\', '/')
                else:
                    self.log_message(f"⚠️ {t.t('The video folder does not exist: %s') % video_folder_path}")
            except Exception as e:
                self.log_message(f"⚠️ {t.t('Error scanning video file：%s') % str(e)}")

        self.log_message(f"  • {t.t('Found %d video files') % len(self.video_files)}")

        # 显示匹配结果
        self.log_message(f"\n🎯 {t.t('File matching result:')}")
        matched_images = 0
        matched_videos = 0

        for rom in self.rom_files:
            rom_name = rom['name']
            image_found = rom_name in self.image_files
            video_found = rom_name in self.video_files

            if image_found:
                matched_images += 1
            if video_found:
                matched_videos += 1

            status_icons = ""
            if image_found:
                status_icons += "📊"
            if video_found:
                if status_icons != "":
                    status_icons += "+"
                status_icons += "🎬"

            if not image_found and not video_found:
                status_icons = "❌"

            self.log_message(f"  {status_icons} {rom['filename']}")

        self.log_message(f"\n📈 {t.t('Match statistics:')}")
        self.log_message(f"  • {t.t('ROM files: %d') % len(self.rom_files)}")
        self.log_message(f"  • {t.t('Match images: %d') % matched_images}")
        self.log_message(f"  • {t.t('Match videos: %d') % matched_videos}")

        self.update_progress(100, t.t("Scan completed"))
        self.update_status(f"{t.t('Scan completed - found %d ROM files') % len(self.rom_files)}")
        self.scan_issues = True
        self.switch_btn(True)

    def generate_gamelist(self):
        """生成gamelist.xml文件"""
        t = self.t
        self.switch_btn(False)
        if not self.scan_issues:
            self.create_centered_dialog(t.t("Warning"), t.t("Please scan and preview first!"), "warning")
            self.switch_btn(True)
            return

        self.result_text.delete(1.0, tk.END)
        self.log_message(f"🚀 {t.t('Starting to generate gamelist.xml')}")
        self.update_progress(0, t.t("Generating ..."))

        # 创建XML根元素
        game_list = ET.Element('gameList')

        # 为每个ROM文件创建游戏条目
        total_files = len(self.rom_files)
        for i, rom in enumerate(self.rom_files):
            game_element = ET.SubElement(game_list, 'game')

            # 路径
            path_element = ET.SubElement(game_element, 'path')
            path_element.text = f"./{rom['path']}"

            # 名称
            name_element = ET.SubElement(game_element, 'name')
            name_element.text = rom['name']

            # 描述（使用名称作为描述）
            desc_element = ET.SubElement(game_element, 'desc')
            desc_element.text = rom['name']

            # 图片
            if self.include_images.get() and rom['name'] in self.image_files:
                image_element = ET.SubElement(game_element, 'image')
                image_element.text = f"./{self.image_files[rom['name']]}"

            # 视频
            if self.include_videos.get() and rom['name'] in self.video_files:
                video_element = ET.SubElement(game_element, 'video')
                video_element.text = f"./{self.video_files[rom['name']]}"

            # 更新进度
            progress = (i + 1) / total_files * 100
            self.update_progress(progress, f"{t.t('Processing:')} {i + 1}/{total_files}")

        # 格式化XML
        rough_string = ET.tostring(game_list, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        # 移除XML声明行
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()][1:])

        pretty_xml = CommonUtils.fix_xml_special_chars(pretty_xml)

        # 添加自定义注释头
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  gamelist.xml
  generation time: {timestamp}
  generation tool: Gamelist.xml Generator {ver}
  development: G.R.H
  ROM file: {len(self.rom_files)}
  Include images: {self.include_images.get()}
  Including videos: {self.include_videos.get()}
-->
{pretty_xml}"""

        # 保存文件
        output_path = os.path.join(self.output_folder.get(), 'gamelist.xml').replace('\\', '/')

        # 备份现有文件（如果存在）
        if os.path.exists(output_path):
            try:
                backfile = f'gamelist-back-{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xml'
                backup_path = os.path.join(self.output_folder.get(), backfile).replace('\\', '/')
                shutil.copy2(output_path, backup_path)  # 使用copy2保留元数据
                self.log_message(f"📦 {t.t('Backup existing gamelist.xml to: %s') % backfile}")
            except Exception as e:
                self.log_message(f"⚠️ {t.t('Warning: Could not backup existing file: %s') % str(e)}")
                self.switch_btn(True)
                return

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            self.log_message(f"✅ {t.t('Gamelist.xml generated successfully!')}")
            self.log_message(f"  • {t.t('Save location: %s') % output_path.replace('\\', '/')}")
            self.log_message(f"  • {t.t('Including games: %d') % len(self.rom_files)}")

            # 统计匹配情况
            matched_images = sum(1 for rom in self.rom_files if rom['name'] in self.image_files)
            matched_videos = sum(1 for rom in self.rom_files if rom['name'] in self.video_files)

            self.log_message(f"  • {t.t('Match images: %d') % matched_images}")
            self.log_message(f"  • {t.t('Match videos: %d') % matched_videos}")

            self.update_progress(100, t.t("Generation completed"))
            self.update_status(
                f"{t.t('Gamelist.xml generated successfully - contains %d games') % len(self.rom_files)}")

            self.create_centered_dialog(t.t("Success"),
                                f"{t.t('Gamelist.xml generated successfully!\ncontains %d games') % len(self.rom_files)}")
            self.scan_issues = False
            self.switch_btn(True)

        except Exception as e:
            self.create_centered_dialog(t.t("Error"), f"{t.t('Error saving file:')} {str(e)}", "error")
            self.log_message(f"❌ {t.t('Error saving file:')} {str(e)}")

    def reset_all(self):
        """重置所有设置"""
        t = self.t
        self.switch_btn(False)
        result = self.create_centered_dialog(t.t("Confirm reset"), t.t("Are you sure you want to reset all settings?"),
                                             "askyesno")
        if result:
            self.rom_folder.set("")
            self.image_folder.set("images")
            self.video_folder.set("videos")
            self.output_folder.set("")
            self.extensions.set(".zip,.7z,.nes,.smc,.gb,.gbc,.gba,.nds,.iso,.bin,.chd")
            self.image_ext.set(".png,.jpg,.jpeg")
            self.video_ext.set(".mp4")
            self.include_images.set(False)
            self.include_videos.set(False)
            self.image_ext_entry.config(state="disabled")
            self.image_folder_entry.config(state="disabled")
            self.video_ext_entry.config(state="disabled")
            self.video_folder_entry.config(state="disabled")
            self.rom_files.clear()
            self.image_files.clear()
            self.video_files.clear()
            self.result_text.delete(1.0, tk.END)
            self.update_progress(0, "就绪")
            self.update_status("就绪")
        self.switch_btn(True)


class PegasusConverterFrame(BaseFrame):
    def __init__(self, parent, gamelistgeneratorframe: GamelistGeneratorFrame, translator: Translator):
        super().__init__(parent, translator)
        self.parent = parent
        self.gg = gamelistgeneratorframe

        # 初始化变量
        self.out_type = tk.IntVar(value=1)
        self.out_mode = tk.IntVar(value=1)
        self.cb_var1 = tk.BooleanVar(value=True)
        self.cb_var2 = tk.BooleanVar(value=False)
        self.folder_path = tk.StringVar()
        self.folder_path2 = tk.StringVar()

        self.scan_is_done = False
        self.source_path = ""
        self.target_path = ""
        self.games = []
        self.dialog_result = None

        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        t = self.t
        main_frame = ttk.Frame(self, padding="8")
        main_frame.pack(fill='both', expand=True)

        config_frame = ttk.Frame(main_frame)
        config_frame.pack(fill='x', pady=(0, 8))

        left_config = ttk.Frame(config_frame)
        left_config.pack(side='left', fill='both', expand=True, padx=(0, 8))

        right_config = ttk.Frame(config_frame)
        right_config.pack(side='right', fill='both', expand=True, padx=(8, 0))

        folder_section = ttk.LabelFrame(left_config, text=f"{t.t('Folder Settings')}", padding="10",
                                        style="Section.TLabelframe")
        folder_section.pack(fill='both', expand=True, pady=(0, 10))

        source_frame = ttk.Frame(folder_section)
        source_frame.pack(fill='x', pady=(0, 8))

        ttk.Label(source_frame, text=f"{t.t('Game source folder:')}", font=(self.font_family, 9)).pack(anchor='w')

        source_input_frame = ttk.Frame(source_frame)
        source_input_frame.pack(fill='x', pady=(3, 0))

        folder_entry = ttk.Entry(source_input_frame, textvariable=self.folder_path, font=(self.font_family, 8))
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 6))

        browse_btn = ttk.Button(source_input_frame, text=f"{t.t('Browse...')}", command=self.browse_folder)
        browse_btn.pack(side='right')

        target_frame = ttk.Frame(folder_section)
        target_frame.pack(fill='x', pady=(8, 0))

        ttk.Label(target_frame, text=f"{t.t('Output folder:')}", font=(self.font_family, 9)).pack(anchor='w')

        target_input_frame = ttk.Frame(target_frame)
        target_input_frame.pack(fill='x', pady=(3, 0))

        folder_entry2 = ttk.Entry(target_input_frame, textvariable=self.folder_path2, font=(self.font_family, 8))
        folder_entry2.pack(side='left', fill='x', expand=True, padx=(0, 6))

        browse_btn2 = ttk.Button(target_input_frame, text=f"{t.t('Browse...')}", command=self.browse_folder2)
        browse_btn2.pack(side='right')

        # 按钮区域
        button_frame = ttk.Frame(left_config)
        button_frame.pack(fill='x', pady=10)

        button_inner_frame = ttk.Frame(button_frame)
        button_inner_frame.pack()

        self.scan_btn = ttk.Button(button_inner_frame, text=f"{t.t('Scan game')}",
                                   command=self.scan_files, style="Action.TButton", width=17)
        self.scan_btn.pack(side='left', padx=(0, 8))

        self.cove_btn = ttk.Button(button_inner_frame, text=f"{t.t('Converter')}",
                                   command=self.convert_files, style="Action.TButton", width=17)
        self.cove_btn.pack(side='left', padx=(0, 8))

        self.reset_btn = ttk.Button(button_inner_frame, text=f"☢ {t.t('Reset')}",
                                    command=self.reset_all, style="Action.TButton", width=17)
        self.reset_btn.pack(side='left')

        output_section = ttk.LabelFrame(right_config, text=f"{t.t('Output settings')}", padding="10",
                                        style="Section.TLabelframe")
        output_section.pack(fill='both', expand=True)

        type_frame = ttk.LabelFrame(output_section, text=f"{t.t('Adaptation type')}", padding="6")
        type_frame.pack(fill='x', pady=(0, 8))

        out_type_1 = ttk.Radiobutton(type_frame, variable=self.out_type,
                                     text=f"{t.t('H700 front-end')}", command=self.on_output_type_change, value=1)
        out_type_1.pack(anchor='w', pady=2)
        out_type_2 = ttk.Radiobutton(type_frame, variable=self.out_type,
                                     text=f"{t.t('ES (including gamelist.xml game list)')}",
                                     command=self.on_output_type_change, value=2)
        out_type_2.pack(anchor='w', pady=2)

        mode_frame = ttk.LabelFrame(output_section, text=f"{t.t('Generation method')}", padding="6")
        mode_frame.pack(fill='x', pady=(0, 8))

        out_mode_1 = ttk.Radiobutton(mode_frame, variable=self.out_mode,
                                     text=f"{t.t('Normal mode (retaining source game files)')}", value=1)
        out_mode_1.pack(anchor='w', pady=2)
        out_mode_2 = ttk.Radiobutton(mode_frame, variable=self.out_mode,
                                     text=f"{t.t('Speed mode (moving source game files)')}", value=2)
        out_mode_2.pack(anchor='w', pady=2)

        media_frame = ttk.LabelFrame(output_section, text=f"{t.t('Output media')}", padding="6")
        media_frame.pack(fill='x')

        self.out_media_1 = ttk.Checkbutton(media_frame, variable=self.cb_var1, text=f"{t.t('Game Preview Image')}")
        self.out_media_1.pack(anchor='w', pady=3)
        self.out_media_2 = ttk.Checkbutton(media_frame, variable=self.cb_var2,
                                           command=self.on_video_checkbox_click, text=f"{t.t('Game Preview Video')}")
        self.out_media_2.pack(anchor='w', pady=3)

        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=(0, 5))

        ttk.Label(progress_frame, text=f"{t.t('Process:')}", font=(self.font_family, 9, "bold")).pack(anchor='w',
                                                                                                      pady=(0, 6))
        self.progress = ttk.Progressbar(progress_frame, style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill='x')

        self.progress_label = ttk.Label(progress_frame, text="0%", font=(self.font_family, 9))
        self.progress_label.pack(anchor='e', pady=(3, 0))

        result_section = ttk.LabelFrame(main_frame, text=f"{t.t('Scan results')}", padding="12",
                                        style="Section.TLabelframe")
        result_section.pack(fill='both', expand=True)

        self.stats_frame = ttk.Frame(result_section)
        self.stats_frame.pack(fill='x', pady=(0, 8))

        self.games_count = ttk.Label(self.stats_frame, text=f"{t.t('Find the game:')} 0",
                                     font=(self.font_family, 9, "bold"))
        self.games_count.pack(side='left')

        self.status_label = ttk.Label(self.stats_frame, text=f"{t.t('Status: Ready')}", font=(self.font_family, 9))
        self.status_label.pack(side='right')

        text_frame = ttk.Frame(result_section)
        text_frame.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        self.result_text = tk.Text(text_frame, yscrollcommand=scrollbar.set,
                                   wrap='word', font=("Consolas", 9),
                                   padx=10, pady=10, height=12,
                                   bg="#f8f9fa", fg="#2c3e50",
                                   selectbackground="#3498db", selectforeground="white")
        self.result_text.pack(side='left', fill='both', expand=True)

        scrollbar.config(command=self.result_text.yview)

    def switch_btn2(self, button):
        if button:
            self.scan_btn.config(state='normal')
            self.cove_btn.config(state='normal')
            self.reset_btn.config(state='normal')
        else:
            self.scan_btn.config(state='disabled')
            self.cove_btn.config(state='disabled')
            self.reset_btn.config(state='disabled')

    def reset_all(self):
        """重置所有设置"""
        t = self.t
        self.switch_btn2(False)
        result = self.create_centered_dialog(t.t("Confirm reset"), t.t("Are you sure you want to reset all settings?"),
                                             "askyesno")
        if result:
            self.folder_path.set("")
            self.folder_path2.set("")
            self.out_type.set(1)
            self.out_mode.set(1)
            self.cb_var1.set(True)
            self.cb_var2.set(False)
            self.result_text.delete(1.0, tk.END)
            self.games_count.config(text="🎯 找到游戏: 0")
            self.games.clear()
            self.update_status(t.t("Settings have been reset"))
            self.update_progress(0, "0%")
        self.switch_btn2(True)

    def browse_folder(self):
        """浏览原文件夹"""
        t = self.t
        folder_selected = filedialog.askdirectory(title=t.t("Select game source folder"))
        if folder_selected:
            if os.path.exists(os.path.join(folder_selected, 'metadata.pegasus.txt')):
                self.folder_path.set(folder_selected)
                self.folder_path2.set(folder_selected)
                self.update_status(t.t("Selected source folder"))
                self.result_text.insert(tk.END, f"📁 {t.t('Selected source folder:')} {folder_selected}\n")
                self.scan_is_done = False
            else:
                self.create_centered_dialog(t.t("Error"),
                                            t.t("The selected folder does not contain the metadata.pegasus.txt file!"),
                                            "error")

    def browse_folder2(self):
        """浏览目标文件夹"""
        t = self.t
        if not self.folder_path.get():
            self.create_centered_dialog(t.t("Error"), t.t("Please select the game source folder first!"), "error")
            return
        folder_selected = filedialog.askdirectory(title=t.t("Select output destination folder"))
        if folder_selected:
            self.folder_path2.set(folder_selected)
            self.update_status(t.t("Selected output folder"))
            self.result_text.insert(tk.END, f"📁 {t.t('Selected output folder:')} {folder_selected}\n")

    def on_output_type_change(self):
        """输出类型改变时的处理"""
        t = self.t
        if self.out_type.get() == 1:  # H700前端
            self.cb_var2.set(False)  # 禁用视频选项
            self.result_text.insert(tk.END, f"🔄 {t.t('Switch to H700 front-end mode')}\n")
        else:  # ES前端
            self.result_text.insert(tk.END, f"🔄 {t.t('Switch to ES front-end mode')}\n")

    def on_video_checkbox_click(self):
        """视频复选框点击处理"""
        t = self.t
        if self.out_type.get() == 1 and self.cb_var2.get():
            self.create_centered_dialog(t.t("Error"),
                                        t.t("H700 front-end does not support game preview videos, please choose ES front-end!"),
                                        "error")
            self.cb_var2.set(False)

    def update_status(self, message):
        """更新状态信息"""
        t = self.t
        self.status_label.config(text=f"✅ {t.t('Status:')} {message}")
        self.update()

    def update_progress(self, value, text=None):
        """更新进度条"""
        self.progress['value'] = value
        if text is None:
            text = f"{int(value)}%"
        self.progress_label.config(text=text)
        self.update()

    def scan_files(self):
        """扫描文件并提取游戏信息"""
        t = self.t
        self.switch_btn2(False)
        if not self.validate_inputs():
            self.switch_btn2(True)
            return

        self.games.clear()
        self.result_text.delete(1.0, tk.END)
        self.update_status(t.t("Scanning ..."))
        self.update_progress(0, t.t("Start scanning ..."))

        try:
            metadata_file = os.path.join(self.folder_path.get(), 'metadata.pegasus.txt').replace('/', '\\')
            metadata_file = os.path.abspath(metadata_file)
            self.result_text.insert(tk.END, f"🔍 {t.t('Scanning file:')} {metadata_file}\n")

            with open(metadata_file, 'r', encoding='utf-8') as f:
                text = f.read()
                game_blocks = text.strip().split('\n\n')

                for block in game_blocks:
                    if not block.strip().startswith('game:'):
                        continue

                    game_info = self.parse_game_block(block)
                    if game_info:
                        self.games.append(game_info)

            self.display_results()
            self.scan_is_done = True
            self.switch_btn2(True)

        except Exception as e:
            self.create_centered_dialog(t.t("Error"),
                                        f"{t.t('An error occurred during the scanning process:')} {str(e)}", "error")
            self.update_status(t.t("Scan error"))
            self.update_progress(0, t.t("Scan failed"))
            self.switch_btn2(True)

    def parse_game_block(self, block):
        """解析游戏信息块"""
        game_info = {}
        lines = block.strip().split('\n')

        for line in lines:
            if line.startswith('game:'):
                game_info['game'] = line.replace('game:', '').strip()
            elif line.startswith('file:'):
                game_info['file'] = line.replace('file:', '').strip()
            elif line.startswith('developer:'):
                game_info['developer'] = line.replace('developer:', '').strip()
            elif line.startswith('description:'):
                game_info['description'] = line.replace('description:', '').strip()

        # 验证必要字段
        required_fields = ['game', 'file', 'developer', 'description']
        if all(key in game_info for key in required_fields):
            return game_info
        return None

    def validate_inputs(self):
        """验证输入参数"""
        t = self.t
        folder_path = self.folder_path.get()
        if not folder_path:
            self.create_centered_dialog(t.t("Error"), t.t("Please select the game source folder first!"), "error")
            return False

        if not os.path.exists(folder_path):
            self.create_centered_dialog(t.t("Error"), t.t("The selected folder does not exist!"), "error")
            return False

        if self.out_type.get() == 0:
            self.create_centered_dialog(t.t("Error"), t.t("Please select the output type!"), "error")
            return False

        if self.out_mode.get() == 0:
            self.create_centered_dialog(t.t("Error"), t.t("Please choose the output method!"), "error")
            return False

        return True

    def display_results(self):
        """显示扫描结果"""
        t = self.t
        if self.games:
            self.games_count.config(text=f"🎯 {t.t('Find the game:')} {len(self.games)}")

            # 添加结果标题
            self.result_text.insert(tk.END, f"• {t.t('Scan completed! Found% d games in total') % len(self.games)}\n")

            # 显示配置信息
            output_type = t.t("H700 front-end") if self.out_type.get() == 1 else t.t("ES front-end")
            output_mode = t.t("Normal mode (copy)") if self.out_mode.get() == 1 else t.t("Speed mode (move)")
            resources = []
            if self.cb_var1.get():
                resources.append(t.t("preview image"))
            if self.cb_var2.get():
                resources.append(t.t("Preview video "))

            self.result_text.insert(tk.END, f"• {t.t('Output settings:')} {output_type} | {output_mode}\n")
            self.result_text.insert(tk.END,
                                    f"• {t.t('Output resources:')} {', '.join(resources) if resources else t.t('None')}\n")
            self.result_text.insert(tk.END, "=" * 60 + "\n")
            # 添加操作提示
            self.result_text.insert(tk.END,
                                    f"💡 {t.t('Tip: You can click the ❃ %s button to convert game resources') % t.t('Converter')}\n")
            self.result_text.insert(tk.END, "=" * 60 + "\n\n")
            self.result_text.insert(tk.END, t.t("Game details:") + "\n")

            # 显示游戏列表
            for i, game in enumerate(self.games, 1):
                self.result_text.insert(tk.END, f"🎮 {t.t('Game')} {i}:\n")
                self.result_text.insert(tk.END, f"   {t.t('Name:')} {game['game']}\n")
                self.result_text.insert(tk.END, f"   {t.t('File:')} {game['file']}\n")
                self.result_text.insert(tk.END, f"   {t.t('Description:')} {game['description']}\n")
                self.result_text.insert(tk.END, "-" * 50 + "\n\n")

                self.update_progress((i / len(self.games)) * 100, f"{t.t('Display result:')} {i}/{len(self.games)}")

            self.update_status(t.t("Scan completed"))
            self.update_progress(100, t.t("Scan completed"))

        else:
            self.result_text.insert(tk.END, f"❌ {t.t('No game information was found in the specified folder.')}\n")
            self.update_status(t.t("Game not found"))
            self.update_progress(0, t.t("Game not found"))

    def convert_files(self):
        """转换文件"""
        t = self.t
        self.switch_btn2(False)
        if not self.games or not self.scan_is_done:
            self.create_centered_dialog(t.t("Warning"), f"⚠️ {t.t('Please scan the game files first!')}", "warning")
            self.switch_btn2(True)
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.result_text.insert(tk.END, f"✨ {t.t('Start converting game resources ...')}\n\n")

        error_list = []

        try:
            self.update_status(t.t("Converting ..."))
            self.update_progress(0, t.t("Prepare to convert ..."))

            source_path = self.folder_path.get()
            target_path = self.folder_path2.get()

            # 创建输出目录
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            roms_path = os.path.join(f"{target_path}/{os.path.basename(target_path)}_pegasus_{timestamp}").replace('/',
                                                                                                                   '\\')
            media_path = os.path.join(roms_path, "Imgs")

            os.makedirs(media_path, exist_ok=True)

            success_count = 0
            total_count = len(self.games)

            for i, game in enumerate(self.games, 1):

                try:
                    self.result_text.insert(tk.END, f"🎮 {t.t('Processing:')} {game['file']}\n")
                    success = self.process_game_files(game, source_path, roms_path, media_path)
                    if success:
                        success_count += 1
                        status_icon = "✅"
                    else:
                        status_icon = "⚠️"
                        error_list.append(game['file'])
                    self.result_text.insert(tk.END,
                                            f"{status_icon} {t.t('Complete')} {i}/{total_count}: {game['file']}\n")
                    self.result_text.see(tk.END)

                except Exception as e:
                    status_icon = "❌"  # 默认设置为失败状态
                    self.result_text.insert(tk.END,
                                            f"{status_icon} {t.t('Failure')} {i}/{total_count}: {game['file']} - {str(e)}\n")
                    self.result_text.see(tk.END)
                    error_list.append(game['file'])

                self.update_progress((i / total_count) * 100, f"{t.t('Converting:')} {i}/{total_count}")

            # 输出错误列表
            if error_list:
                self.result_text.insert(tk.END, "-" * 60 + "\n")
                self.result_text.insert(tk.END, f"❌ {t.t('Games with conversion issues:')}\n\n")
                for error_file in error_list:
                    self.result_text.insert(tk.END, f"   • {error_file}\n")
                self.result_text.see(tk.END)

            # 生成前端配置文件
            if self.out_type.get() == 2:  # ES前端
                self.generate_es_config(roms_path)

            self.update_status(t.t("Conversion completion"))
            self.update_progress(100, t.t("Conversion completion"))

            # 显示最终结果
            self.result_text.insert(tk.END, "-" * 60 + "\n")
            self.result_text.insert(tk.END, f"📊 {t.t('Statistical information:')}\n")
            self.result_text.insert(tk.END, f"• {t.t('Total number of games:')} {total_count}\n")
            self.result_text.insert(tk.END, f"• {t.t('Successful conversion:')} {success_count}\n")
            self.result_text.insert(tk.END, f"• {t.t('Failed:')} {total_count - success_count}\n")
            self.result_text.insert(tk.END, "\n")
            self.result_text.insert(tk.END, f"📁 {t.t('Output directory:')}\n")
            self.result_text.insert(tk.END, roms_path)
            self.result_text.see(tk.END)
            self.scan_is_done = False
            self.switch_btn2(True)

        except Exception as e:
            self.create_centered_dialog(t.t("Error"),
                                        f"{t.t('An error occurred during the conversion process:')} {str(e)}", "error")
            self.update_status(t.t("Conversion error"))
            self.update_progress(0, t.t("Conversion failed"))
            self.switch_btn2(True)

    def process_game_files(self, game, source_path, roms_path, media_path):
        """处理单个游戏的资源文件"""
        t = self.t
        game_base_name = str(game['game'])
        media_subdir = os.path.join(str(source_path), 'media', game_base_name)
        if not os.path.exists(media_subdir):
            media_subdir = os.path.join(str(source_path), 'media', os.path.splitext(game['file'])[0])

        # 处理游戏ROM文件
        rom_source = os.path.join(source_path, str(game['file']))
        rom_target = os.path.join(roms_path, str(game['file']))

        if os.path.exists(rom_source):
            if self.out_mode.get() == 1:  # 正常模式 - 复制
                shutil.copy2(rom_source, rom_target)
            else:  # 快速模式 - 移动
                shutil.move(rom_source, rom_target)
        else:
            self.result_text.insert(tk.END, f"⚠️ {t.t('ROM file does not exist:')} {game['file']}\n")
            return False

        success = True
        # 处理预览图 - 支持jpg和png格式
        if self.cb_var1.get():
            image_extensions = ['.jpg', '.png']
            image_found = False
            for ext in image_extensions:
                image_source = os.path.join(media_subdir, f'boxFront{ext}')
                image_target = os.path.join(media_path, f"{game_base_name}{ext}")

                if os.path.exists(image_source):
                    if self.out_mode.get() == 1:  # 正常模式 - 复制
                        shutil.copy2(image_source, image_target)
                    else:  # 快速模式 - 移动
                        shutil.move(image_source, image_target)
                    image_found = True
                    break

            if not image_found:
                self.result_text.insert(tk.END,
                                        f"⚠️ {t.t('Preview image does not exist: %s (tried JPG and PNG formats)') % game_base_name}\n")
                success = False

        # 处理预览视频（仅ES前端支持）
        if self.cb_var2.get() and self.out_type.get() == 2:
            video_source = os.path.join(media_subdir, 'video.mp4')
            video_target = os.path.join(media_path, f"{game_base_name}.mp4")

            if os.path.exists(video_source):
                if self.out_mode.get() == 1:
                    shutil.copy2(video_source, video_target)
                else:
                    shutil.move(video_source, video_target)
            else:
                self.result_text.insert(tk.END,
                                        f"⚠️ {t.t('Preview video does not exist:')} {os.path.basename(video_source)}\n")
                success = False

        return success

    def generate_es_config(self, roms_path):
        """生成ES前端的gamelist.xml配置文件"""
        t = self.t
        try:
            gamelist_path = os.path.join(roms_path, 'gamelist.xml')

            with open(gamelist_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<!-- Generated by Pegasus Game Resource Converter (G.R.H) -->\n')
                f.write('<gameList>\n')

                for game in self.games:
                    game_base_name = os.path.splitext(game['file'])[0]
                    f.write('  <game>\n')
                    f.write(f'    <path>./{CommonUtils.fix_xml_special_chars(game["file"])}</path>\n')
                    f.write(f'    <name>{CommonUtils.fix_xml_special_chars(game["game"])}</name>\n')
                    f.write(f'    <desc>{CommonUtils.fix_xml_special_chars(game["description"])}</desc>\n')

                    # 检查图片是否存在（支持jpg和png）
                    if self.cb_var1.get():
                        image_extensions = ['.jpg', '.png']
                        for ext in image_extensions:
                            image_path = os.path.join(roms_path, 'Imgs', f"{game_base_name}{ext}")
                            if os.path.exists(image_path):
                                f.write(
                                    f'    <image>./Imgs/{CommonUtils.fix_xml_special_chars(game_base_name)}{ext}</image>\n')
                                break

                    if self.cb_var2.get():
                        f.write(f'    <video>./Imgs/{CommonUtils.fix_xml_special_chars(game_base_name)}.mp4</video>\n')

                    f.write('  </game>\n')

                f.write('</gameList>\n')

            self.result_text.insert(tk.END, "\n" + "-" * 60 + "\n")
            self.result_text.insert(tk.END,
                                    f"✅ {t.t('ES front-end configuration file has been generated:')} gamelist.xml\n")

        except Exception as e:
            self.result_text.insert(tk.END, "\n" + "-" * 60 + "\n")
            self.result_text.insert(tk.END, f"❌ {t.t('Failed to generate ES configuration file:')} {str(e)}\n")
        self.result_text.see(tk.END)


class MainApplication:
    def __init__(self, root, translator: Translator):
        self.root = root
        self.t = translator
        self.settings_manager = SettingsManager()

        # 从设置中加载语言
        saved_language = self.settings_manager.get("language", "en-US")
        self.translator = Translator()
        self.translator.load_language(saved_language)

        self.root.title(f"{self.translator.t('Game Tool Collection')} {ver}")
        self.root.resizable(True, True)
        CommonUtils.center_window(self.root, 900, 1000)

        # 设置窗口图标
        try:
            prog_path = os.path.abspath(__file__)
            self.ico_path = os.path.join(os.path.dirname(prog_path), 'icon', 'icon.ico')
            myappid = f'com.grh.GameTools.{ver}'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.root.iconbitmap(self.ico_path)
        except:
            pass

        # 初始化翻译器
        self.gg = GamelistGeneratorFrame(self.root, self.translator)
        self.font_family = self.gg.font_family

        self.create_widgets()

    def create_widgets(self):
        """创建主界面组件"""
        t = self.t
        # 创建菜单
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=False)
        languagemenu = tk.Menu(menubar, tearoff=False)
        helpmenu = tk.Menu(menubar, tearoff=False)

        menubar.add_cascade(label=self.translator.t("File"), menu=filemenu)
        menubar.add_cascade(label=self.translator.t("Language"), menu=languagemenu)
        menubar.add_cascade(label=self.translator.t("Help"), menu=helpmenu)

        filemenu.add_command(label=self.translator.t("Exit"), command=self.exit_application)
        helpmenu.add_command(label=self.translator.t("About"), command=self.show_about)

        # 添加语言选项
        for lang_code, lang_name in self.translator.available_languages:
            languagemenu.add_command(
                label=f"√ {lang_name}" if self.settings_manager.get("language",
                                                                    "en-US") == lang_code else f"   {lang_name}",
                command=lambda lc=lang_code: self.change_language(lc)
            )

        # 创建选项卡
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建Gamelist生成器选项卡
        self.gamelist_frame = GamelistGeneratorFrame(notebook, self.translator)
        notebook.add(self.gamelist_frame, text=f"🎮 {self.translator.t('Gamelist Generator')}")

        # 创建Gamelist编辑器选项卡
        self.editor_frame = GamelistEditorFrame(notebook, self.translator)
        notebook.add(self.editor_frame, text=f"📋 {self.translator.t('Gamelist Editor')}")

        # 创建Gamelist拼音修改器选项卡
        self.update_frame = GamelistPinyinFrame(notebook, self.translator)
        notebook.add(self.update_frame, text=f"🀄 {self.translator.t('Gamelist Pinyin')}")

        # 创建ROM文件名修改器选项卡
        self.romname_frame = GameRomNameFrame(notebook, self.translator)
        notebook.add(self.romname_frame, text=f"📝 {self.translator.t('ROM Name Editor')}")

        # 创建天马转换器选项卡
        self.pegasus_frame = PegasusConverterFrame(notebook, self.gg, self.translator)
        notebook.add(self.pegasus_frame, text=f"🐎 Pegasus {self.translator.t('Converter')}")

    def change_language(self, lang_code):
        """切换语言"""
        if lang_code != self.translator.lang_code:
            # 保存语言设置
            self.settings_manager.set("language", lang_code)

            # 重新加载语言
            self.translator.load_language(lang_code)

            # 重新创建界面
            for widget in self.root.winfo_children():
                widget.destroy()
            self.create_widgets()

            # 更新窗口标题
            self.root.title(f"{self.translator.t('Game Tool Collection')} {ver}")

    def show_about(self):
        """显示关于信息"""
        about_text = f"{self.translator.t('AboutText').format(ver=ver)}\nMake by 上帝之右手"
        dialog = tk.Toplevel(self.root)
        dialog.title(self.translator.t("About"))
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.configure(bg="#e8f5e8")

        content_frame = ttk.Frame(dialog, padding="20")
        content_frame.pack(fill='both', expand=True)

        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 15))

        icon_label = ttk.Label(header_frame, text="ℹ️", font=(self.font_family, 15),
                               foreground="#2e7d32")
        icon_label.pack(side='left', padx=(0, 10))

        title_label = ttk.Label(header_frame, text=self.translator.t("About"), font=(self.font_family, 12, "bold"),
                                foreground="#2e7d32")
        title_label.pack(side='left')

        message_frame = ttk.Frame(content_frame)
        message_frame.pack(fill='x', pady=(0, 20))

        message_label = ttk.Label(message_frame, text=about_text, font=(self.font_family, 10),
                                  justify='left', wraplength=400)
        message_label.pack(anchor='w')

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x')

        ok_button = ttk.Button(button_frame, text=self.translator.t("Ok"),
                               command=dialog.destroy, width=12)
        ok_button.pack(side='right')

        # 居中对话框
        CommonUtils.center_dialog(dialog, self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def exit_application(self):
        """退出应用程序"""
        self.root.quit()
        self.root.destroy()


def main():
    root = tk.Tk()
    translator = Translator()
    app = MainApplication(root, translator)
    root.mainloop()


if __name__ == "__main__":
    main()
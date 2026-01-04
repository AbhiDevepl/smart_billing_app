import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DB_PATH = os.path.join(DATA_DIR, 'app.db')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
    INVOICE_DIR = os.path.join(BASE_DIR, 'invoices')
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    
    APP_TITLE = "Smart Battery Billing"
    WINDOW_SIZE = "1200x800"
    SETTINGS_PATH = os.path.join(DATA_DIR, 'settings.json')
    # Theme Configuration
    THEME = "dark"  # "light" or "dark"

    @staticmethod
    def load_settings(path=None):
        import json
        p = path or Config.SETTINGS_PATH
        if os.path.exists(p):
            try:
                with open(p, 'r') as f:
                    return json.load(f)
            except Exception: pass
        return {}

    @staticmethod
    def save_settings(settings):
        import json
        try:
            with open(Config.SETTINGS_PATH, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception: pass

    # Initialize dynamic paths via a direct call before it becomes a staticmethod
    _settings_loader = lambda p: Config.load_settings(p) # This still needs Config name which might fail
    # Let's use a more direct way
    import json as _json
    _init_settings = {}
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r') as _f:
                _init_settings = _json.load(_f)
        except: pass
    
    INVOICE_DIR = _init_settings.get('invoice_path', os.path.join(BASE_DIR, 'invoices'))
    
    PALETTES = {
        "light": {
            "bg": "#F8F9FA",
            "fg": "#212529",
            "accent": "#007BFF",
            "card_bg": "#FFFFFF",
            "border": "#DEE2E6",
            "danger": "#DC3545",
            "sidebar_bg": "#FFFFFF",
            "sidebar_fg": "#495057",
            "sidebar_active": "#E7F1FF",
            "header_bg": "#FFFFFF"
        },
        "dark": {
            "bg": "#121212",
            "fg": "#E0E0E0",
            "accent": "#0D47A1",
            "card_bg": "#1E1E1E",
            "border": "#333333",
            "danger": "#CF6679",
            "sidebar_bg": "#1A1A1A",
            "sidebar_fg": "#B0B0B0",
            "sidebar_active": "#2C2C2C",
            "header_bg": "#1E1E1E"
        }
    }

    @staticmethod
    def get_qss(theme):
        p = Config.PALETTES[theme]
        return f"""
            QMainWindow, QWidget {{
                background-color: {p['bg']};
                color: {p['fg']};
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            
            /* Sidebar Navigation */
            #Sidebar {{
                background-color: {p['sidebar_bg']};
                border-right: 1px solid {p['border']};
                min-width: 220px;
                max-width: 220px;
            }}
            
            QPushButton#NavButton {{
                background-color: transparent;
                color: {p['sidebar_fg']};
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                margin: 4px 10px;
            }}
            
            QPushButton#NavButton:hover {{
                background-color: {p['bg']};
            }}
            
            QPushButton#NavButton[active="true"] {{
                background-color: {p['sidebar_active']};
                color: {p['accent']};
                font-weight: bold;
            }}
            
            /* Main Content Area */
            #TopBar {{
                background-color: {p['header_bg']};
                border-bottom: 1px solid {p['border']};
                padding: 10px 30px;
            }}
            
            #ContentArea {{
                background-color: {p['bg']};
            }}
            
            /* Cards and Containers */
            #Card {{
                background-color: {p['card_bg']};
                border: 1px solid {p['border']};
                border-radius: 12px;
            }}
            
            #Card:hover {{
                background-color: {p['border']}22;
                border: 1px solid {p['accent']}44;
            }}
            
            #SectionHeader {{
                font-size: 24px;
                font-weight: 700;
                color: {p['fg']};
            }}
            
            #SubHeader {{
                font-size: 16px;
                font-weight: 600;
                color: {p['fg']};
            }}
            
            #Description {{
                font-size: 13px;
                color: {p['fg']}88;
                line-height: 1.4;
            }}
            
            /* Inputs and Forms */
            QLineEdit, QComboBox, QPlainTextEdit {{
                border: 1px solid {p['border']};
                border-radius: 8px;
                padding: 10px 14px;
                background-color: {p['bg']};
                color: {p['fg']};
                font-size: 14px;
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {p['accent']};
                background-color: {p['card_bg']};
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {p['accent']};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                border: none;
            }}
            
            QPushButton:hover {{
                background-color: {p['accent']}ee;
            }}
            
            QPushButton#Secondary {{
                background-color: transparent;
                color: {p['fg']};
                border: 1px solid {p['border']};
            }}
            
            QPushButton#Secondary:hover {{
                background-color: {p['border']}44;
            }}
            
            QPushButton#Danger {{
                background-color: {p['danger']};
            }}
            
            /* Table Styling */
            QTableWidget {{
                background-color: {p['card_bg']};
                border: 1px solid {p['border']};
                border-radius: 8px;
                gridline-color: {p['border']}33;
            }}
            
            QHeaderView::section {{
                background-color: {p['bg']};
                padding: 12px;
                border: none;
                border-bottom: 1px solid {p['border']};
                font-weight: 700;
                font-size: 12px;
                color: {p['fg']}88;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            QTableWidget::item {{
                padding: 12px;
            }}
            
            /* Status Badges */
            QLabel#BadgeSuccess {{ background-color: #E8F5E9; color: #2E7D32; border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; }}
            QLabel#BadgeWarning {{ background-color: #FFF3E0; color: #EF6C00; border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; }}
            QLabel#BadgeDanger {{ background-color: #FFEBEE; color: #C62828; border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {p['border']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {p['fg']}33;
            }}
        """

    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(INVOICE_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

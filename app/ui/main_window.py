from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QStatusBar, QFrame, QLabel)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from app.config import Config
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Config.APP_TITLE)
        self.resize(1280, 800)
        self.current_theme = Config.THEME
        self.screens = {}
        self.nav_buttons = {}
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        # Logo / Brand
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(25, 10, 25, 30)
        
        logo_lbl = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_lbl.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_lbl.setText("🔋 SmartBill")
            logo_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #007BFF;")
        
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_lbl)
        sidebar_layout.addWidget(logo_container)

        self.create_nav_button("Dashboard", "🏠", self.show_dashboard)
        self.create_nav_button("New Bill", "🛒", self.show_billing)
        self.create_nav_button("Inventory", "📦", self.show_products)
        self.create_nav_button("Stock Ledger", "📊", self.show_stock)
        
        sidebar_layout.addStretch()
        
        self.btn_theme = QPushButton(" Toggle Theme")
        self.btn_theme.setObjectName("NavButton")
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        self.main_layout.addWidget(self.sidebar)

        # 2. Right Side
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        top_bar_layout = QHBoxLayout(self.top_bar)
        
        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        top_bar_layout.addWidget(self.lbl_page_title)
        
        top_bar_layout.addStretch()

        self.btn_refresh = QPushButton(" 🔄 Refresh ")
        self.btn_refresh.setObjectName("Secondary")
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.clicked.connect(self.refresh_current_screen)
        top_bar_layout.addWidget(self.btn_refresh)
        
        right_layout.addWidget(self.top_bar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")
        right_layout.addWidget(self.stack)

        self.main_layout.addWidget(right_container)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.show_dashboard()

    def create_nav_button(self, text, icon, callback):
        btn = QPushButton(f" {icon}  {text}")
        btn.setObjectName("NavButton")
        btn.setToolTip(f"Go to {text}")
        btn.setProperty("active", "false")
        btn.clicked.connect(callback)
        self.sidebar.layout().addWidget(btn)
        self.nav_buttons[text] = btn

    def set_active_nav(self, text):
        for name, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if name == text else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.lbl_page_title.setText(text)
        self.status_bar.showMessage(f"Viewing {text}")

    def apply_theme(self):
        qss = Config.get_qss(self.current_theme)
        self.setStyleSheet(qss)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        # Refresh current screen if it has specific theme logic
        if self.stack.currentWidget():
            self.stack.currentWidget().update()

    def refresh_current_screen(self):
        screen = self.stack.currentWidget()
        if screen and hasattr(screen, 'load_data'):
            screen.load_data()
            self.status_bar.showMessage("Data Refreshed", 3000)

    def show_dashboard(self):
        self.set_active_nav("Dashboard")
        from app.ui.dashboard import Dashboard
        self._switch_screen("dashboard", Dashboard)

    def show_billing(self):
        self.set_active_nav("New Bill")
        from app.ui.billing_screen import BillingScreen
        self._switch_screen("billing", BillingScreen)

    def show_products(self):
        self.set_active_nav("Inventory")
        from app.ui.product_form import ProductForm
        self._switch_screen("products", ProductForm)

    def show_stock(self):
        self.set_active_nav("Stock Ledger")
        from app.ui.stock_screen import StockScreen
        self._switch_screen("stock", StockScreen)

    def _switch_screen(self, key, widget_class):
        if key not in self.screens:
            self.screens[key] = widget_class(controller=self)
            self.stack.addWidget(self.screens[key])
        
        self.stack.setCurrentWidget(self.screens[key])
        
        if hasattr(self.screens[key], 'load_data'):
            self.screens[key].load_data()

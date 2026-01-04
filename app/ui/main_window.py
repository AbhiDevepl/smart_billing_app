from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QStatusBar, QToolBar)
from PySide6.QtCore import Qt
from app.config import Config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Config.APP_TITLE)
        self.resize(1280, 800)
        self.current_theme = Config.THEME
        self.history = []
        self.screens = {}
        self.nav_buttons = {}
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        # Central widget and horizontal layout
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

        # Brand / Logo
        brand = QLabel("🔋 SmartBill")
        brand.setStyleSheet("font-size: 20px; font-weight: 800; color: #007BFF; margin: 10px 25px 30px 25px;")
        sidebar_layout.addWidget(brand)

        # Nav Buttons
        self.create_nav_button("Dashboard", "🏠", self.show_dashboard)
        self.create_nav_button("New Bill", "🛒", self.show_billing)
        self.create_nav_button("Inventory", "📦", self.show_products)
        self.create_nav_button("Stock Ledger", "📊", self.show_stock)
        
        sidebar_layout.addStretch()
        
        # Bottom Sidebar Action (Theme Toggle)
        self.btn_theme = QPushButton(" Toggle Theme")
        self.btn_theme.setObjectName("NavButton")
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        self.main_layout.addWidget(self.sidebar)

        # 2. Right Side (TopBar + Content)
        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # TopBar
        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        top_bar_layout = QHBoxLayout(self.top_bar)
        
        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        top_bar_layout.addWidget(self.lbl_page_title)
        top_bar_layout.addStretch()

        right_layout.addWidget(self.top_bar)

        # Stacked Widget for Screens
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")
        right_layout.addWidget(self.stack)

        self.main_layout.addWidget(self.right_container)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.show_dashboard(record_history=False)

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
        
        self.current_screen_name = screen_name
        
        # Clean up stack and add new widget
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
            
        self.stack.addWidget(screen_widget)
        self.stack.setCurrentWidget(screen_widget)
        self.update_back_button_state()

    def show_dashboard(self, record_history=True):
        from app.ui.dashboard import Dashboard
        self.switch_screen(Dashboard(self), "dashboard", record_history)

    def show_billing(self, record_history=True):
        from app.ui.billing_screen import BillingScreen
        self.switch_screen(BillingScreen(self), "billing", record_history)

    def show_products(self, record_history=True):
        from app.ui.product_form import ProductForm
        self.switch_screen(ProductForm(self), "products", record_history)

    def show_stock(self, record_history=True):
        from app.ui.stock_screen import StockScreen
        self.switch_screen(StockScreen(self), "stock", record_history)

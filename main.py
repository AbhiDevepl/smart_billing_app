import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.utils import setup_logging
from app.database import db # Initializes DB on import

def main():
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

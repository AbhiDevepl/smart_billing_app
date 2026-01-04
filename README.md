# 🔋 Smart Battery Billing System

A professional, high-performance desktop billing terminal designed for battery and inverter retailers. Built with Python and PySide6, featuring a premium dark-themed UI/UX.

## 🚀 Key Features

- **💎 Elite UI/UX**: Immersive borderless full-screen experience with smooth dark/light mode transitions.
- **🔍 Real-time Fuzzy Search**: Instant product lookup as you type in the billing screen.
- **📄 Smart Invoicing**: 
  - Automated PDF generation with custom naming: `{Customer}_{Product}_{DateTime}.pdf`.
  - Daily folder organization (e.g., `invoices/2026-01-04/`).
  - Integrated exchange logic for old battery value deductions.
- **👥 Customer Directory**: Dedicated searchable database linked directly to the billing workflow.
- **📊 Interactive Dashboard**: Real-time sales metrics and low-stock alerts with click-to-action navigation.
- **🛡️ Data Integrity**: "Soft Delete" system archives products without breaking historical invoice data.
- **⌨️ Keyboard Productivity**: Escape key back-navigation history and optimized form flows.

## 🛠️ Tech Stack

- **Framework**: PySide6 (Qt for Python)
- **Database**: SQLite3
- **PDF Core**: ReportLab
- **Styling**: QSS (Qt Style Sheets) with modern Inter typography.

## 📦 Installation & Setup

1. **Clone the project**
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Seed Demo Data** (Optional but recommended):
   ```bash
   python seed_demo_data.py
   ```
5. **Launch the Application**:
   ```bash
   python main.py
   ```

## 🏁 Project Initialization (First Run)

The application features a smart **first-launch setup**:
1. When you run `main.py` for the first time, a setup dialog will appear.
2. Select your preferred **Invoice Storage Folder**.
3. This preference is saved in `data/settings.json`, and the app will never ask again.
4. The database is automatically initialized in `data/app.db`.

## 📦 Converting to EXE (.exe)

To package the application into a standalone Windows executable, use **PyInstaller**:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```
2. **Build the Application**:
   Run this command from the project root:
   ```bash
   pyinstaller --noconsole --onefile --icon=assets/logo.png --add-data "assets;assets" main.py
   ```
   *   `--noconsole`: Hides the command window during launch.
   *   `--add-data "assets;assets"`: Manually includes your logos and icons in the build.
3. **Find the EXE**: Your standalone app will be located in the `dist/` folder.

> [!IMPORTANT]
> When running the .exe for the first time, it will still perform the "First Run" setup to ensure invoices are stored in your desired location on that machine.

## 📂 Project Structure

- `app/ui/`: All screen components (Dashboard, Billing, Inventory, Stock, Customers).
- `app/services/`: Core logic for Invoices, PDF generation, and Database management.
- `app/config.py`: Global theme, palettes, and folder settings.
- `invoices/`: Automatically organized storage for generated bills.

---
Built with ❤️ for High-Speed Retail Operations.
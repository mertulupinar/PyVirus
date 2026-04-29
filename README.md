# 🛡️ PyVirus Pro - Security Center

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

### 🚀 Modern, Fast and Powerful Python Antivirus Scanner

**Created by Mert Ulupınar** ⚡

---

## 🌟 Overview

PyVirus Pro is an advanced, multithreaded desktop antivirus scanner built with Python and PyQt5. It provides a robust malware detection engine based on file hashing and a beautiful, modern Dark Mode graphical user interface. 

The project has recently undergone a **massive architectural refactor and UI overhaul** to meet professional software development standards, ensuring high performance, thread safety, and an exceptional user experience.

---

## ✨ Key Features & Recent Upgrades

### 1. 🏗️ Professional Modular Architecture
The application was refactored from a monolithic script into a highly organized, modular package structure:
- **`core/`**: The heart of the application. Contains the business logic.
  - `database.py`: Handles signature loading, caching, and saving. Fully **thread-safe** with `threading.Lock()`.
  - `scanner.py`: Responsible for file hashing (MD5/SHA256) and parallel processing logic.
  - `quarantine.py`: Safely isolates infected files.
- **`ui/`**: The presentation layer.
  - `main_window.py`: The dashboard, managing UI state and user interactions.
  - `components.py`: Custom-built PyQt5 widgets (`ModernButton`, `StatusCard`, `AnimatedProgressBar`) with drop-shadows and rich styling.
  - `threads.py`: Asynchronous QThread workers to keep the UI responsive.
- **`utils/`**: Shared utilities like `logger.py` for centralized event logging.

### 2. ⚡ Extreme Performance Optimizations
- **Batch Processing in UI**: The previous version updated the UI table synchronously for every single file scanned, causing the app to freeze when scanning directories with thousands of files. The new `ScanThread` utilizes a `batch_results` signal, pushing updates to the UI in batches.
- **Render Optimizaton**: Table sorting is temporarily disabled during bulk inserts, resulting in a dramatic increase in rendering speed for large directories.
- **Thread-Pool Execution**: Uses `concurrent.futures.ThreadPoolExecutor` to scan multiple files concurrently without blocking the main event loop.

### 3. 🎨 Premium Dark Mode Dashboard (UI/UX)
- **Sleek Cyber-Security Theme**: Replaced the basic OS-default theme with a custom `#111827` (slate/navy) dark mode tailored for security tools.
- **Drop Shadows & Depth**: Added `QGraphicsDropShadowEffect` to cards and buttons to provide depth and a modern web-like feel.
- **Dynamic Status Indicators**: The top-right badge provides real-time system status ("Secure", "Scanning", "Threats Found").
- **Custom UI Components**: 
  - `ModernButton`: Semantic coloring (Primary, Danger, Warning) with hover and press animations.
  - `StatusCard`: Rounded borders, neat typography, and distinct icons.
  - `AnimatedProgressBar`: A sleek, thin gradient progress bar.

### 4. 🔒 Thread Safety & Bug Fixes
- Addressed race conditions in the signature database. Reading from and writing to the `virus_signatures.json` cache is now protected by thread locks, preventing data corruption during concurrent operations.
- Enhanced Thread cancellation gracefully stops the thread pool when a scan is aborted.

---

## 🛠️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PyVirus.git
   cd PyVirus
   ```

2. **Install Dependencies**
   Ensure you have Python 3.7+ installed.
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: PyQt5 is required for the GUI).*

3. **Run the Application**
   You can start the app via the main entry point:
   ```bash
   python PyVirüs.py
   ```

---

## 💻 Usage

- **Scan Directory**: Click the primary "Scan Directory" button to select a folder. The tool will recursively scan all files using multiple threads.
- **Quarantine**: If a file is marked as `⚠️ Infected`, select it from the results table and click "Quarantine Selected". The file will be safely moved to the `quarantine/` folder.
- **Manage Signatures**: Manually add or remove MD5/SHA256 hash signatures using the "Add Signature" and "Remove Signature" buttons.
- **Save Report**: Export your scan results as a `.json` or `.csv` file.

---

## 🧪 Running Tests

The refactor maintained full backward compatibility with the existing test suite. To run the unit tests:

```bash
python test_antivirus.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

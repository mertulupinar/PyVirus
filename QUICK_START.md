# ⚡ Quick Start Guide

**PyVirus - Oxynos Antivirus Scanner Pro**

Created by Oxynos 🛡️

---

## 🚀 Get Started in 5 Minutes

### 1️⃣ Installation (30 seconds)

```bash
# Clone repository
git clone https://github.com/yourusername/pyvirus.git
cd pyvirus

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ First Run (10 seconds)

```bash
# Start application
python PyVirüs.py
```

### 3️⃣ First Scan (1 minute)

1. Click **"🔍 Scan Files"** button
2. Select a folder
3. Wait for results ✅

---

## 🎯 Basic Usage

### Adding Virus Signature

```bash
# From GUI
1. Click "➕ Add Signature" button
2. Select suspicious file
3. Confirm
```

### Quarantine

```bash
# From GUI
1. Select infected file in table (red)
2. Click "🔒 Quarantine" button
3. File is moved to secure area
```

### Save Report

```bash
# From GUI
1. Click "💾 Save Report" button
2. Select format (JSON/CSV)
3. Choose location
```

---

## 💡 Advanced

### Programmatic Usage

```python
# Simple scanning
from PyVirüs import scan_file, load_virus_signatures

signatures = load_virus_signatures()
path, is_virus = scan_file("/path/to/file.exe", signatures)
print(f"Virus: {is_virus}")
```

### Parallel Scanning

```python
# Multi-file scanning
from PyVirüs import scan_files_parallel, load_virus_signatures

files = ["/path/f1.exe", "/path/f2.dll"]
signatures = load_virus_signatures()
results = scan_files_parallel(files, signatures, max_workers=4)
```

### Running Tests

```bash
# Run all tests
python test_antivirus.py

# Hash tests only
python -m unittest test_antivirus.TestHashCalculation
```

### Cloud Update

```python
from cloud_updater import CloudUpdater
from PyVirüs import load_virus_signatures, save_virus_signatures

updater = CloudUpdater()
local = load_virus_signatures()
updated = updater.update_from_cloud(local)

if updated:
    save_virus_signatures(updated)
```

---

## 📊 Performance Settings

### Increase Thread Count

```python
# In PyVirüs.py file
self.scanThread = ScanThread(
    dir_path, 
    'directory',
    parallel=True,
    max_workers=8  # 4 → 8 threads
)
```

### Adjust Cache Size

```python
# Increase hash chunk size (faster)
# PyVirüs.py > calculate_hash()
for chunk in iter(lambda: f.read(131072), b""):  # 64KB → 128KB
    hash_func.update(chunk)
```

---

## 🐛 Troubleshooting

### Problem: GUI won't open

```bash
# Solution: Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5
```

### Problem: Signatures won't load

```bash
# Solution: Check file permissions
ls -la virus_signatures.json

# Create if missing
echo '[]' > virus_signatures.json
```

### Problem: Scanning is slow

```bash
# Solution 1: Enable parallel mode
# Automatic in GUI (for 10+ files)

# Solution 2: Increase thread count
# Set max_workers=8
```

### Problem: Logs are too large

```bash
# Solution: Increase log level
# PyVirüs.py > logging.basicConfig
level=logging.WARNING  # INFO → WARNING
```

---

## 📚 More Information

- 📖 **Full Documentation**: [README.md](README.md)
- 📝 **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- 🧪 **Test Documentation**: [test_antivirus.py](test_antivirus.py)
- ☁️ **Cloud Module**: [cloud_updater.py](cloud_updater.py)

---

## 💬 Help

Having issues?

1. Check **README.md**
2. Search in **Issues** section
3. Open a new issue

---

## ⭐ Like it?

Don't forget to ⭐ on GitHub!

```bash
# Fork the project
gh repo fork yourusername/pyvirus

# Contribute
git checkout -b feature/amazing
git commit -am "feat: Add amazing feature"
git push origin feature/amazing
```

---

<div align="center">

**Created by Oxynos** ⚡

Happy Secure Coding! 🛡️

[⬆ Back to Top](#-quick-start-guide)

</div>

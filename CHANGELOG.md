# 📝 Changelog

**PyVirus - Oxynos Antivirus Scanner Pro**

Created by Oxynos ⚡

---

## [2.0.0] - 2025-10-20

### 🎉 Major Release - Complete Optimization

This release includes a complete redesign of PyVirus.

### ✨ New Features

#### 🚀 Performance
- **Multi-threading Support**: Parallel file scanning with 4 threads
  - Optimized with `ThreadPoolExecutor`
  - Automatic parallel mode for 10+ files
  - Configurable thread count
  - 3-5x performance boost

- **Cache Mechanism**: Smart memory cache system
  - Global `_virus_signatures_cache` variable
  - File modification check (`mtime` based)
  - 283x faster signature loading
  - Memory optimized

- **Optimized I/O**: File reading optimizations
  - Chunk size: 4KB → 64KB (16x improvement)
  - Buffered reading strategy
  - Exception handling improvements

#### 📊 Logging System
- **Comprehensive Logging**: Python `logging` module integration
  - File logger: `antivirus.log`
  - Console logger: Real-time output
  - Log levels: DEBUG, INFO, WARNING, ERROR
  - Detailed records for every operation
  - Timestamp and module-based logging

#### 🧪 Test Suite
- **Unit Tests**: Comprehensive test package
  - `test_antivirus.py` - 18 test cases
  - Hash calculation tests
  - Virus signature management tests
  - File scanning tests
  - Quarantine tests
  - Performance tests
  - %94 code coverage

#### ☁️ Cloud Support
- **Cloud Updater**: Automatic signature updates
  - `cloud_updater.py` module
  - HTTP/HTTPS support
  - Automatic update checks
  - Scheduled updates (1 hour interval)
  - Merge strategy (local + cloud)
  - Cache mechanism

### 🔧 Improvements

#### 💻 Code Quality
- **Type Hints**: Type annotations added to all functions
  ```python
  def calculate_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
  ```
- **Docstrings**: Detailed documentation
- **PEP 8 Compliance**: Python style guide compliance
- **Import Organization**: Modular import structure

#### 🎨 UI/UX
- **ModernButton**: Optimized button class
  - Color map system
  - Dynamic color darkening
  - Private methods (`_get_style`, `_darken_color`)
- **StatusCard**: Statistics cards
- **AnimatedProgressBar**: Advanced progress bar

#### 🛡️ Security
- **Error Handling**: Robust error catching
  - Try-except blocks
  - Specific exception handling
  - Graceful degradation
- **Permission Management**: File access control
- **Quarantine Logic**: Improved quarantine system
  - File conflict check
  - Unique name generation
  - `exist_ok=True` optimization

### 🐛 Bug Fixes

- ✅ **Quarantine Conflict**: Unique names for duplicate files
- ✅ **Progress Bar**: Accurate percentage calculation
- ✅ **UI Freeze**: Eliminated with thread usage
- ✅ **Cache Invalidation**: Auto-refresh on file change
- ✅ **Memory Leaks**: Fixed with set copying

### 📚 Documentation

- ✅ **README.md**: Comprehensive documentation
  - 750+ lines of detailed explanation
  - Emoji headers
  - Code snippets
  - Benchmark results
  - API documentation
  - Architecture diagrams
  
- ✅ **CHANGELOG.md**: This file
- ✅ **requirements.txt**: Dependency management
- ✅ **.gitignore**: Git ignore rules

### 🔄 Changes

#### Breaking Changes
- `calculate_sha256()` → `calculate_hash()` (with algorithm parameter)
- `VIRUS_DB_FILE`: `.txt` support removed, JSON only
- `ScanThread`: New parameters added (`parallel`, `max_workers`)

#### Deprecated
- Old import structure (wildcard imports removed)

### 📊 Performance Metrics

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| 1000 file scan | 24.7s | 7.1s | **3.5x** |
| Load signatures (10K) | 85ms | 0.3ms | **283x** |
| Memory usage | 150MB | 95MB | **37% reduction** |
| UI responsiveness | Freezes | Smooth | **∞x** |

---

## [1.0.0] - 2024-XX-XX

### 🎉 Initial Release

- ✅ Basic file scanning
- ✅ PyQt5 GUI
- ✅ MD5 hash checking
- ✅ Quarantine system
- ✅ JSON/CSV report generation
- ✅ Signature management

---

<div align="center">

**Created by Oxynos** ⚡

[⬆ Back to Top](#-changelog)

</div>

# 🤝 Contributing to PyVirus

**Created by Mert Ulupınar** ⚡

Thank you for your interest in contributing to PyVirus! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [How to Contribute](#-how-to-contribute)
- [Coding Standards](#-coding-standards)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Testing](#-testing)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- ✅ Be respectful and inclusive
- ✅ Provide constructive feedback
- ✅ Focus on what's best for the project
- ✅ Show empathy towards others

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Git
- PyQt5
- Basic understanding of Python and GUI development

### Quick Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/pyvirus.git
cd pyvirus

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_antivirus.py
```

---

## 🛠️ Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # Optional: for testing
```

### 3. Run Application

```bash
python PyVirüs.py
```

---

## 💡 How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in Issues
2. If not, create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - System information

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear feature description
   - Use case/motivation
   - Proposed implementation (optional)

### Code Contributions

1. **Fork** the repository
2. **Create** a new branch
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages
6. **Push** to your fork
7. **Create** a Pull Request

---

## 📝 Coding Standards

### Python Style Guide

- Follow **PEP 8**
- Use **type hints** for all functions
- Write **docstrings** for classes and functions
- Keep functions **small and focused**

### Example

```python
def calculate_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Calculate file hash using specified algorithm.
    
    Args:
        path: File path to hash
        algorithm: Hash algorithm ('md5' or 'sha256')
    
    Returns:
        Hash string or None if error occurs
    """
    # Implementation
```

### Code Organization

```python
# 1. Standard library imports
import os
import sys

# 2. Third-party imports
from PyQt5.QtWidgets import QWidget

# 3. Local imports
from my_module import my_function
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ScanThread`)
- **Functions**: `snake_case` (e.g., `scan_file`)
- **Constants**: `UPPER_CASE` (e.g., `VIRUS_DB_FILE`)
- **Private methods**: `_leading_underscore` (e.g., `_get_files`)

---

## 📤 Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good commits
feat: Add parallel scanning support
fix: Resolve quarantine file conflict
docs: Update API documentation
perf: Optimize hash calculation with 64KB chunks

# Bad commits
update
fixed bug
changes
```

### Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep first line under 72 characters
- Reference issues: `fix: Resolve #123`

---

## 🔄 Pull Request Process

### Before Submitting

1. ✅ Update your fork
2. ✅ Run all tests
3. ✅ Update documentation
4. ✅ Add tests for new features
5. ✅ Check code style

### PR Checklist

- [ ] Code follows project style guide
- [ ] All tests pass
- [ ] New tests added (if applicable)
- [ ] Documentation updated
- [ ] Commits follow guidelines
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed
```

### Review Process

1. Maintainer reviews your PR
2. Feedback provided (if needed)
3. Make requested changes
4. PR approved and merged

---

## 🧪 Testing

### Running Tests

```bash
# All tests
python test_antivirus.py

# Specific test class
python -m unittest test_antivirus.TestHashCalculation

# With coverage (requires pytest-cov)
pytest --cov=PyVirüs test_antivirus.py
```

### Writing Tests

```python
import unittest

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        pass
    
    def test_feature_works(self):
        """Test that feature works correctly"""
        result = my_function()
        self.assertEqual(result, expected)
    
    def tearDown(self):
        """Cleanup after each test"""
        pass
```

### Test Guidelines

- Write tests for all new features
- Test edge cases
- Test error handling
- Keep tests independent
- Use descriptive test names

---

## 🏗️ Project Structure

```
PyVirus/
├── PyVirüs.py              # Main application
├── cloud_updater.py         # Cloud updates
├── test_antivirus.py        # Tests
├── virus_signatures.json    # Signatures
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT License
└── .gitignore              # Git ignore
```

---

## 💬 Communication

### Where to Ask Questions

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions
- **Pull Requests**: Code review discussions

### Response Times

We aim to respond to:
- Critical bugs: Within 24 hours
- Other issues: Within 1 week
- Pull requests: Within 1 week

---

## 🎯 Areas for Contribution

### Good First Issues

- Documentation improvements
- Adding tests
- Fixing typos
- Small bug fixes

### Advanced Contributions

- Performance optimizations
- New features
- Architecture improvements
- Security enhancements

---

## 📚 Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)

---

## 🙏 Thank You

Thank you for contributing to PyVirus! Your efforts help make this project better for everyone.

---

<div align="center">

**Created by Mert Ulupınar** ⚡

Questions? Open an issue or discussion!

[⬆ Back to Top](#-contributing-to-pyvirus)

</div>


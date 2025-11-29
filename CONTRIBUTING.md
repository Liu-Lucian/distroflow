# Contributing to DistroFlow

Thank you for your interest in contributing!

---

## How to Contribute

### Report Bugs
[Open an issue](https://github.com/yourusername/distroflow/issues) with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

### Suggest Features
[Start a discussion](https://github.com/yourusername/distroflow/discussions) about:
- What problem it solves
- How it would work
- Why it's valuable

### Add a Platform

**Most valuable contribution!**

1. **Choose a platform** not yet supported
2. **Research** authentication and posting workflow
3. **Create** `distroflow/platforms/yourplatform.py`
4. **Test** thoroughly with real account
5. **Document** in `docs/PLATFORMS.md`
6. **Submit PR**

---

## Development Setup

```bash
# Clone repo
git clone https://github.com/yourusername/distroflow.git
cd distroflow

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install in dev mode
pip install -e .

# Run tests
pytest tests/
```

---

## Code Style

- **Formatter**: Black
- **Linter**: Flake8
- **Line length**: 100 characters
- **Type hints**: Encouraged
- **Docstrings**: Required for public APIs

---

## Pull Request Process

1. Fork the repository
2. Create branch: `feature/your-feature`
3. Make changes
4. Test your changes
5. Submit PR with clear description

---

Thank you for contributing! 🎉

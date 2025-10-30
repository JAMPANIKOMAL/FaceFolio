<!-- FaceFolio README - Professional Photo Sorter for Windows -->

# 📸 FaceFolio - Professional Photo Sorter for Windows

Automatically sort and organize your event photos by the people in them using advanced facial recognition.

[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-blue?logo=windows&logoColor=white)](https://github.com/JAMPANIKOMAL/FaceFolio/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Release](https://img.shields.io/github/v/release/JAMPANIKOMAL/FaceFolio?logo=github)](https://github.com/JAMPANIKOMAL/FaceFolio/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/JAMPANIKOMAL/FaceFolio/total?logo=github&color=brightgreen)](https://github.com/JAMPANIKOMAL/FaceFolio/releases)

A professional Windows utility for **intelligent photo management**. Perfect for photographers, event organizers, and anyone looking to efficiently manage large photo collections. Features two powerful sorting workflows and a clean, modern user interface.

---

## 🔥 Key Features
- 🤖 **Intelligent Sorting**: Choose between providing reference photos or letting the app automatically discover new faces.
- ⚡️ **High-Performance Engine**: Quickly and accurately processes large batches of photos.
- 📂 **Automatic Organization**: Creates neatly organized folders for each identified person, saving you hours of manual work.
- 🖼️ **Interactive Tagging**: View upscaled portraits and the original photo to easily identify and name new faces.
- 📦 **Professional Installer**: Simple and clean installer for easy setup on any Windows machine.
- 🔄 **Automated Releases**: CI/CD pipeline ensures reliable and consistent new versions.
- 🤖 **Enhanced with AI assistance** for optimal code quality and performance.

---

## 📥 Download

### Latest Release
[![Download Latest](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge)](https://github.com/JAMPANIKOMAL/FaceFolio/releases/latest)

See the "What's New" section for the latest release on the [Releases Page](https://github.com/JAMPANIKOMAL/FaceFolio/releases).

---

## 🚀 Quick Start

### Option 1: Windows Installer (Recommended)
1. Download `FaceFolio_Setup_vX.Y.Z.exe` from the [Latest Release](https://github.com/JAMPANIKOMAL/FaceFolio/releases/latest).
2. Run the installer.
3. Follow the setup wizard.
4. Launch FaceFolio from the Start Menu or desktop shortcut.

### Option 2: Building from Source
1. Clone this repository.
2. Follow the setup instructions in the **Building from Source** section below.
3. Run the application:
	```bash
	python main.py
	```

---

## 📋 Requirements

- **Windows 10 or later** (x64)
- **Python 3.9+** (if building from source)
- **Microsoft C++ Build Tools & CMake** (if building from source)

---

## 🏗️ Building from Source

### Prerequisites
- All requirements listed above
- InnoSetup (for creating the installer)

### Build Commands
```bash
# 1. Install all required Python packages
pip install -r requirements.txt

# 2. Build the executable using PyInstaller
# (Run the command from the "Corrected PyInstaller Command" step)
pyinstaller --name FaceFolio ... main.py

# 3. Build the installer (requires InnoSetup)
# Open setup.iss with the InnoSetup Compiler and click "Compile"
```

---

## 🗑️ Uninstallation

If you used the installer, you can uninstall FaceFolio like any other Windows application:
1. Go to **Settings → Apps → Installed apps**.
2. Find FaceFolio in the list and select **Uninstall**.
3. Alternatively, use the "Uninstall FaceFolio" shortcut in the Start Menu.

The uninstaller will completely remove all application files, shortcuts, and registry entries.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
📋 RequirementsWindows 10 or later (x64)Python 3.9+ (if building from source)Microsoft C++ Build Tools & CMake (if building from source)🏗️ Building from SourcePrerequisitesAll requirements listed above.InnoSetup (for creating the installer).Build Commands# 1. Install all required Python packages
pip install -r requirements.txt

# 2. Build the executable using PyInstaller
# (Run the command from the "Corrected PyInstaller Command" step)
pyinstaller --name FaceFolio ... main.py

# 3. Build the installer (requires InnoSetup)
# Open setup.iss with the InnoSetup Compiler and click "Compile"
🗑️ UninstallationIf you used the installer, you can uninstall FaceFolio like any other Windows application:Go to Settings → Apps → Installed apps.Find FaceFolio in the list and select "Uninstall".Alternatively, use the "Uninstall FaceFolio" shortcut in the Start Menu.The uninstaller will completely remove all application files, shortcuts, and registry entries.📄 LicenseThis project is licensed under the MIT License - see the LICENSE file for details.
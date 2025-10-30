# FaceFolio 📸

FaceFolio is a cross-platform desktop app that automatically sorts and organizes event photos by the people in them. Using advanced facial recognition, it groups pictures efficiently, saving you hours of manual work.

> **Note:** We leveraged AI tools and assistance throughout the development of this project to enhance productivity and accuracy.

## ✨ Features

FaceFolio supports two main workflows:

### 1. Reference-Based Sorting

- Provide a `.zip` file of your event photos.
- Provide a second `.zip` file of reference photos, each named after the person (e.g., `Alice.jpg`, `Bob.png`).
- FaceFolio creates folders for each person and copies all event photos containing them into their respective folders.

### 2. Automatic Discovery & Tagging

- Provide only the `.zip` file of your event photos.
- FaceFolio analyzes the photos, identifies unique individuals, and generates a portrait for each.
- The app displays these portraits for you to input names.
- Once tagged, photos are sorted accordingly.

## 💻 How to Use (Development)

These steps are for running the core logic script for testing.

### 1. Prerequisites

- Python 3.9+
- Microsoft C++ Build Tools (with "Desktop development with C++" workload)
- CMake (added to system PATH)

### 2. Setup

Clone the repository and set up a Python virtual environment:

```sh
# Navigate to your project directory
cd path/to/FaceFolio

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# Install required libraries from requirements.txt
pip install -r requirements.txt
```

### 3. Running the Core Logic

The `src/core.py` script contains the main processing logic. You can run the GUI application with:

```sh
python src/main.py
```

## 🛠️ Technology Stack

- **Core Language:** Python
- **Facial Recognition:** face_recognition (built on dlib)
- **Image Processing:** Pillow
- **GUI Framework:** PyQt6
- **Packaging:** PyInstaller
- **Installer:** Inno Setup

## 🚀 Project Structure

```
FaceFolio/
├── src/              # Source code
│   ├── main.py      # PyQt6 GUI application
│   └── core.py      # Facial recognition logic
├── docs/             # Documentation
├── assets/           # Icons and resources
├── build/            # Build configuration
└── requirements.txt  # Python dependencies
```

Run the application with `python src/main.py` after installing dependencies.

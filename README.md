# FaceFolio 📸

FaceFolio is a cross-platform desktop app that automatically sorts and organizes event photos by the people in them. Using advanced facial recognition, it groups pictures efficiently, saving you hours of manual work.

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

# Install required libraries
pip install cmake dlib face_recognition opencv-python Pillow
```

### 3. Running the Core Logic

The `core.py` script contains the main processing logic. Test the workflows by following the instructions in the `if __name__ == "__main__":` block.

#### To Test Workflow 1 (Reference-Based):

1. Create `temp_files/reference_photos` and add named reference images (e.g., `Alice.jpg`).
2. Create `temp_files/event_photos` and add your event photos.
3. Uncomment the "TESTING WORKFLOW 1" block in `core.py` and run the script.

#### To Test Workflow 2 (Discovery):

1. Create `temp_files/event_photos` and add your event photos.
2. Uncomment the "TESTING WORKFLOW 2" block in `core.py` and run the script.

## 🛠️ Technology Stack

- **Core Language:** Python
- **Facial Recognition:** face_recognition (built on dlib)
- **Image Processing:** Pillow, opencv-python
- **GUI Framework (Upcoming):** PyQt6
- **Packaging (Upcoming):** PyInstaller
- **Installer (Upcoming):** Inno Setup

## 🚀 Next Steps

The next phase is building the graphical user interface (GUI) to connect with the core logic, providing a seamless and user-friendly experience.

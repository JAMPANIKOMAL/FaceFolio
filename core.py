import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

# --- Main Application Window ---
class FaceFolioApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window Properties ---
        self.setWindowTitle("FaceFolio - Photo Sorter")
        self.setGeometry(100, 100, 900, 700) # x, y, width, height
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QLabel {
                color: #e6edf3;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: 1px solid #30363d;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QFrame {
                border: 1px solid #30363d;
                border-radius: 6px;
            }
        """)

        # --- Main Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(25)

        # --- UI Elements ---
        self.setup_ui()

    def setup_ui(self):
        """
        Creates and arranges the user interface widgets.
        """
        # --- Title ---
        title_label = QLabel("FaceFolio")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Subtitle ---
        subtitle_label = QLabel("Your Automatic Photo Sorter")
        subtitle_label.setStyleSheet("font-size: 16px; color: #7d8590; margin-bottom: 20px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Workflow 1: With Reference Photos ---
        workflow1_frame = self.create_workflow_frame(
            "Workflow 1: Sort Using Reference Photos",
            "Provide a zip of event photos and a zip of named reference photos.",
            "Select Event Photos (.zip)",
            "Select Reference Photos (.zip)"
        )

        # --- Workflow 2: Discover and Tag ---
        workflow2_frame = self.create_workflow_frame(
            "Workflow 2: Discover Faces Automatically",
            "Provide a zip of event photos. The app will find unique people for you to tag.",
            "Select Event Photos (.zip)",
            None  # No second button for this workflow
        )

        # --- Add widgets to the layout ---
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(subtitle_label)
        self.main_layout.addWidget(workflow1_frame)
        self.main_layout.addWidget(workflow2_frame)
        self.main_layout.addStretch() # Pushes everything to the top

    def create_workflow_frame(self, title, description, button1_text, button2_text):
        """Helper function to create a consistent frame for each workflow."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #58a6ff;")

        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 14px; color: #7d8590;")
        desc_label.setWordWrap(True)

        button1 = QPushButton(button1_text)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(button1)

        if button2_text:
            button2 = QPushButton(button2_text)
            layout.addWidget(button2)
        
        return frame


# --- Application Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceFolioApp()
    window.show()
    sys.exit(app.exec())

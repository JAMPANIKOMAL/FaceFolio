import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QFileDialog
from PyQt6.QtCore import Qt

# --- Main Application Window ---
class FaceFolioApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- File Path Storage ---
        self.w1_event_zip_path = None
        self.w1_ref_zip_path = None
        self.w2_event_zip_path = None

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
            QPushButton:disabled {
                background-color: #21262d;
                color: #7d8590;
                border-color: #30363d;
            }
            QFrame {
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            /* Style for the file path labels */
            .PathLabel {
                color: #7d8590;
                font-size: 12px;
                padding: 5px;
                border: 1px solid #30363d;
                border-radius: 4px;
                background-color: #161b22;
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
        self.setup_workflow1_ui()

        # --- Workflow 2: Discover and Tag ---
        self.setup_workflow2_ui()

        # --- Add widgets to the layout ---
        self.main_layout.addStretch() # Pushes everything to the top

    def setup_workflow1_ui(self):
        """Sets up the UI components for Workflow 1."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        title_label = QLabel("Workflow 1: Sort Using Reference Photos")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #58a6ff;")
        desc_label = QLabel("Provide a zip of event photos and a zip of named reference photos.")
        desc_label.setStyleSheet("font-size: 14px; color: #7d8590;")
        desc_label.setWordWrap(True)

        # Event Photos Row
        self.w1_event_path_label = QLabel("No file selected.")
        self.w1_event_path_label.setObjectName("PathLabel")
        btn_select_w1_event = QPushButton("Select Event Photos (.zip)")
        btn_select_w1_event.clicked.connect(self.select_w1_event_zip)
        
        # Reference Photos Row
        self.w1_ref_path_label = QLabel("No file selected.")
        self.w1_ref_path_label.setObjectName("PathLabel")
        btn_select_w1_ref = QPushButton("Select Reference Photos (.zip)")
        btn_select_w1_ref.clicked.connect(self.select_w1_ref_zip)

        # Start Button
        self.w1_start_button = QPushButton("Start Sorting")
        self.w1_start_button.setEnabled(False)
        # self.w1_start_button.clicked.connect(self.start_workflow1) # We will connect this later

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.create_file_selector_row(btn_select_w1_event, self.w1_event_path_label))
        layout.addWidget(self.create_file_selector_row(btn_select_w1_ref, self.w1_ref_path_label))
        layout.addWidget(self.w1_start_button)
        
        self.main_layout.addWidget(frame)

    def setup_workflow2_ui(self):
        """Sets up the UI components for Workflow 2."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        title_label = QLabel("Workflow 2: Discover Faces Automatically")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #58a6ff;")
        desc_label = QLabel("Provide a zip of event photos. The app will find unique people for you to tag.")
        desc_label.setStyleSheet("font-size: 14px; color: #7d8590;")
        desc_label.setWordWrap(True)

        # Event Photos Row
        self.w2_event_path_label = QLabel("No file selected.")
        self.w2_event_path_label.setObjectName("PathLabel")
        btn_select_w2_event = QPushButton("Select Event Photos (.zip)")
        btn_select_w2_event.clicked.connect(self.select_w2_event_zip)

        # Start Button
        self.w2_start_button = QPushButton("Start Discovery")
        self.w2_start_button.setEnabled(False)
        # self.w2_start_button.clicked.connect(self.start_workflow2) # We will connect this later

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.create_file_selector_row(btn_select_w2_event, self.w2_event_path_label))
        layout.addWidget(self.w2_start_button)
        
        self.main_layout.addWidget(frame)

    def create_file_selector_row(self, button, label):
        """Helper to create a horizontal layout for a button and a label."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0,0,0,0)
        row_layout.addWidget(button)
        row_layout.addWidget(label, 1) # The '1' makes the label stretch
        return row_widget

    def select_w1_event_zip(self):
        self.w1_event_zip_path = self.open_zip_file_dialog()
        self.update_path_label(self.w1_event_path_label, self.w1_event_zip_path)
        self.check_workflow1_ready()

    def select_w1_ref_zip(self):
        self.w1_ref_zip_path = self.open_zip_file_dialog()
        self.update_path_label(self.w1_ref_path_label, self.w1_ref_zip_path)
        self.check_workflow1_ready()

    def select_w2_event_zip(self):
        self.w2_event_zip_path = self.open_zip_file_dialog()
        self.update_path_label(self.w2_event_path_label, self.w2_event_zip_path)
        self.check_workflow2_ready()

    def open_zip_file_dialog(self):
        """Opens a file dialog to select a zip file and returns the path."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Zip File", "", "Zip Files (*.zip)")
        return file_path if file_path else None

    def update_path_label(self, label, path):
        """Updates a label to show the selected file path or a default message."""
        if path:
            # Show only the filename, not the full path
            label.setText(Path(path).name)
        else:
            label.setText("No file selected.")

    def check_workflow1_ready(self):
        """Enables the start button for workflow 1 if both files are selected."""
        if self.w1_event_zip_path and self.w1_ref_zip_path:
            self.w1_start_button.setEnabled(True)
        else:
            self.w1_start_button.setEnabled(False)

    def check_workflow2_ready(self):
        """Enables the start button for workflow 2 if the event file is selected."""
        if self.w2_event_zip_path:
            self.w2_start_button.setEnabled(True)
        else:
            self.w2_start_button.setEnabled(False)


# --- Application Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceFolioApp()
    window.show()
    sys.exit(app.exec())

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QFileDialog, QStackedWidget, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# --- Import the core logic ---
import core

# --- Worker Thread for Long-Running Tasks ---
class Worker(QThread):
    """
    Runs a long-running task in a separate thread to avoid freezing the UI.
    """
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Execute the task."""
        self.function(*self.args, **self.kwargs)
        self.finished.emit()


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
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow, QWidget {
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
                padding: 15px;
            }
            QProgressBar {
                border: 1px solid #30363d;
                border-radius: 6px;
                text-align: center;
                color: #e6edf3;
            }
            QProgressBar::chunk {
                background-color: #238636;
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
        
        self.stacked_widget = QStackedWidget()
        main_container_layout = QVBoxLayout(central_widget)
        main_container_layout.addWidget(self.stacked_widget)

        self.main_screen = QWidget()
        self.main_layout = QVBoxLayout(self.main_screen)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(25)

        self.processing_screen = self.create_processing_screen()

        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.processing_screen)

        self.setup_ui()

    def create_processing_screen(self):
        """Creates the screen shown during and after processing."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        self.status_label = QLabel("Processing... Please wait.")
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e6edf3;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)

        # Container for buttons that appear after processing
        self.finish_buttons_widget = QWidget()
        finish_layout = QHBoxLayout(self.finish_buttons_widget)
        
        self.btn_download = QPushButton("Open Download Location")
        self.btn_download.clicked.connect(self.open_download_location)
        
        self.btn_back = QPushButton("Back to Main Menu")
        self.btn_back.clicked.connect(self.reset_to_main_screen)

        finish_layout.addWidget(self.btn_download)
        finish_layout.addWidget(self.btn_back)
        self.finish_buttons_widget.hide() # Hide until processing is done

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.finish_buttons_widget)
        return widget

    def setup_ui(self):
        """Creates and arranges the user interface widgets for the main screen."""
        title_label = QLabel("FaceFolio")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Your Automatic Photo Sorter")
        subtitle_label.setStyleSheet("font-size: 16px; color: #7d8590; margin-bottom: 20px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(subtitle_label)

        self.setup_workflow1_ui()
        self.setup_workflow2_ui()

        self.main_layout.addStretch()

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

        self.w1_event_path_label = QLabel("No file selected.")
        self.w1_event_path_label.setProperty("class", "PathLabel")
        btn_select_w1_event = QPushButton("Select Event Photos (.zip)")
        btn_select_w1_event.clicked.connect(self.select_w1_event_zip)
        
        self.w1_ref_path_label = QLabel("No file selected.")
        self.w1_ref_path_label.setProperty("class", "PathLabel")
        btn_select_w1_ref = QPushButton("Select Reference Photos (.zip)")
        btn_select_w1_ref.clicked.connect(self.select_w1_ref_zip)

        self.w1_start_button = QPushButton("Start Sorting")
        self.w1_start_button.setEnabled(False)
        self.w1_start_button.clicked.connect(self.start_workflow1)

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

        self.w2_event_path_label = QLabel("No file selected.")
        self.w2_event_path_label.setProperty("class", "PathLabel")
        btn_select_w2_event = QPushButton("Select Event Photos (.zip)")
        btn_select_w2_event.clicked.connect(self.select_w2_event_zip)

        self.w2_start_button = QPushButton("Start Discovery")
        self.w2_start_button.setEnabled(False)
        # self.w2_start_button.clicked.connect(self.start_workflow2)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.create_file_selector_row(btn_select_w2_event, self.w2_event_path_label))
        layout.addWidget(self.w2_start_button)
        
        self.main_layout.addWidget(frame)

    def create_file_selector_row(self, button, label):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0,0,0,0)
        row_layout.addWidget(button)
        row_layout.addWidget(label, 1)
        return row_widget

    def start_workflow1(self):
        self.switch_screen(1)
        self.status_label.setText("Starting Workflow 1...")
        self.worker = Worker(self.run_w1_logic)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()

    def run_w1_logic(self):
        print("--- RUNNING WORKFLOW 1 ---")
        core.setup_directories()
        core.extract_zip(self.w1_event_zip_path, core.EXTRACTED_EVENTS_DIR)
        core.extract_zip(self.w1_ref_zip_path, core.EXTRACTED_REFERENCES_DIR)
        known_encodings, known_names = core.load_reference_encodings(core.EXTRACTED_REFERENCES_DIR)
        if known_encodings:
            core.find_and_sort_faces_by_reference(core.EXTRACTED_EVENTS_DIR, known_encodings, known_names)
            core.copy_reference_photos(core.EXTRACTED_REFERENCES_DIR)
            core.create_download_zip(core.OUTPUT_DIR, core.DOWNLOAD_ZIP_PATH)
        else:
            print("Processing stopped: No reference faces were loaded.")

    def on_processing_finished(self):
        print("--- WORKFLOW FINISHED ---")
        self.status_label.setText("Processing Complete!")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.finish_buttons_widget.show()

    def open_download_location(self):
        """Opens the folder containing the final zip file."""
        try:
            # Use os.startfile for Windows, works like double-clicking the folder
            os.startfile(Path.cwd())
        except Exception as e:
            print(f"Could not open file explorer: {e}")

    def reset_to_main_screen(self):
        """Resets the UI to the initial state."""
        self.switch_screen(0)
        self.w1_event_zip_path = None
        self.w1_ref_zip_path = None
        self.w2_event_zip_path = None
        self.update_path_label(self.w1_event_path_label, None)
        self.update_path_label(self.w1_ref_path_label, None)
        self.update_path_label(self.w2_event_path_label, None)
        self.check_workflow1_ready()
        self.check_workflow2_ready()
        
        # Reset processing screen
        self.status_label.setText("Processing... Please wait.")
        self.progress_bar.setRange(0, 0)
        self.finish_buttons_widget.hide()

    def switch_screen(self, index):
        self.stacked_widget.setCurrentIndex(index)

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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Zip File", "", "Zip Files (*.zip)")
        return file_path if file_path else None

    def update_path_label(self, label, path):
        if path:
            label.setText(Path(path).name)
            label.setToolTip(path) # Show full path on hover
        else:
            label.setText("No file selected.")
            label.setToolTip("")

    def check_workflow1_ready(self):
        if self.w1_event_zip_path and self.w1_ref_zip_path:
            self.w1_start_button.setEnabled(True)
        else:
            self.w1_start_button.setEnabled(False)

    def check_workflow2_ready(self):
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

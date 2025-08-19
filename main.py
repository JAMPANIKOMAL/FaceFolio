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
    # Signals to communicate with the main thread
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
        # Note: We can't directly update the UI from this thread.
        # We must use signals. For now, we'll just run the function.
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
            /* ... (style sheet remains the same) ... */
        """)

        # --- Main Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Use a QStackedWidget to manage different screens (e.g., main, processing)
        self.stacked_widget = QStackedWidget()
        main_container_layout = QVBoxLayout(central_widget)
        main_container_layout.addWidget(self.stacked_widget)

        # Create the main screen
        self.main_screen = QWidget()
        self.main_layout = QVBoxLayout(self.main_screen)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(25)

        # Create the processing screen
        self.processing_screen = self.create_processing_screen()

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.processing_screen)

        # --- UI Elements ---
        self.setup_ui()

    def create_processing_screen(self):
        """Creates the screen shown during processing."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("Processing... Please wait.")
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e6edf3;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate progress bar

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
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
        # ... (rest of the function is the same)
        self.w1_start_button.setEnabled(False)
        self.w1_start_button.clicked.connect(self.start_workflow1) # Connect the button
        # ... (rest of the function is the same)
        self.main_layout.addWidget(frame)

    def setup_workflow2_ui(self):
        """Sets up the UI components for Workflow 2."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        # ... (rest of the function is the same)
        self.w2_start_button.setEnabled(False)
        # self.w2_start_button.clicked.connect(self.start_workflow2) # We will connect this later
        # ... (rest of the function is the same)
        self.main_layout.addWidget(frame)

    # --- Core Logic Integration ---
    def start_workflow1(self):
        """Initiates the photo sorting process for workflow 1."""
        self.switch_screen(1) # Switch to processing screen
        self.status_label.setText("Starting Workflow 1...")
        
        # Run the core logic in a separate thread
        self.worker = Worker(self.run_w1_logic)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()

    def run_w1_logic(self):
        """The actual function that runs in the background thread."""
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
        """Called when the worker thread is done."""
        print("--- WORKFLOW FINISHED ---")
        self.status_label.setText("Processing Complete!")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        # In the next step, we'll add a button to go back or download.

    def switch_screen(self, index):
        """Switches the view to the specified screen index."""
        self.stacked_widget.setCurrentIndex(index)

    # --- File Dialog Functions (remain the same) ---
    def create_file_selector_row(self, button, label):
        # ...
        return QWidget()
    def select_w1_event_zip(self):
        # ...
        pass
    def select_w1_ref_zip(self):
        # ...
        pass
    def select_w2_event_zip(self):
        # ...
        pass
    def open_zip_file_dialog(self):
        # ...
        return ""
    def update_path_label(self, label, path):
        # ...
        pass
    def check_workflow1_ready(self):
        # ...
        pass
    def check_workflow2_ready(self):
        # ...
        pass

# --- Application Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceFolioApp()
    window.show()
    sys.exit(app.exec())

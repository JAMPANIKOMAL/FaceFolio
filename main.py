import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QFileDialog, QStackedWidget, QProgressBar, QScrollArea,
                             QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

# --- Import the core logic ---
import core

# --- Worker Thread for Long-Running Tasks ---
class Worker(QThread):
    """
    Runs a long-running task in a separate thread to avoid freezing the UI.
    Now includes a signal to pass back results.
    """
    finished = pyqtSignal(object) # Can emit any object as a result

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        """Execute the task and store the result."""
        self.result = self.function(*self.args, **self.kwargs)
        self.finished.emit(self.result)

# --- Custom Widget for Face Tagging ---
class FaceTagWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(15)

        # Display the face portrait
        self.image_label = QLabel()
        pixmap = QPixmap(str(image_path))
        self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Text input for the name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter person's name...")
        self.name_input.setStyleSheet("padding: 8px; border-radius: 4px; border: 1px solid #30363d;")

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_input, 1) # Stretch the line edit

    def get_name(self):
        return self.name_input.text().strip()

# --- Main Application Window ---
class FaceFolioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # --- Data Storage for Workflow 2 ---
        self.discovered_encodings = []
        self.all_face_metadata = []
        self.face_tag_widgets = []

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
        self.stacked_widget = QStackedWidget()
        main_container_layout = QVBoxLayout(central_widget)
        main_container_layout.addWidget(self.stacked_widget)

        self.main_screen = QWidget()
        self.main_layout = QVBoxLayout(self.main_screen)
        
        self.processing_screen = self.create_processing_screen()
        self.tagging_screen = self.create_tagging_screen()

        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.processing_screen)
        self.stacked_widget.addWidget(self.tagging_screen)

        self.setup_ui()

    def create_tagging_screen(self):
        """Creates the screen for naming discovered faces."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("Name the Discovered People")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #58a6ff;")
        
        # Scroll area for the face widgets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # Container for the face widgets inside the scroll area
        self.scroll_content_widget = QWidget()
        self.tagging_layout = QVBoxLayout(self.scroll_content_widget)
        self.tagging_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content_widget)

        # Finish button
        btn_finish_tagging = QPushButton("Finish Tagging and Sort Photos")
        btn_finish_tagging.clicked.connect(self.start_final_sorting)
        
        main_layout.addWidget(title)
        main_layout.addWidget(scroll_area, 1) # Make scroll area stretch
        main_layout.addWidget(btn_finish_tagging)
        
        return widget

    def populate_tagging_screen(self):
        """Clears and adds FaceTagWidgets for each discovered portrait."""
        # Clear previous widgets
        for i in reversed(range(self.tagging_layout.count())): 
            self.tagging_layout.itemAt(i).widget().setParent(None)
        self.face_tag_widgets = []

        portrait_paths = sorted(list(core.UNKNOWN_PORTRAITS_DIR.glob("*.png")))
        for i, path in enumerate(portrait_paths):
            tag_widget = FaceTagWidget(path)
            tag_widget.name_input.setText(f"Person_{i+1}") # Default name
            self.tagging_layout.addWidget(tag_widget)
            self.face_tag_widgets.append(tag_widget)

    def start_workflow2(self):
        """Initiates the face discovery process."""
        self.switch_screen(1)
        self.status_label.setText("Discovering unique faces... This may take a while.")
        self.worker = Worker(self.run_w2_discovery)
        self.worker.finished.connect(self.on_discovery_finished)
        self.worker.start()

    def run_w2_discovery(self):
        """The discovery function that runs in the background."""
        print("--- RUNNING WORKFLOW 2 (DISCOVERY) ---")
        core.setup_directories()
        core.extract_zip(self.w2_event_zip_path, core.EXTRACTED_EVENTS_DIR)
        return core.find_unique_faces(core.EXTRACTED_EVENTS_DIR)

    def on_discovery_finished(self, result):
        """Called when face discovery is complete."""
        self.discovered_encodings, self.all_face_metadata = result
        print(f"--- DISCOVERY FINISHED: Found {len(self.discovered_encodings)} unique people ---")

        if not self.discovered_encodings:
            self.status_label.setText("No faces were found in the provided photos.")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.finish_buttons_widget.show()
            self.btn_download.hide() # No download if no faces found
        else:
            self.populate_tagging_screen()
            self.switch_screen(2) # Switch to tagging screen

    def start_final_sorting(self):
        """Gathers names from the UI and starts the final sorting process."""
        self.switch_screen(1)
        self.status_label.setText("Sorting photos based on your tags...")

        # Gather names from the input fields
        user_names = {i: widget.get_name() for i, widget in enumerate(self.face_tag_widgets)}
        
        self.worker = Worker(self.run_w2_final_sort, user_names)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()

    def run_w2_final_sort(self, user_names):
        """The final sorting function that runs in the background."""
        print("--- RUNNING WORKFLOW 2 (FINAL SORT) ---")
        core.sort_photos_by_discovered_faces(self.all_face_metadata, self.discovered_encodings, user_names)
        core.create_download_zip(core.OUTPUT_DIR, core.DOWNLOAD_ZIP_PATH)

    # --- Other methods (setup_ui, workflow1, etc.) remain largely the same ---
    # ... Make sure to connect the w2_start_button in setup_workflow2_ui ...
    def setup_workflow2_ui(self):
        # ... (previous setup code) ...
        self.w2_start_button.setEnabled(False)
        self.w2_start_button.clicked.connect(self.start_workflow2) # Connect the button
        # ... (rest of the setup) ...
        
    # --- The rest of the file is the same as the previous version ---
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

        self.finish_buttons_widget = QWidget()
        finish_layout = QHBoxLayout(self.finish_buttons_widget)
        
        self.btn_download = QPushButton("Open Download Location")
        self.btn_download.clicked.connect(self.open_download_location)
        
        self.btn_back = QPushButton("Back to Main Menu")
        self.btn_back.clicked.connect(self.reset_to_main_screen)

        finish_layout.addWidget(self.btn_download)
        finish_layout.addWidget(self.btn_back)
        self.finish_buttons_widget.hide()

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

    def on_processing_finished(self, result=None):
        print("--- WORKFLOW FINISHED ---")
        self.status_label.setText("Processing Complete!")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.btn_download.show()
        self.finish_buttons_widget.show()

    def open_download_location(self):
        try:
            os.startfile(Path.cwd())
        except Exception as e:
            print(f"Could not open file explorer: {e}")

    def reset_to_main_screen(self):
        self.switch_screen(0)
        self.w1_event_zip_path = None
        self.w1_ref_zip_path = None
        self.w2_event_zip_path = None
        self.update_path_label(self.w1_event_path_label, None)
        self.update_path_label(self.w1_ref_path_label, None)
        self.update_path_label(self.w2_event_path_label, None)
        self.check_workflow1_ready()
        self.check_workflow2_ready()
        
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
            label.setToolTip(path)
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

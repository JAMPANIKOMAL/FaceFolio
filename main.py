import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QFileDialog, QStackedWidget, QProgressBar, QScrollArea,
                             QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

# --- Import the core logic ---
import core

# --- Worker Thread for Long-Running Tasks ---
class Worker(QThread):
    """
    Runs a long-running task in a separate thread to avoid freezing the UI.
    Emits a result object when finished.
    """
    finished = pyqtSignal(object)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        """Execute the task and store the result."""
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            print(f"An error occurred in the worker thread: {e}")
            self.result = None # Indicate failure
        self.finished.emit(self.result)

# --- Custom Widget for Face Tagging ---
class FaceTagWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(15)

        self.image_label = QLabel()
        pixmap = QPixmap(str(image_path))
        self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter person's name...")
        self.name_input.setStyleSheet("padding: 8px; border-radius: 4px; border: 1px solid #30363d;")

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_input, 1)

    def get_name(self):
        return self.name_input.text().strip()

# --- Main Application Window ---
class FaceFolioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.discovered_encodings = []
        self.all_face_metadata = []
        self.face_tag_widgets = []
        self.w1_event_zip_path = None
        self.w1_ref_zip_path = None
        self.w2_event_zip_path = None

        self.setWindowTitle("FaceFolio - Photo Sorter")
        self.setGeometry(100, 100, 900, 700)
        
        if Path("icon.png").exists():
            self.setWindowIcon(QIcon("icon.png"))
            
        self.apply_stylesheet()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_screen = self.create_main_screen()
        self.processing_screen = self.create_processing_screen()
        self.tagging_screen = self.create_tagging_screen()

        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.processing_screen)
        self.stacked_widget.addWidget(self.tagging_screen)

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0d1117;
                font-family: 'Segoe UI';
            }
            QLabel { color: #e6edf3; }
            QPushButton {
                background-color: #238636;
                color: white;
                border: 1px solid #30363d;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2ea043; }
            QPushButton:disabled {
                background-color: #21262d;
                color: #7d8590;
                border-color: #30363d;
            }
            QFrame {
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 20px;
            }
            QProgressBar {
                border: 1px solid #30363d;
                border-radius: 6px;
                text-align: center;
                color: #e6edf3;
                background-color: #161b22;
            }
            QProgressBar::chunk {
                background-color: #238636;
                border-radius: 6px;
            }
            .PathLabel {
                color: #7d8590;
                font-size: 12px;
                padding: 5px;
                border: 1px solid #30363d;
                border-radius: 4px;
                background-color: #161b22;
            }
            QScrollArea { border: none; }
            QLineEdit {
                padding: 8px; 
                border-radius: 4px; 
                border: 1px solid #30363d;
                background-color: #0d1117;
                color: #e6edf3;
            }
            QMessageBox { background-color: #161b22; }
            QMessageBox QLabel { color: #e6edf3; }
            QMessageBox QPushButton { min-width: 80px; }
        """)

    def create_main_screen(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        title_label = QLabel("FaceFolio")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(title_label)
        
        self.setup_workflow1_ui(content_layout)
        self.setup_workflow2_ui(content_layout)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        return main_widget

    def setup_workflow1_ui(self, parent_layout):
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
        btn_select_w1_event.setToolTip("Select the .zip file containing all your event photos.")
        btn_select_w1_event.clicked.connect(self.select_w1_event_zip)
        
        self.w1_ref_path_label = QLabel("No file selected.")
        self.w1_ref_path_label.setProperty("class", "PathLabel")
        btn_select_w1_ref = QPushButton("Select Reference Photos (.zip)")
        btn_select_w1_ref.setToolTip("Select a .zip file of photos, where each filename is the person's name (e.g., 'Alice.jpg').")
        btn_select_w1_ref.clicked.connect(self.select_w1_ref_zip)

        self.w1_start_button = QPushButton("Start Sorting")
        self.w1_start_button.setToolTip("Begin the sorting process for Workflow 1.")
        self.w1_start_button.setEnabled(False)
        self.w1_start_button.clicked.connect(self.start_workflow1)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.create_file_selector_row(btn_select_w1_event, self.w1_event_path_label))
        layout.addWidget(self.create_file_selector_row(btn_select_w1_ref, self.w1_ref_path_label))
        layout.addWidget(self.w1_start_button)
        
        parent_layout.addWidget(frame)

    def setup_workflow2_ui(self, parent_layout):
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
        btn_select_w2_event.setToolTip("Select the .zip file containing all your event photos.")
        btn_select_w2_event.clicked.connect(self.select_w2_event_zip)

        self.w2_start_button = QPushButton("Start Discovery")
        self.w2_start_button.setToolTip("Begin the discovery process for Workflow 2.")
        self.w2_start_button.setEnabled(False)
        self.w2_start_button.clicked.connect(self.start_workflow2)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.create_file_selector_row(btn_select_w2_event, self.w2_event_path_label))
        layout.addWidget(self.w2_start_button)
        
        parent_layout.addWidget(frame)

    def create_file_selector_row(self, button, label):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0,0,0,0)
        row_layout.addWidget(button)
        row_layout.addWidget(label, 1)
        return row_widget

    def create_tagging_screen(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("Name the Discovered People")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #58a6ff;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.scroll_content_widget = QWidget()
        self.tagging_layout = QVBoxLayout(self.scroll_content_widget)
        self.tagging_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content_widget)

        btn_finish_tagging = QPushButton("Finish Tagging and Sort Photos")
        btn_finish_tagging.setToolTip("Sorts all photos into folders using the names you've provided.")
        btn_finish_tagging.clicked.connect(self.start_final_sorting)
        
        main_layout.addWidget(title)
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(btn_finish_tagging)
        
        return widget

    def populate_tagging_screen(self):
        # Clear previous widgets
        for i in reversed(range(self.tagging_layout.count())): 
            self.tagging_layout.itemAt(i).widget().setParent(None)
        self.face_tag_widgets = []

        portrait_paths = sorted(list(core.UNKNOWN_PORTRAITS_DIR.glob("*.png")))
        for i, path in enumerate(portrait_paths):
            person_index = int(path.stem.split('_')[1])
            tag_widget = FaceTagWidget(path)
            tag_widget.name_input.setText(f"Person_{person_index + 1}")
            self.tagging_layout.addWidget(tag_widget)
            self.face_tag_widgets.append((person_index, tag_widget))

    def start_workflow2(self):
        if not self.w2_event_zip_path: return
        self.switch_screen(1)
        self.status_label.setText("Discovering unique faces... This may take a while.")
        self.progress_bar.setRange(0, 0) # Indeterminate progress
        self.finish_buttons_widget.hide()
        self.worker = Worker(self.run_w2_discovery)
        self.worker.finished.connect(self.on_discovery_finished)
        self.worker.start()

    def run_w2_discovery(self):
        core.setup_directories()
        core.extract_zip(self.w2_event_zip_path, core.EXTRACTED_EVENTS_DIR)
        return core.find_unique_faces(core.EXTRACTED_EVENTS_DIR)

    def on_discovery_finished(self, result):
        if result is None:
            self.show_error_message("An error occurred during face discovery.")
            self.reset_to_main_screen()
            return
            
        self.discovered_encodings, self.all_face_metadata = result
        print(f"--- DISCOVERY FINISHED: Found {len(self.discovered_encodings)} unique people ---")

        if not self.discovered_encodings:
            QMessageBox.information(self, "No Faces Found", "Could not find any faces in the provided photos.")
            self.reset_to_main_screen()
        else:
            self.populate_tagging_screen()
            self.switch_screen(2)

    def start_final_sorting(self):
        self.switch_screen(1)
        self.status_label.setText("Sorting photos based on your tags...")
        self.progress_bar.setRange(0, 0)
        self.finish_buttons_widget.hide()

        user_names = {index: widget.get_name() for index, widget in self.face_tag_widgets}
        self.worker = Worker(self.run_w2_final_sort, user_names)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()

    def run_w2_final_sort(self, user_names):
        core.sort_photos_by_discovered_faces(self.all_face_metadata, self.discovered_encodings, user_names)
        core.create_download_zip(core.OUTPUT_DIR, core.DOWNLOAD_ZIP_PATH)
        return True # Indicate success

    def create_processing_screen(self):
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
        self.btn_download.setToolTip("Opens the folder containing the final 'FaceFolio_Sorted.zip' file.")
        self.btn_download.clicked.connect(self.open_download_location)
        
        self.btn_back = QPushButton("Back to Main Menu")
        self.btn_back.setToolTip("Return to the main screen to start a new task.")
        self.btn_back.clicked.connect(self.reset_to_main_screen)

        finish_layout.addWidget(self.btn_download)
        finish_layout.addWidget(self.btn_back)
        self.finish_buttons_widget.hide()

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.finish_buttons_widget)
        return widget

    def start_workflow1(self):
        if not (self.w1_event_zip_path and self.w1_ref_zip_path): return
        self.switch_screen(1)
        self.status_label.setText("Sorting photos... This may take a while.")
        self.progress_bar.setRange(0, 0) # Indeterminate progress
        self.finish_buttons_widget.hide()
        self.worker = Worker(self.run_w1_logic)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()

    def run_w1_logic(self):
        core.setup_directories()
        core.extract_zip(self.w1_event_zip_path, core.EXTRACTED_EVENTS_DIR)
        core.extract_zip(self.w1_ref_zip_path, core.EXTRACTED_REFERENCES_DIR)
        known_encodings, known_names = core.load_reference_encodings(core.EXTRACTED_REFERENCES_DIR)
        
        if known_encodings:
            core.find_and_sort_faces_by_reference(core.EXTRACTED_EVENTS_DIR, known_encodings, known_names)
            core.copy_reference_photos(core.EXTRACTED_REFERENCES_DIR)
            core.create_download_zip(core.OUTPUT_DIR, core.DOWNLOAD_ZIP_PATH)
            return True # Indicate success
        else:
            print("Processing stopped: No reference faces were loaded.")
            return "No reference faces found."

    def on_processing_finished(self, result):
        if result is None:
            self.show_error_message("An unexpected error occurred during processing.")
            self.reset_to_main_screen()
            return
        
        if isinstance(result, str): # Handle specific error messages from worker
            self.show_error_message(result)
            self.reset_to_main_screen()
            return

        print("--- WORKFLOW FINISHED ---")
        self.status_label.setText("Processing Complete!")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.btn_download.show()
        self.finish_buttons_widget.show()
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Success")
        msg_box.setText("Your photos have been successfully sorted!")
        msg_box.setInformativeText(f"You can find the final zip file at:\n{os.path.abspath(core.DOWNLOAD_ZIP_PATH)}")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def open_download_location(self):
        try:
            os.startfile(os.path.abspath(core.DOWNLOAD_ZIP_PATH.parent))
        except Exception as e:
            print(f"Could not open file explorer: {e}")
            self.show_error_message("Could not open the download folder. Please navigate to it manually.")

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
        
    def switch_screen(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def select_w1_event_zip(self):
        path = self.open_zip_file_dialog()
        if path:
            self.w1_event_zip_path = path
            self.update_path_label(self.w1_event_path_label, self.w1_event_zip_path)
            self.check_workflow1_ready()

    def select_w1_ref_zip(self):
        path = self.open_zip_file_dialog()
        if path:
            self.w1_ref_zip_path = path
            self.update_path_label(self.w1_ref_path_label, self.w1_ref_zip_path)
            self.check_workflow1_ready()

    def select_w2_event_zip(self):
        path = self.open_zip_file_dialog()
        if path:
            self.w2_event_zip_path = path
            self.update_path_label(self.w2_event_path_label, self.w2_event_zip_path)
            self.check_workflow2_ready()

    def open_zip_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Zip File", "", "Zip Files (*.zip)")
        return file_path

    def update_path_label(self, label, path):
        if path:
            label.setText(Path(path).name)
            label.setToolTip(path)
        else:
            label.setText("No file selected.")
            label.setToolTip("")

    def check_workflow1_ready(self):
        self.w1_start_button.setEnabled(bool(self.w1_event_zip_path and self.w1_ref_zip_path))

    def check_workflow2_ready(self):
        self.w2_start_button.setEnabled(bool(self.w2_event_zip_path))

# --- Application Entry Point ---
if __name__ == "__main__":
    # Before running, ensure you have the necessary libraries installed:
    # pip install PyQt6 face_recognition Pillow cmake dlib
    app = QApplication(sys.argv)
    window = FaceFolioApp()
    window.show()
    sys.exit(app.exec())

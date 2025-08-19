import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

# --- Main Application Window ---
class FaceFolioApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window Properties ---
        self.setWindowTitle("FaceFolio - Photo Sorter")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height

        # --- Main Widget and Layout ---
        # All other widgets will go inside this central widget.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # The main layout will be a vertical box layout.
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- UI Elements ---
        self.setup_ui()

    def setup_ui(self):
        """
        Creates and arranges the user interface widgets.
        """
        # Add a title label
        title_label = QLabel("Welcome to FaceFolio")
        # You can style it with CSS-like syntax
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add a simple button as a placeholder
        test_button = QPushButton("This is a placeholder button")
        
        # Add widgets to the layout
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(test_button)


# --- Application Entry Point ---
if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Create the main window
    window = FaceFolioApp()
    window.show() # Display the window
    
    # Start the application's event loop
    sys.exit(app.exec())

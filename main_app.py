# main_app.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                              QVBoxLayout, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt
from sentinel2_downloader import SentinelDownloaderGUI
from c2rcc_processor import C2RCCProcessorGUI
from translations import translations

# ----------------------------------------------------------------------------------------------------------------------
# Class: MainApp
# Description: Main window with two tabs for downloading and processing Sentinel-2 data.
class MainApp(QMainWindow):
    # Function: __init__
    # Description: Initialize main window, create tab widget, and apply translations.
    def __init__(self):
        super().__init__()
        self.current_language = "cs"
        self.setWindowTitle(translations[self.current_language]["app_title"])
        self.setGeometry(100, 100, 600, 750)
        
        self.init_ui()
        self.update_translations()
        
    def init_ui(self):
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Language buttons at top right
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        
        self.btn_cz = QPushButton("Čeština")
        self.btn_cz.clicked.connect(lambda: self.set_language("cs"))
        lang_layout.addWidget(self.btn_cz)
        
        self.btn_en = QPushButton("English")
        self.btn_en.clicked.connect(lambda: self.set_language("en"))
        lang_layout.addWidget(self.btn_en)
        
        main_layout.addLayout(lang_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Download tab
        self.download_tab = QWidget()
        self.download_gui = SentinelDownloaderGUI(self.download_tab)
        self.tab_widget.addTab(self.download_tab, translations[self.current_language]["download_tab"])
        
        # Process tab
        self.process_tab = QWidget()
        self.process_gui = C2RCCProcessorGUI(self.process_tab)
        self.tab_widget.addTab(self.process_tab, translations[self.current_language]["process_tab"])
        
    def set_language(self, lang):
        self.current_language = lang
        self.update_translations()
        
    # Function: update_translations
    # Description: Refresh window title and tab labels, delegate translations to child GUIs.
    def update_translations(self):
        # Update main window
        self.setWindowTitle(translations[self.current_language]["app_title"])
        
        # Update tab names
        self.tab_widget.setTabText(0, translations[self.current_language]["download_tab"])
        self.tab_widget.setTabText(1, translations[self.current_language]["process_tab"])
        
        # Update child widgets
        self.download_gui.update_translations(self.current_language)
        self.process_gui.update_translations(self.current_language)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QFrame, QComboBox, QTextEdit, QFileDialog, 
                              QMessageBox, QGroupBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, QObject
import requests
import geopandas as gpd
from shapely.geometry import box
from datetime import datetime
import os
import threading
import re
import webbrowser
from translations import translations

# ----------------------------------------------------------------------------------------------------------------------
# Class: Communicate
# Description: Defines signals to communicate between the download thread and GUI:
#   log_signal (str), message_signal (str, str, str), update_button_signal (bool).
class Communicate(QObject):
    # Define all signals first
    log_signal = Signal(str)
    message_signal = Signal(str, str, str)  # title, message, type
    update_button_signal = Signal(bool)     # enable/disable download button

    # Function: __init__
    # Description: Initialize GUI state, default language, and connect signals.
    def __init__(self):
        super().__init__()
        # Signals are automatically initialized by PySide6

# ----------------------------------------------------------------------------------------------------------------------
# Class: SentinelDownloaderGUI
# Description: GUI for authenticating, searching, listing, and downloading Sentinel-2 products.
class SentinelDownloaderGUI(QWidget):
    # Function: __init__
    # Description: Initialize GUI state, default language, and connect signals.
    def __init__(self, parent):
        super().__init__(parent)
        self.token = None
        self.products_to_download = []
        self.comm = Communicate()  # This must come before any signal connections
        self.current_language = "cs"
        
        # Connect signals
        self.comm.log_signal.connect(self.log)
        self.comm.message_signal.connect(self.show_message)
        self.comm.update_button_signal.connect(self.update_download_button)
        
        self.setup_gui()
        self.param_frame.setEnabled(False)

        
    # Function: setup_gui
    # Description: Build the login frame, parameter inputs, shapefile loader, search and download controls.
    def setup_gui(self):
        layout = QVBoxLayout(self)
        
        
        # Top container
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)

        # Login frame
        login_frame = QGroupBox()
        login_layout = QVBoxLayout(login_frame)

        self.username_label = QLabel(translations[self.current_language]["username"])
        self.username_entry = QLineEdit()
        login_layout.addWidget(self.username_label)
        login_layout.addWidget(self.username_entry)

        self.password_label = QLabel(translations[self.current_language]["password"])
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.password_label)
        login_layout.addWidget(self.password_entry)

        self.login_button = QPushButton(translations[self.current_language]["login"])
        self.login_button.clicked.connect(self.login)
        login_layout.addWidget(self.login_button)

        # Registration frame
        reg_frame = QGroupBox()
        reg_layout = QVBoxLayout(reg_frame)

        self.info_label_main = QLabel(translations[self.current_language]["login_info"])
        self.info_label_main.setWordWrap(True)
        reg_layout.addWidget(self.info_label_main)

        self.info_label = QLabel(translations[self.current_language]["register"])
        font = self.info_label.font()
        font.setBold(True)
        self.info_label.setFont(font)
        reg_layout.addWidget(self.info_label)

        self.url_label = QLabel('<a href="https://dataspace.copernicus.eu/">https://dataspace.copernicus.eu/</a>')
        self.url_label.setOpenExternalLinks(True)
        reg_layout.addWidget(self.url_label)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("C:/Users/rybar/Downloads/LOGOtransparent (1).png")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(100, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setMaximumWidth(150)

        # Přidání do top layoutu
        top_layout.addWidget(login_frame)
        top_layout.addWidget(reg_frame)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()

        
        # Wrapper blok pro login + registraci + logo + parametry + log_text
        left_block = QWidget()
        left_layout = QVBoxLayout(left_block)
        left_block.setMaximumWidth(800)

        left_layout.addWidget(top_container)


        
        # Parameters frame
        self.param_frame = QGroupBox(translations[self.current_language]["parameters"])
        self.param_frame.setMaximumWidth(600)
        param_layout = QVBoxLayout(self.param_frame)
        
        # Shapefile
        shape_layout = QHBoxLayout()
        self.shape_label = QLabel(translations[self.current_language]["shapefile"])
        self.shapefile_path = QLineEdit()
        self.shape_button = QPushButton(translations[self.current_language]["select"])
        self.shape_button.clicked.connect(self.load_shapefile)
        shape_layout.addWidget(self.shape_label)
        shape_layout.addWidget(self.shapefile_path)
        shape_layout.addWidget(self.shape_button)
        param_layout.addLayout(shape_layout)
        
        # Dates
        # Dates - Date from
        date_from_layout = QHBoxLayout()

        self.date_from_label = QLabel(translations[self.current_language]["date_from"])
        self.date_from_entry = QLineEdit()
        self.date_from_entry.setInputMask("0000-00-00")
        self.date_from_entry.setFixedWidth(100)

        # Zabalíme vstupní pole do containeru pro zarovnání vlevo
        entry_wrapper = QWidget()
        entry_wrapper_layout = QHBoxLayout(entry_wrapper)
        entry_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        entry_wrapper_layout.setAlignment(Qt.AlignLeft)
        entry_wrapper_layout.addWidget(self.date_from_entry)

        date_from_layout.addWidget(self.date_from_label)
        date_from_layout.addWidget(entry_wrapper)
        param_layout.addLayout(date_from_layout)

        
        # Dates - Date to
        date_to_layout = QHBoxLayout()

        self.date_to_label = QLabel(translations[self.current_language]["date_to"])
        self.date_to_entry = QLineEdit()
        self.date_to_entry.setInputMask("0000-00-00")
        self.date_to_entry.setFixedWidth(100)

        # Zabalíme vstupní pole do containeru pro zarovnání vlevo
        entry_wrapper_to = QWidget()
        entry_wrapper_to_layout = QHBoxLayout(entry_wrapper_to)
        entry_wrapper_to_layout.setContentsMargins(0, 0, 0, 0)
        entry_wrapper_to_layout.setAlignment(Qt.AlignLeft)
        entry_wrapper_to_layout.addWidget(self.date_to_entry)

        date_to_layout.addWidget(self.date_to_label)
        date_to_layout.addWidget(entry_wrapper_to)
        param_layout.addLayout(date_to_layout)

        
        # Save folder
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel(translations[self.current_language]["save_folder"])
        self.folder_path = QLineEdit()
        self.folder_button = QPushButton(translations[self.current_language]["select"])
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(self.folder_button)
        param_layout.addLayout(folder_layout)
        
       # Cloud cover
        cloud_layout = QHBoxLayout()
        self.cloud_label = QLabel(translations[self.current_language]["cloud_cover"])
        self.cloud_cover_entry = QLineEdit("20")
        self.cloud_cover_entry.setFixedWidth(50)  # max 3 cifry

        # Zarovnání vlevo přes wrapper
        cloud_wrapper = QWidget()
        cloud_wrapper_layout = QHBoxLayout(cloud_wrapper)
        cloud_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        cloud_wrapper_layout.setAlignment(Qt.AlignLeft)
        cloud_wrapper_layout.addWidget(self.cloud_cover_entry)

        cloud_layout.addWidget(self.cloud_label)
        cloud_layout.addWidget(cloud_wrapper)
        param_layout.addLayout(cloud_layout)


        
     # Product type
        product_layout = QHBoxLayout()
        product_layout.setAlignment(Qt.AlignLeft)  # celé zarovnáno vlevo

        self.product_label = QLabel(translations[self.current_language]["product_type"])
        self.product_label.setFixedWidth(150)  # omezíme šířku labelu

        self.product_type_combo = QComboBox()
        self.product_type_combo.addItems(["Level-2A", "Level-1C"])
        self.product_type_combo.setFixedWidth(100)

        product_layout.addWidget(self.product_label)
        product_layout.addWidget(self.product_type_combo)
        param_layout.addLayout(product_layout)



        
        # Buttons
        self.find_button = QPushButton(translations[self.current_language]["search"])
        self.find_button.clicked.connect(self.run_search_thread)
        param_layout.addWidget(self.find_button)
        
        self.download_button = QPushButton(translations[self.current_language]["download"])
        self.download_button.clicked.connect(self.run_download_thread)
        self.download_button.setEnabled(False)
        param_layout.addWidget(self.download_button)
        
        left_layout.addWidget(self.param_frame)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        left_layout.addWidget(self.log_text)
        
        layout.addWidget(left_block)
        self.setLayout(layout)
        
    # Function: update_translations
    # Description: Update all UI labels and button texts based on selected language.
    # Params: lang (language code).
    def update_translations(self, lang):
        self.current_language = lang
        # Update all texts based on current language
        self.username_label.setText(translations[lang]["username"])
        self.password_label.setText(translations[lang]["password"])
        self.login_button.setText(translations[lang]["login"])
        self.info_label_main.setText(translations[lang]["login_info"])
        self.info_label.setText(translations[lang]["register"])
        self.param_frame.setTitle(translations[lang]["parameters"])
        self.shape_label.setText(translations[lang]["shapefile"])
        self.shape_button.setText(translations[lang]["select"])
        self.date_from_label.setText(translations[lang]["date_from"])
        self.date_to_label.setText(translations[lang]["date_to"])
        self.folder_label.setText(translations[lang]["save_folder"])
        self.folder_button.setText(translations[lang]["select"])
        self.cloud_label.setText(translations[lang]["cloud_cover"])
        self.product_label.setText(translations[lang]["product_type"])
        self.find_button.setText(translations[lang]["search"])
        self.download_button.setText(translations[lang]["download"])
        
    # Function: log
    # Description: Append a status message to the log text area.
    # Params: message (str).
    def log(self, message):
        self.log_text.append(message)
        
    # Function: show_message
    # Description: Display a popup dialog of given type ('info' or 'error').
    def show_message(self, title, message, msg_type):
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
            
    # Function: update_download_button
    # Description: Enable or disable the search/download button.
    def update_download_button(self, enabled):
        self.download_button.setEnabled(enabled)

    # Function: log
    # Description: Append a status message to the log text area.
    # Params: message (str).
    # Function: login
    # Description: Authenticate against Keycloak and enable parameter inputs on success.
    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        try:
            token = self.get_keycloak_token(username, password)
            self.token = token
            self.param_frame.setEnabled(True)

            self.comm.message_signal.emit(
                translations[self.current_language]["login_success"],
                translations[self.current_language]["login_success"],
                "info"
            )
            self.comm.update_button_signal.emit(False)
            self.products_to_download = []
        except Exception as e:
            self.comm.message_signal.emit(
                translations[self.current_language]["login_error"],
                str(e),
                "error"
            )
            
    # Function: get_keycloak_token
    # Description: Request an access token from Keycloak using provided credentials.
    def get_keycloak_token(self, username, password):
        data = {
            "client_id": "cdse-public",
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
        return r.json()["access_token"]

    # Function: load_shapefile
    # Description: Open shapefile dialog and load its WKT geometry for API queries.
    def load_shapefile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Shapefile", "", "Shapefiles (*.shp)")
        if file_path:
            self.shapefile_path.setText(file_path)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.folder_path.setText(folder)

    # Function: get_wkt_from_shapefile
    # Description: Convert shapefile geometry to WKT via geopandas.
    def get_wkt_from_shapefile(self, filepath):
        gdf = gpd.read_file(filepath)
        self.comm.log_signal.emit(f"Načten shapefile: {filepath}, CRS: {gdf.crs}")
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
            self.comm.log_signal.emit("Transformace na EPSG:4326 proběhla.")
        bounds = gdf.total_bounds
        self.comm.log_signal.emit(f"Vypočtený bounding box: {bounds}")
        return box(*bounds).wkt

    # Function: validate_inputs
    # Description: Ensure mandatory inputs (dates, cloud cover, AOI) are provided.
    def validate_inputs(self):
        errors = []
        lang = self.current_language

        # Validate dates
        for label, entry in [("date_from", self.date_from_entry), ("date_to", self.date_to_entry)]:
            date_str = entry.text()
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
                    raise ValueError("Invalid date format")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj > datetime.now():
                    errors.append(f"Datum v poli {label} nesmí být v budoucnosti.")
            except ValueError:
                errors.append(f"Neplatný formát datumu v poli {label}. Očekává se YYYY-MM-DD.")

        # Validate date range
        if not errors:
            try:
                date_from = datetime.strptime(self.date_from_entry.text(), "%Y-%m-%d")
                date_to = datetime.strptime(self.date_to_entry.text(), "%Y-%m-%d")
                if date_from > date_to:
                    errors.append("Datum 'Od' nemůže být pozdější než datum 'Do'.")
            except ValueError:
                pass  # Already handled above

        # Validate cloud cover
        cloud_cover = self.cloud_cover_entry.text()
        try:
            value = float(cloud_cover.replace(',', '.'))
            if value < 0 or value > 100:
                errors.append("Hodnota oblačnosti musí být mezi 0 a 100.")
        except ValueError:
            errors.append("Hodnota oblačnosti není platné číslo.")

        # Validate shapefile
        if not self.shapefile_path.text() or not os.path.exists(self.shapefile_path.text()):
            errors.append("Neplatný shapefile.")

        # Validate save folder
        if not self.folder_path.text() or not os.path.isdir(self.folder_path.text()):
            errors.append("Neplatná výstupní složka.")

        if errors:
            self.comm.message_signal.emit(
                translations[lang]["error"],
                "\n".join(errors),
                "error"
            )
            return False
        return True

    def run_search_thread(self):
        if not self.validate_inputs():
            return

        self.comm.update_button_signal.emit(False)
        self.products_to_download = []
        threading.Thread(target=self.search_data).start()

    # Function: search_data
    # Description: Query Copernicus API for Sentinel-2 products matching parameters.
    def search_data(self):
        try:
            wkt = self.get_wkt_from_shapefile(self.shapefile_path.text())
            date_from = self.date_from_entry.text()
            date_to = self.date_to_entry.text()
            cloud_cover = self.cloud_cover_entry.text()
            product_type = self.product_type_combo.currentText()

            product_type_code = {
                "Level-2A": "S2MSI2A",
                "Level-1C": "S2MSI1C"
            }.get(product_type, "S2MSI2A")

            url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?" \
                f"$filter=Collection/Name eq 'SENTINEL-2'" \
                f" and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{product_type_code}')" \
                f" and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {cloud_cover})" \
                f" and OData.CSC.Intersects(area=geography'SRID=4326;{wkt}')" \
                f" and ContentDate/Start gt {date_from}T00:00:00.000Z" \
                f" and ContentDate/Start lt {date_to}T00:00:00.000Z" \
                f"&$count=True&$top=100"

            self.comm.log_signal.emit("Odesílám dotaz na API...")
            session = requests.Session()
            session.headers.update({"Authorization": f"Bearer {self.token}"})

            response = session.get(url)
            self.comm.log_signal.emit(f"HTTP status: {response.status_code}")
            json_ = response.json()

            self.products_to_download = json_.get("value", [])
            if not self.products_to_download:
                self.comm.log_signal.emit("Žádné produkty nenalezeny.")
                self.comm.message_signal.emit(
                    translations[self.current_language]["info"],
                    translations[self.current_language]["no_products"],
                    "info"
                )
                return

            self.comm.log_signal.emit(f"Počet nalezených produktů: {len(self.products_to_download)}")
            self.comm.update_button_signal.emit(True)

        except Exception as ex:
            self.comm.log_signal.emit(f"Chyba při vyhledávání: {ex}")
            self.comm.update_button_signal.emit(False)

    def run_download_thread(self):
        if not self.products_to_download:
            self.comm.message_signal.emit(
                translations[self.current_language]["error"],
                "Nejsou k dispozici žádné produkty ke stažení. Nejprve proveďte vyhledání.",
                "error"
            )
            return
        
        threading.Thread(target=self.download_data).start()

    # Function: download_data
    # Description: Download selected products via streaming to output folder.
    def download_data(self):
        try:
            folder = self.folder_path.text()
            session = requests.Session()
            session.headers.update({"Authorization": f"Bearer {self.token}"})

            for product in self.products_to_download:
                try:
                    prod_id = product["Id"]
                    prod_name = product["Name"].split(".")[0]
                    download_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({prod_id})/$value"
                    self.comm.log_signal.emit(f"Stahuji: {prod_name}")

                    resp = session.get(download_url, allow_redirects=False)
                    while resp.status_code in (301, 302, 303, 307):
                        download_url = resp.headers["Location"]
                        resp = session.get(download_url, allow_redirects=False)

                    file_resp = session.get(download_url, stream=True)
                    file_path = os.path.join(folder, f"{prod_name}.zip")
                    with open(file_path, "wb") as f:
                        for chunk in file_resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    self.comm.log_signal.emit(f"Uloženo do: {file_path}")
                except Exception as e:
                    self.comm.log_signal.emit(f"Chyba při stahování {product['Name']}: {e}")

            self.comm.message_signal.emit(
                translations[self.current_language]["complete"],
                translations[self.current_language]["download_complete"],
                "info"
            )

        except Exception as ex:
            self.comm.log_signal.emit(f"Neočekávaná chyba při stahování: {ex}")
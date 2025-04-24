# c2rcc_processor.py
import os
import threading
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QCheckBox, QFileDialog, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject
from translations import translations

# SNAP cesta
sys.path.append('C:\\Users\\rybar\\.snap\\snap-python')

# ----------------------------------------------------------------------------------------------------------------------
# Class: C2RCCSignals
# Description: Defines custom signals for logging and messaging between the processing thread and GUI.
# Signals:
#   log_signal (str): Emits log messages.
#   message_signal (str, str, str): Emits popup dialogs: (title, message, type).
class C2RCCSignals(QObject):
    log_signal = Signal(str)
    message_signal = Signal(str, str, str)

# ----------------------------------------------------------------------------------------------------------------------
# Class: C2RCCProcessorGUI
# Description: GUI widget for running the C2RCC water quality processor using SNAP.
# Allows selecting input/output folders, shapefile, and output options.
class C2RCCProcessorGUI(QWidget):
    # Function: __init__
    # Description: Initialize GUI, default language, custom signals, and build UI components.
    # Params: parent (optional QWidget parent).
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = C2RCCSignals()
        self.snap_initialized = False
        self.current_language = "cs"
        self.setup_gui()

        # Signály
        self.signals.log_signal.connect(self.log)
        self.signals.message_signal.connect(self.show_message)

    # Function: setup_gui
    # Description: Construct and arrange all UI elements (entries, buttons, checkboxes, log area).
    def setup_gui(self):
        layout = QVBoxLayout(self)

        self.input_entry = QLineEdit()
        self.output_entry = QLineEdit()
        self.shapefile_entry = QLineEdit()

        self.btn_input = QPushButton()
        self.btn_input.clicked.connect(lambda: self.select_folder(self.input_entry))
        self.btn_output = QPushButton()
        self.btn_output.clicked.connect(lambda: self.select_folder(self.output_entry))
        self.btn_shapefile = QPushButton()
        self.btn_shapefile.clicked.connect(lambda: self.select_file(self.shapefile_entry))

        for label_key, entry, button in [
            ("input_folder", self.input_entry, self.btn_input),
            ("output_folder", self.output_entry, self.btn_output),
            ("shapefile_label", self.shapefile_entry, self.btn_shapefile)
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(translations[self.current_language][label_key]))
            row.addWidget(entry)
            row.addWidget(button)
            layout.addLayout(row)

        # Výstupní volby
        self.check_rrs = QCheckBox()
        self.check_ac = QCheckBox()
        self.check_iop = QCheckBox()
        self.check_iopbio = QCheckBox()
        self.check_kd = QCheckBox()
        self.check_unc = QCheckBox()
        self.check_total = QCheckBox()

        self.check_rrs.setChecked(True)
        self.check_ac.setChecked(True)
        self.check_iop.setChecked(True)
        self.check_iopbio.setChecked(True)
        self.check_kd.setChecked(True)
        self.check_total.setChecked(True)

        self.output_group = QGroupBox()
        output_layout = QVBoxLayout(self.output_group)
        for cb in [self.check_rrs, self.check_ac, self.check_iop, self.check_iopbio, self.check_kd, self.check_unc, self.check_total]:
            output_layout.addWidget(cb)
        layout.addWidget(self.output_group)

        # Tlačítko spuštění
        self.process_button = QPushButton()
        self.process_button.clicked.connect(self.run_thread)
        layout.addWidget(self.process_button)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)
        self.update_translations(self.current_language)

    def update_translations(self, lang):
        self.current_language = lang
        self.findChildren(QLabel)[0].setText(translations[lang]["input_folder"])
        self.findChildren(QLabel)[1].setText(translations[lang]["output_folder"])
        self.findChildren(QLabel)[2].setText(translations[lang]["shapefile_label"])
        self.btn_input.setText(translations[lang]["select"])
        self.btn_output.setText(translations[lang]["select"])
        self.btn_shapefile.setText(translations[lang]["select"])
        self.output_group.setTitle(translations[lang]["output_options"])
        self.check_rrs.setText(translations[lang]["rrs"])
        self.check_ac.setText(translations[lang]["ac"])
        self.check_iop.setText(translations[lang]["iop"])
        self.check_iopbio.setText(translations[lang]["iopbio"])
        self.check_kd.setText(translations[lang]["kd"])
        self.check_unc.setText(translations[lang]["unc"])
        self.check_total.setText(translations[lang]["total"])
        self.process_button.setText(translations[lang]["process"])

    # Function: select_folder
    # Description: Open a folder dialog and set path into the provided QLineEdit.
    # Params: entry (QLineEdit to populate).
    def select_folder(self, entry):
        folder = QFileDialog.getExistingDirectory(self, "Vybrat složku")
        if folder:
            entry.setText(folder)

    # Function: select_file
    # Description: Open a file dialog for shapefiles and set path into the QLineEdit.
    # Params: entry (QLineEdit to populate).
    def select_file(self, entry):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vybrat shapefile", "", "Shapefiles (*.shp)")
        if file_path:
            entry.setText(file_path)

    # Function: log
    # Description: Append a message to the GUI log text area.
    # Params: message (str).
    def log(self, message):
        self.log_text.append(message)

    # Function: show_message
    # Description: Display a popup dialog based on msg_type ('info' or 'error').
    # Params: title (str), message (str), msg_type ('info'|'error').
    def show_message(self, title, message, msg_type):
        if msg_type == "error":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def run_thread(self):
        threading.Thread(target=self.run_processing).start()

    # Function: init_snap
    # Description: Initialize the SNAP Java gateway and required modules once before processing.
    def init_snap(self):
        if not self.snap_initialized:
            self.signals.log_signal.emit("🛠️ Inicializuji SNAP prostředí...")
            global ProductIO, GPF, HashMap, jpy, ProductUtils, File, ProgressMonitor
            from esa_snappy import ProductIO, GPF, HashMap, jpy, ProductUtils
            File = jpy.get_type('java.io.File')
            ProgressMonitor = jpy.get_type('com.bc.ceres.core.ProgressMonitor')
            self.snap_initialized = True
            self.signals.log_signal.emit("✅ SNAP inicializace dokončena.")

    # Function: run_processing
    # Description: Execute full C2RCC processing for each .SAFE product in the input folder:
    #   1. Initialize SNAP (if not already).
    #   2. Validate inputs and paths.
    #   3. Resample to 10m, subset by shapefile (optional).
    #   4. Configure C2RCC parameters and run processing.
    #   5. Export outputs and notify user.
    def run_processing(self):
        try:
            self.init_snap()
            vstup = self.input_entry.text()
            vystup = self.output_entry.text()
            shp = self.shapefile_entry.text()

            if not os.path.exists(vstup):
                self.signals.message_signal.emit(
                    translations[self.current_language]["error"],
                    translations[self.current_language]["invalid_input"],
                    "error"
                )
                return

            for item in os.listdir(vstup):
                if item.endswith(".SAFE"):
                    safe_path = os.path.join(vstup, item)
                    input_mtd = os.path.join(safe_path, "MTD_MSIL1C.xml")
                    self.signals.log_signal.emit(f"📂 Načítám produkt: {input_mtd}")
                    product = ProductIO.readProduct(input_mtd)

                    Integer = jpy.get_type('java.lang.Integer')
                    resample_params = HashMap()
                    resample_params.put('targetResolution', Integer(10))
                    resample_params.put('upsampling', 'Nearest')
                    resample_params.put('downsampling', 'First')
                    resample_params.put('resampleOnPyramidLevels', False)

                    self.signals.log_signal.emit("📏 Resample...")
                    product_resampled = GPF.createProduct('Resample', resample_params, product)

                    if shp and os.path.exists(shp):
                        self.signals.log_signal.emit("✂️ Ořez podle shapefile...")
                        subset_params = HashMap()
                        subset_params.put('shapefile', shp)
                        product_subset = GPF.createProduct('Subset', subset_params, product_resampled)
                    else:
                        product_subset = product_resampled
                        self.signals.log_signal.emit("✂️ Přeskakuji ořez...")

                    self.signals.log_signal.emit("🌊 Spouštím C2RCC...")
                    params = HashMap()
                    params.put('salinity', '35.0')
                    params.put('temperature', '15.0')
                    params.put('ozone', '330')
                    params.put('press', '1013')
                    params.put('outputAsRrs', self.check_rrs.isChecked())
                    params.put('outputAcReflectance', self.check_ac.isChecked())
                    params.put('outputIop', self.check_iop.isChecked())
                    params.put('outputIopBio', self.check_iopbio.isChecked())
                    params.put('outputKd', self.check_kd.isChecked())
                    params.put('outputUncertainties', self.check_unc.isChecked())
                    params.put('outputTotalConc', self.check_total.isChecked())

                    product_c2rcc = GPF.createProduct('c2rcc.msi', params, product_subset)

                    output_path = os.path.join(vystup, os.path.basename(safe_path) + "_C2RCC")
                    self.signals.log_signal.emit("💾 Exportuji zvolené produkty...")
                    GPF.writeProduct(product_c2rcc, File(output_path), "BEAM-DIMAP", False, ProgressMonitor.NULL)
                    self.signals.log_signal.emit(f"✅ Hotovo: {output_path}.dim")

            self.signals.message_signal.emit(
                translations[self.current_language]["complete"],
                translations[self.current_language]["processing_complete"],
                "info"
            )

        except Exception as e:
            self.signals.message_signal.emit(
                translations[self.current_language]["error"],
                str(e),
                "error"
            )
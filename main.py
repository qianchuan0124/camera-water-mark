import os
import sys
import platform
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from app.view.main_window import MainWindow
from qfluentwidgets import FluentTranslator
from PyQt5.QtCore import QLocale
from app.utils.logger import setup_logger
logger = setup_logger("main")

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings) # type: ignore

translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
app.installTranslator(translator)

w = MainWindow()
w.show()
sys.exit(app.exec_())
    
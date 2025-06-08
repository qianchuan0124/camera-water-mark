import sys
import traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from app.view.main_window import MainWindow
from qfluentwidgets import FluentTranslator
from PyQt5.QtCore import QLocale
from app.utils.logger import setup_logger

print(""""
本工具为开源工具，遵循 Apache 2.0 License 发布。如果您在使用过程中遇到问题，请联系作者：
      GitHub: @qianchuan0124
      邮箱: qianchuan0124@gmail.com
""")


def exception_hook(exctype, value, tb):
    logger = setup_logger("main")
    logger.exception("".join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)  # 调用默认的异常处理


sys.excepthook = exception_hook

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)  # type: ignore

translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
app.installTranslator(translator)

w = MainWindow()
w.show()
sys.exit(app.exec_())

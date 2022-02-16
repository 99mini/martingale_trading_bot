import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QDate, Qt


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.date = QDate.currentDate()
        self.initUI()

    def initUI(self):
        # window title
        self.setWindowTitle('Date')
        # status bar
        self.statusBar().showMessage(self.date.toString(Qt.DefaultLocaleLongDate))

        # 보유 현금
        krw_balance_label = QLabel('보유 현금: {0}'.format(123), self)

        krw_balance_font = krw_balance_label.font()
        krw_balance_font.setPointSize(14)

        krw_balance_label.setAlignment(Qt.AlignCenter)
        krw_balance_label.setFont(krw_balance_font)
        krw_balance_label.setFixedSize(300, 100)

        start_btn = QPushButton('프로그램 시작', self)
        end_btn = QPushButton('프로그램 종료', self)

        layout = QHBoxLayout()
        # layout.addWidget(krw_balance_label)
        layout.addWidget(start_btn)
        layout.addWidget(end_btn)

        self.setLayout(layout)
        # window size
        self.setGeometry(500, 500, 400, 200)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

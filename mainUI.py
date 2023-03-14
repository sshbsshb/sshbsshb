from PySide2 import QtCore, QtGui
from PySide2.QtCore import Signal, Slot, QTimer
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QMenu, QMenuBar, QStatusBar, QAction, \
    QFileDialog, QLineEdit, QPushButton, QCheckBox, QMessageBox, QVBoxLayout, \
        QTabWidget, QHBoxLayout, QWidget, QHeaderView, QLabel, QDialog
import sys
from EquipmentHandler import EquipmentHandler
from CommandQueue import CommandQueue, CommandQueueExeThread
from configparser import ConfigParser
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self, config_file):
        super(MainWindow, self).__init__()
        self.config_file = config_file

        self.setObjectName("MainWindow")
        self.setWindowTitle("Data Acquisition System V2")
        self.resize(1024, 1024)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(10)
        self.dataPlot = pg.PlotWidget(self.centralwidget)
        self.dataPlot.setObjectName("dataPlot")
        # self.dataPlot.setGeometry(0, 0, 1024, 600)
        self.dataPlot.resize(1420,820)
        self.gridLayout.addWidget(self.dataPlot, 0, 0)


        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.setTabPosition(QTabWidget.North)
        # self.tab_widget.setMovable(True)
        self.gridLayout.addWidget(self.tab_widget, 1, 0)

        # Read the configuration file
        self.config = ConfigParser()
        self.config.read(self.config_file)

        self.command_queue = CommandQueue()
        self.command_queue_exe = CommandQueueExeThread(self.command_queue)

        # Create a tab for each piece of equipment in the configuration file and initial it at the same time
        for section_name in self.config.sections():
            self.equipment_config = dict(self.config[section_name])
            self.equipment_tab = EquipmentHandler(self.equipment_config, self.tab_widget, self.dataPlot, self.command_queue)
            self.tab_widget.addTab(self.equipment_tab, section_name)   

        self.command_queue.command_added.connect(self.process_command_queue)
        self.command_queue_exe.start()

        self.gridLayout.setRowStretch(0, 5)
        self.gridLayout.setRowStretch(1, 1)
        # self.gridLayout.setRowStretch(2, 1)
        # self.gridLayout.setRowStretch(3, 0)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menubar.setNativeMenuBar(False)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionSave = QAction(self)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())
        
        # self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    # def retranslateUi(self, MainWindow):
    #     _translate = QtCore.QCoreApplication.translate
    #     MainWindow.setWindowTitle(_translate("MainWindow", "Data Acquisition System"))
    #     self.daqStartButton.setText(_translate("MainWindow", "Start"))
    #     self.daqConnectButton.setText(_translate("MainWindow", "Connect"))
    #     self.menuFile.setTitle(_translate("MainWindow", "File"))
    #     self.actionSave.setText(_translate("MainWindow", "Save"))

    def process_command_queue(self):
        self.command_queue_exe.execute_wakeup(True)
        
    def closeEvent(self, event):
        self.command_queue_exe.quit()
        self.command_queue_exe.execute_wakeup(False)
        self.command_queue_exe.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataAcquisitionSystem = MainWindow(config_file='./equipment_config.ini')
    dataAcquisitionSystem.show()
    sys.exit(app.exec_())
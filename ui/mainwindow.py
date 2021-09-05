# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1003, 885)
        self.actionImport = QAction(MainWindow)
        self.actionImport.setObjectName(u"actionImport")
        self.actionLoad_from_words = QAction(MainWindow)
        self.actionLoad_from_words.setObjectName(u"actionLoad_from_words")
        self.actionLoad_from_xprv = QAction(MainWindow)
        self.actionLoad_from_xprv.setObjectName(u"actionLoad_from_xprv")
        self.actionNew_HD = QAction(MainWindow)
        self.actionNew_HD.setObjectName(u"actionNew_HD")
        self.actionNew_empty = QAction(MainWindow)
        self.actionNew_empty.setObjectName(u"actionNew_empty")
        self.actionWallets = QAction(MainWindow)
        self.actionWallets.setObjectName(u"actionWallets")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.UTXOsGroupBox = QGroupBox(self.centralwidget)
        self.UTXOsGroupBox.setObjectName(u"UTXOsGroupBox")
        self.verticalLayout_4 = QVBoxLayout(self.UTXOsGroupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.selectUTXOsPushButton = QPushButton(self.UTXOsGroupBox)
        self.selectUTXOsPushButton.setObjectName(u"selectUTXOsPushButton")

        self.verticalLayout_4.addWidget(self.selectUTXOsPushButton)

        self.UTXOsTableWidget = QTableWidget(self.UTXOsGroupBox)
        self.UTXOsTableWidget.setObjectName(u"UTXOsTableWidget")
        self.UTXOsTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.UTXOsTableWidget.setAlternatingRowColors(True)
        self.UTXOsTableWidget.setSelectionMode(QAbstractItemView.MultiSelection)

        self.verticalLayout_4.addWidget(self.UTXOsTableWidget)


        self.horizontalLayout_2.addWidget(self.UTXOsGroupBox)

        self.outputsGroupBox = QGroupBox(self.centralwidget)
        self.outputsGroupBox.setObjectName(u"outputsGroupBox")
        self.outputsGroupBox.setFlat(False)
        self.outputsGroupBox.setCheckable(False)
        self.verticalLayout_5 = QVBoxLayout(self.outputsGroupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.addOutputPushButton = QPushButton(self.outputsGroupBox)
        self.addOutputPushButton.setObjectName(u"addOutputPushButton")

        self.horizontalLayout_4.addWidget(self.addOutputPushButton)

        self.removeOutputPushButton = QPushButton(self.outputsGroupBox)
        self.removeOutputPushButton.setObjectName(u"removeOutputPushButton")

        self.horizontalLayout_4.addWidget(self.removeOutputPushButton)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.outputsListWidget = QListWidget(self.outputsGroupBox)
        self.outputsListWidget.setObjectName(u"outputsListWidget")
        self.outputsListWidget.setAlternatingRowColors(True)

        self.verticalLayout_5.addWidget(self.outputsListWidget)


        self.horizontalLayout_2.addWidget(self.outputsGroupBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.widget_2, 0, 4, 1, 1)

        self.dateTimeEdit = QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit.setObjectName(u"dateTimeEdit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.dateTimeEdit.sizePolicy().hasHeightForWidth())
        self.dateTimeEdit.setSizePolicy(sizePolicy1)
        self.dateTimeEdit.setMinimumSize(QSize(200, 0))
        self.dateTimeEdit.setDateTime(QDateTime(QDate(2033, 5, 18), QTime(3, 40, 0)))
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setTimeSpec(Qt.LocalTime)

        self.gridLayout.addWidget(self.dateTimeEdit, 0, 3, 1, 1)

        self.nLockTimeTypeComboBox = QComboBox(self.centralwidget)
        self.nLockTimeTypeComboBox.setObjectName(u"nLockTimeTypeComboBox")

        self.gridLayout.addWidget(self.nLockTimeTypeComboBox, 0, 1, 1, 1)

        self.locktimeLineEdit = QLineEdit(self.centralwidget)
        self.locktimeLineEdit.setObjectName(u"locktimeLineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.locktimeLineEdit.sizePolicy().hasHeightForWidth())
        self.locktimeLineEdit.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.locktimeLineEdit, 0, 2, 1, 1)

        self.nLockTimeRadioButton = QRadioButton(self.centralwidget)
        self.nLockTimeRadioButton.setObjectName(u"nLockTimeRadioButton")

        self.gridLayout.addWidget(self.nLockTimeRadioButton, 0, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.PreventFeeSnipingRadioButton = QRadioButton(self.centralwidget)
        self.PreventFeeSnipingRadioButton.setObjectName(u"PreventFeeSnipingRadioButton")
        self.PreventFeeSnipingRadioButton.setChecked(True)

        self.verticalLayout_3.addWidget(self.PreventFeeSnipingRadioButton)

        self.RBFCheckBox = QCheckBox(self.centralwidget)
        self.RBFCheckBox.setObjectName(u"RBFCheckBox")
        self.RBFCheckBox.setChecked(False)

        self.verticalLayout_3.addWidget(self.RBFCheckBox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.widget)

        self.signAllPUshButton = QPushButton(self.centralwidget)
        self.signAllPUshButton.setObjectName(u"signAllPUshButton")

        self.horizontalLayout_3.addWidget(self.signAllPUshButton)

        self.verifyPushButton = QPushButton(self.centralwidget)
        self.verifyPushButton.setObjectName(u"verifyPushButton")

        self.horizontalLayout_3.addWidget(self.verifyPushButton)

        self.exportPushButton = QPushButton(self.centralwidget)
        self.exportPushButton.setObjectName(u"exportPushButton")

        self.horizontalLayout_3.addWidget(self.exportPushButton)

        self.broadcastPushButton = QPushButton(self.centralwidget)
        self.broadcastPushButton.setObjectName(u"broadcastPushButton")

        self.horizontalLayout_3.addWidget(self.broadcastPushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1003, 21))
        self.menuTX = QMenu(self.menubar)
        self.menuTX.setObjectName(u"menuTX")
        self.menuWallets = QMenu(self.menubar)
        self.menuWallets.setObjectName(u"menuWallets")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuTX.menuAction())
        self.menubar.addAction(self.menuWallets.menuAction())
        self.menuTX.addAction(self.actionImport)
        self.menuWallets.addSeparator()
        self.menuWallets.addAction(self.actionLoad_from_words)
        self.menuWallets.addAction(self.actionLoad_from_xprv)
        self.menuWallets.addAction(self.actionNew_HD)
        self.menuWallets.addAction(self.actionNew_empty)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"myTxBuilderOrSomething", None))
        self.actionImport.setText(QCoreApplication.translate("MainWindow", u"Import...", None))
        self.actionLoad_from_words.setText(QCoreApplication.translate("MainWindow", u"Regenerate from words", None))
        self.actionLoad_from_xprv.setText(QCoreApplication.translate("MainWindow", u"Regenerate from xprv...", None))
        self.actionNew_HD.setText(QCoreApplication.translate("MainWindow", u"New HD...", None))
        self.actionNew_empty.setText(QCoreApplication.translate("MainWindow", u"New empty...", None))
        self.actionWallets.setText(QCoreApplication.translate("MainWindow", u"Wallets", None))
        self.UTXOsGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"UTXOs", None))
        self.selectUTXOsPushButton.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.outputsGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Outputs", None))
        self.addOutputPushButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.removeOutputPushButton.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.dateTimeEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd HH:mm zzz", None))
        self.locktimeLineEdit.setText(QCoreApplication.translate("MainWindow", u"2000000000", None))
        self.nLockTimeRadioButton.setText(QCoreApplication.translate("MainWindow", u"nLockTime", None))
        self.PreventFeeSnipingRadioButton.setText(QCoreApplication.translate("MainWindow", u"Prevent fee sniping", None))
        self.RBFCheckBox.setText(QCoreApplication.translate("MainWindow", u"Make final", None))
        self.signAllPUshButton.setText(QCoreApplication.translate("MainWindow", u"Sign all mine", None))
        self.verifyPushButton.setText(QCoreApplication.translate("MainWindow", u"Verify", None))
        self.exportPushButton.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.broadcastPushButton.setText(QCoreApplication.translate("MainWindow", u"Broadcast", None))
        self.menuTX.setTitle(QCoreApplication.translate("MainWindow", u"TX", None))
        self.menuWallets.setTitle(QCoreApplication.translate("MainWindow", u"Wallets", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi


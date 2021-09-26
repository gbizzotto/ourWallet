# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
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
        MainWindow.resize(1050, 885)
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
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
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
        self.UTXOsGroupBox.setAlignment(Qt.AlignCenter)
        self.verticalLayout_4 = QVBoxLayout(self.UTXOsGroupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.addInputsPushButton = QPushButton(self.UTXOsGroupBox)
        self.addInputsPushButton.setObjectName(u"addInputsPushButton")

        self.horizontalLayout_11.addWidget(self.addInputsPushButton)

        self.signOneButton = QToolButton(self.UTXOsGroupBox)
        self.signOneButton.setObjectName(u"signOneButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signOneButton.sizePolicy().hasHeightForWidth())
        self.signOneButton.setSizePolicy(sizePolicy)
        self.signOneButton.setPopupMode(QToolButton.MenuButtonPopup)

        self.horizontalLayout_11.addWidget(self.signOneButton)

        self.removeInputsButton = QPushButton(self.UTXOsGroupBox)
        self.removeInputsButton.setObjectName(u"removeInputsButton")

        self.horizontalLayout_11.addWidget(self.removeInputsButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout_11)

        self.inputsView = QTableView(self.UTXOsGroupBox)
        self.inputsView.setObjectName(u"inputsView")
        self.inputsView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.inputsView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inputsView.horizontalHeader().setStretchLastSection(True)
        self.inputsView.verticalHeader().setStretchLastSection(False)

        self.verticalLayout_4.addWidget(self.inputsView)


        self.horizontalLayout_2.addWidget(self.UTXOsGroupBox)

        self.outputsGroupBox = QGroupBox(self.centralwidget)
        self.outputsGroupBox.setObjectName(u"outputsGroupBox")
        self.outputsGroupBox.setAlignment(Qt.AlignCenter)
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

        self.outputsView = QTableView(self.outputsGroupBox)
        self.outputsView.setObjectName(u"outputsView")
        self.outputsView.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_5.addWidget(self.outputsView)


        self.horizontalLayout_2.addWidget(self.outputsGroupBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.widget_4 = QWidget(self.centralwidget)
        self.widget_4.setObjectName(u"widget_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_4.sizePolicy().hasHeightForWidth())
        self.widget_4.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.widget_4)

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_9.addWidget(self.label_5)

        self.transactionSizeEdit = QLineEdit(self.centralwidget)
        self.transactionSizeEdit.setObjectName(u"transactionSizeEdit")
        self.transactionSizeEdit.setReadOnly(True)

        self.horizontalLayout_9.addWidget(self.transactionSizeEdit)

        self.widget_3 = QWidget(self.centralwidget)
        self.widget_3.setObjectName(u"widget_3")
        sizePolicy1.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.widget_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.widget_5 = QWidget(self.centralwidget)
        self.widget_5.setObjectName(u"widget_5")
        sizePolicy1.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy1)

        self.horizontalLayout_10.addWidget(self.widget_5)

        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_10.addWidget(self.label_6)

        self.transactionVSizeEdit = QLineEdit(self.centralwidget)
        self.transactionVSizeEdit.setObjectName(u"transactionVSizeEdit")
        self.transactionVSizeEdit.setReadOnly(True)

        self.horizontalLayout_10.addWidget(self.transactionVSizeEdit)

        self.widget_6 = QWidget(self.centralwidget)
        self.widget_6.setObjectName(u"widget_6")
        sizePolicy1.setHeightForWidth(self.widget_6.sizePolicy().hasHeightForWidth())
        self.widget_6.setSizePolicy(sizePolicy1)

        self.horizontalLayout_10.addWidget(self.widget_6)


        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_8.addWidget(self.label)

        self.inputSumEdit = QLineEdit(self.centralwidget)
        self.inputSumEdit.setObjectName(u"inputSumEdit")
        self.inputSumEdit.setReadOnly(True)

        self.horizontalLayout_8.addWidget(self.inputSumEdit)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_8)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_7.addWidget(self.label_3)

        self.outputSumEdit = QLineEdit(self.centralwidget)
        self.outputSumEdit.setObjectName(u"outputSumEdit")
        self.outputSumEdit.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.outputSumEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.feeEdit = QLineEdit(self.centralwidget)
        self.feeEdit.setObjectName(u"feeEdit")
        self.feeEdit.setReadOnly(True)

        self.horizontalLayout_6.addWidget(self.feeEdit)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_6.addWidget(self.label_4)

        self.feePerByteEdit = QLineEdit(self.centralwidget)
        self.feePerByteEdit.setObjectName(u"feePerByteEdit")
        self.feePerByteEdit.setReadOnly(True)

        self.horizontalLayout_6.addWidget(self.feePerByteEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_5.addLayout(self.verticalLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.widget_2, 0, 4, 1, 1)

        self.locktimeLineEdit = QLineEdit(self.centralwidget)
        self.locktimeLineEdit.setObjectName(u"locktimeLineEdit")
        self.locktimeLineEdit.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.locktimeLineEdit.sizePolicy().hasHeightForWidth())
        self.locktimeLineEdit.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.locktimeLineEdit, 0, 1, 1, 1)

        self.dateTimeEdit = QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit.setObjectName(u"dateTimeEdit")
        self.dateTimeEdit.setEnabled(True)
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.dateTimeEdit.sizePolicy().hasHeightForWidth())
        self.dateTimeEdit.setSizePolicy(sizePolicy4)
        self.dateTimeEdit.setMinimumSize(QSize(200, 0))
        self.dateTimeEdit.setDateTime(QDateTime(QDate(2033, 5, 18), QTime(3, 40, 0)))
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setTimeSpec(Qt.LocalTime)

        self.gridLayout.addWidget(self.dateTimeEdit, 0, 2, 1, 1)

        self.PreventFeeSnipingCheckBox = QCheckBox(self.centralwidget)
        self.PreventFeeSnipingCheckBox.setObjectName(u"PreventFeeSnipingCheckBox")
        self.PreventFeeSnipingCheckBox.setChecked(False)

        self.gridLayout.addWidget(self.PreventFeeSnipingCheckBox, 0, 3, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        sizePolicy2.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy2)

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

        self.clearButton = QPushButton(self.centralwidget)
        self.clearButton.setObjectName(u"clearButton")

        self.horizontalLayout_3.addWidget(self.clearButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1050, 21))
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
        self.menuWallets.addAction(self.actionOpen)
        self.menuWallets.addAction(self.actionLoad_from_words)
        self.menuWallets.addAction(self.actionLoad_from_xprv)
        self.menuWallets.addAction(self.actionNew_HD)
        self.menuWallets.addSeparator()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ourWallet", None))
        self.actionImport.setText(QCoreApplication.translate("MainWindow", u"Import...", None))
        self.actionLoad_from_words.setText(QCoreApplication.translate("MainWindow", u"Regenerate from words...", None))
        self.actionLoad_from_xprv.setText(QCoreApplication.translate("MainWindow", u"Regenerate from xprv...", None))
        self.actionNew_HD.setText(QCoreApplication.translate("MainWindow", u"New HD...", None))
        self.actionNew_empty.setText(QCoreApplication.translate("MainWindow", u"New empty...", None))
        self.actionWallets.setText(QCoreApplication.translate("MainWindow", u"Wallets", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open...", None))
        self.UTXOsGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"UTXOs", None))
        self.addInputsPushButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.signOneButton.setText(QCoreApplication.translate("MainWindow", u"Sign selected", None))
        self.removeInputsButton.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.outputsGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Outputs", None))
        self.addOutputPushButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.removeOutputPushButton.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Transaction size ~", None))
        self.transactionSizeEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Virtual size ~", None))
        self.transactionVSizeEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Inputs total amount", None))
        self.inputSumEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Outputs total amount", None))
        self.outputSumEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Fee", None))
        self.feeEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"sat/B ~", None))
        self.feePerByteEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"LockTime", None))
        self.locktimeLineEdit.setInputMask(QCoreApplication.translate("MainWindow", u"000000000000", None))
        self.locktimeLineEdit.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.dateTimeEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd HH:mm", None))
        self.PreventFeeSnipingCheckBox.setText(QCoreApplication.translate("MainWindow", u"Prevent fee sniping", None))
        self.signAllPUshButton.setText(QCoreApplication.translate("MainWindow", u"Sign all mine", None))
        self.verifyPushButton.setText(QCoreApplication.translate("MainWindow", u"Verify", None))
        self.exportPushButton.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.broadcastPushButton.setText(QCoreApplication.translate("MainWindow", u"Broadcast", None))
        self.clearButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.menuTX.setTitle(QCoreApplication.translate("MainWindow", u"TX", None))
        self.menuWallets.setTitle(QCoreApplication.translate("MainWindow", u"Wallets", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi


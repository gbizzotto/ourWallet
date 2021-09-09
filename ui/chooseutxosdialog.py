# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'chooseutxosdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_ChooseUTXOsDialog(object):
    def setupUi(self, ChooseUTXOsDialog):
        if not ChooseUTXOsDialog.objectName():
            ChooseUTXOsDialog.setObjectName(u"ChooseUTXOsDialog")
        ChooseUTXOsDialog.resize(723, 579)
        self.verticalLayout_2 = QVBoxLayout(ChooseUTXOsDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget = QTabWidget(ChooseUTXOsDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.comboBox = QComboBox(self.tab)
        self.comboBox.setObjectName(u"comboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.comboBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.UTXOsTableWidget = QTableWidget(self.tab)
        self.UTXOsTableWidget.setObjectName(u"UTXOsTableWidget")
        self.UTXOsTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.UTXOsTableWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.UTXOsTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.UTXOsTableWidget.setSortingEnabled(True)
        self.UTXOsTableWidget.horizontalHeader().setVisible(False)
        self.UTXOsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.UTXOsTableWidget.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.UTXOsTableWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.sumLineEdit = QLineEdit(self.tab)
        self.sumLineEdit.setObjectName(u"sumLineEdit")
        self.sumLineEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.sumLineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_3 = QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.tab_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.ffTxidEdit = QLineEdit(self.tab_2)
        self.ffTxidEdit.setObjectName(u"ffTxidEdit")

        self.horizontalLayout_3.addWidget(self.ffTxidEdit)

        self.label_4 = QLabel(self.tab_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.ffVoutEdit = QLineEdit(self.tab_2)
        self.ffVoutEdit.setObjectName(u"ffVoutEdit")
        self.ffVoutEdit.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_3.addWidget(self.ffVoutEdit)

        self.ffDLDataButton = QPushButton(self.tab_2)
        self.ffDLDataButton.setObjectName(u"ffDLDataButton")

        self.horizontalLayout_3.addWidget(self.ffDLDataButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.ffUTXOsTableWidget = QTableWidget(self.tab_2)
        self.ffUTXOsTableWidget.setObjectName(u"ffUTXOsTableWidget")
        self.ffUTXOsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.ffUTXOsTableWidget.verticalHeader().setVisible(False)

        self.verticalLayout_3.addWidget(self.ffUTXOsTableWidget)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_4.addWidget(self.label_5)

        self.ffUTXOsSumEdit = QLineEdit(self.tab_2)
        self.ffUTXOsSumEdit.setObjectName(u"ffUTXOsSumEdit")
        self.ffUTXOsSumEdit.setReadOnly(True)

        self.horizontalLayout_4.addWidget(self.ffUTXOsSumEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(ChooseUTXOsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(ChooseUTXOsDialog)
        self.buttonBox.accepted.connect(ChooseUTXOsDialog.accept)
        self.buttonBox.rejected.connect(ChooseUTXOsDialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ChooseUTXOsDialog)
    # setupUi

    def retranslateUi(self, ChooseUTXOsDialog):
        ChooseUTXOsDialog.setWindowTitle(QCoreApplication.translate("ChooseUTXOsDialog", u"Choost UTXOs", None))
        self.label_2.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"Wallet", None))
        self.label.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"Sum", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("ChooseUTXOsDialog", u"From open wallets", None))
        self.label_3.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"txid", None))
        self.label_4.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"vout", None))
        self.ffDLDataButton.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"Download data", None))
        self.label_5.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"Sum", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("ChooseUTXOsDialog", u"Free-floating", None))
    # retranslateUi


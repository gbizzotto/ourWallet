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
        self.UTXOsTableWidget = QTableWidget(ChooseUTXOsDialog)
        self.UTXOsTableWidget.setObjectName(u"UTXOsTableWidget")
        self.UTXOsTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.UTXOsTableWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.UTXOsTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.UTXOsTableWidget.setSortingEnabled(True)
        self.UTXOsTableWidget.horizontalHeader().setVisible(True)
        self.UTXOsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.UTXOsTableWidget.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.UTXOsTableWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(ChooseUTXOsDialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.sumLineEdit = QLineEdit(ChooseUTXOsDialog)
        self.sumLineEdit.setObjectName(u"sumLineEdit")
        self.sumLineEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.sumLineEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(ChooseUTXOsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(ChooseUTXOsDialog)
        self.buttonBox.accepted.connect(ChooseUTXOsDialog.accept)
        self.buttonBox.rejected.connect(ChooseUTXOsDialog.reject)

        QMetaObject.connectSlotsByName(ChooseUTXOsDialog)
    # setupUi

    def retranslateUi(self, ChooseUTXOsDialog):
        ChooseUTXOsDialog.setWindowTitle(QCoreApplication.translate("ChooseUTXOsDialog", u"Choost UTXOs", None))
        self.label.setText(QCoreApplication.translate("ChooseUTXOsDialog", u"Sum", None))
    # retranslateUi


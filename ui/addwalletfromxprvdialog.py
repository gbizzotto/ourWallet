# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'addwalletfromxprvdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_AddWalletFromXprvDialog(object):
    def setupUi(self, AddWalletFromXprvDialog):
        if not AddWalletFromXprvDialog.objectName():
            AddWalletFromXprvDialog.setObjectName(u"AddWalletFromXprvDialog")
        AddWalletFromXprvDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(AddWalletFromXprvDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.nameLineEdit = QLineEdit(AddWalletFromXprvDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.verticalLayout.addWidget(self.nameLineEdit)

        self.xprvPlainTextEdit = QPlainTextEdit(AddWalletFromXprvDialog)
        self.xprvPlainTextEdit.setObjectName(u"xprvPlainTextEdit")

        self.verticalLayout.addWidget(self.xprvPlainTextEdit)

        self.warningLabel = QLabel(AddWalletFromXprvDialog)
        self.warningLabel.setObjectName(u"warningLabel")

        self.verticalLayout.addWidget(self.warningLabel)

        self.buttonBox = QDialogButtonBox(AddWalletFromXprvDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AddWalletFromXprvDialog)
        self.buttonBox.accepted.connect(AddWalletFromXprvDialog.accept)
        self.buttonBox.rejected.connect(AddWalletFromXprvDialog.reject)

        QMetaObject.connectSlotsByName(AddWalletFromXprvDialog)
    # setupUi

    def retranslateUi(self, AddWalletFromXprvDialog):
        AddWalletFromXprvDialog.setWindowTitle(QCoreApplication.translate("AddWalletFromXprvDialog", u"Dialog", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("AddWalletFromXprvDialog", u"Wallet name", None))
        self.xprvPlainTextEdit.setPlaceholderText(QCoreApplication.translate("AddWalletFromXprvDialog", u"Extended private key (mainnet: xprv, yprv or zprv. testnet: tprv, uprv or vprv)", None))
        self.warningLabel.setText("")
    # retranslateUi


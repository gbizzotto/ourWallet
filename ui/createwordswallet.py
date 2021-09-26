# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'createwordswallet.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_CreateWordWalletDialog(object):
    def setupUi(self, CreateWordWalletDialog):
        if not CreateWordWalletDialog.objectName():
            CreateWordWalletDialog.setObjectName(u"CreateWordWalletDialog")
        CreateWordWalletDialog.resize(400, 332)
        self.verticalLayout_2 = QVBoxLayout(CreateWordWalletDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.nameLineEdit = QLineEdit(CreateWordWalletDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.verticalLayout.addWidget(self.nameLineEdit)

        self.generatePushButton = QPushButton(CreateWordWalletDialog)
        self.generatePushButton.setObjectName(u"generatePushButton")

        self.verticalLayout.addWidget(self.generatePushButton)

        self.wordsPlainTextEdit = QPlainTextEdit(CreateWordWalletDialog)
        self.wordsPlainTextEdit.setObjectName(u"wordsPlainTextEdit")
        font = QFont()
        font.setFamilies([u"FreeMono"])
        self.wordsPlainTextEdit.setFont(font)
        self.wordsPlainTextEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.wordsPlainTextEdit)

        self.pwLineEdit = QLineEdit(CreateWordWalletDialog)
        self.pwLineEdit.setObjectName(u"pwLineEdit")
        self.pwLineEdit.setEchoMode(QLineEdit.Password)

        self.verticalLayout.addWidget(self.pwLineEdit)

        self.warningLabel = QLabel(CreateWordWalletDialog)
        self.warningLabel.setObjectName(u"warningLabel")
        self.warningLabel.setWordWrap(False)

        self.verticalLayout.addWidget(self.warningLabel)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(CreateWordWalletDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setEnabled(True)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(CreateWordWalletDialog)
        self.buttonBox.accepted.connect(CreateWordWalletDialog.accept)
        self.buttonBox.rejected.connect(CreateWordWalletDialog.reject)

        QMetaObject.connectSlotsByName(CreateWordWalletDialog)
    # setupUi

    def retranslateUi(self, CreateWordWalletDialog):
        CreateWordWalletDialog.setWindowTitle(QCoreApplication.translate("CreateWordWalletDialog", u"Load wallet from words", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("CreateWordWalletDialog", u"Wallet name", None))
        self.generatePushButton.setText(QCoreApplication.translate("CreateWordWalletDialog", u"Generate passphrase", None))
        self.wordsPlainTextEdit.setPlaceholderText(QCoreApplication.translate("CreateWordWalletDialog", u"words", None))
        self.pwLineEdit.setPlaceholderText(QCoreApplication.translate("CreateWordWalletDialog", u"BIP38 Password (optional)", None))
        self.warningLabel.setText("")
    # retranslateUi


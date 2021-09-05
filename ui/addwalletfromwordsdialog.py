# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'addwalletfromwordsdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_AddWalletFromWordsDialog(object):
    def setupUi(self, AddWalletFromWordsDialog):
        if not AddWalletFromWordsDialog.objectName():
            AddWalletFromWordsDialog.setObjectName(u"AddWalletFromWordsDialog")
        AddWalletFromWordsDialog.resize(400, 332)
        self.verticalLayout_2 = QVBoxLayout(AddWalletFromWordsDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.nameLineEdit = QLineEdit(AddWalletFromWordsDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.verticalLayout.addWidget(self.nameLineEdit)

        self.wordsPlainTextEdit = QPlainTextEdit(AddWalletFromWordsDialog)
        self.wordsPlainTextEdit.setObjectName(u"wordsPlainTextEdit")
        font = QFont()
        font.setFamilies([u"FreeMono"])
        self.wordsPlainTextEdit.setFont(font)

        self.verticalLayout.addWidget(self.wordsPlainTextEdit)

        self.pwLineEdit = QLineEdit(AddWalletFromWordsDialog)
        self.pwLineEdit.setObjectName(u"pwLineEdit")
        self.pwLineEdit.setEchoMode(QLineEdit.Password)

        self.verticalLayout.addWidget(self.pwLineEdit)

        self.warningLabel = QLabel(AddWalletFromWordsDialog)
        self.warningLabel.setObjectName(u"warningLabel")
        self.warningLabel.setWordWrap(False)

        self.verticalLayout.addWidget(self.warningLabel)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(AddWalletFromWordsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setEnabled(True)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(AddWalletFromWordsDialog)
        self.buttonBox.accepted.connect(AddWalletFromWordsDialog.accept)
        self.buttonBox.rejected.connect(AddWalletFromWordsDialog.reject)

        QMetaObject.connectSlotsByName(AddWalletFromWordsDialog)
    # setupUi

    def retranslateUi(self, AddWalletFromWordsDialog):
        AddWalletFromWordsDialog.setWindowTitle(QCoreApplication.translate("AddWalletFromWordsDialog", u"Load wallet from words", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("AddWalletFromWordsDialog", u"Wallet name", None))
        self.wordsPlainTextEdit.setPlaceholderText(QCoreApplication.translate("AddWalletFromWordsDialog", u"words", None))
        self.pwLineEdit.setPlaceholderText(QCoreApplication.translate("AddWalletFromWordsDialog", u"BIP38 Password (if any)", None))
        self.warningLabel.setText("")
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'passworddialog.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_passwordDialog(object):
    def setupUi(self, passwordDialog):
        if not passwordDialog.objectName():
            passwordDialog.setObjectName(u"passwordDialog")
        passwordDialog.resize(400, 147)
        self.verticalLayout = QVBoxLayout(passwordDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.passwordEdit = QLineEdit(passwordDialog)
        self.passwordEdit.setObjectName(u"passwordEdit")
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        self.verticalLayout.addWidget(self.passwordEdit)

        self.buttonBox = QDialogButtonBox(passwordDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(passwordDialog)
        self.buttonBox.accepted.connect(passwordDialog.accept)
        self.buttonBox.rejected.connect(passwordDialog.reject)

        QMetaObject.connectSlotsByName(passwordDialog)
    # setupUi

    def retranslateUi(self, passwordDialog):
        passwordDialog.setWindowTitle(QCoreApplication.translate("passwordDialog", u"Dialog", None))
        self.passwordEdit.setPlaceholderText(QCoreApplication.translate("passwordDialog", u"Wallet password", None))
    # retranslateUi


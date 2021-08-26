# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'addwalletdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_AddWalletDialog(object):
    def setupUi(self, AddWalletDialog):
        if not AddWalletDialog.objectName():
            AddWalletDialog.setObjectName(u"AddWalletDialog")
        AddWalletDialog.resize(400, 332)
        self.verticalLayout_2 = QVBoxLayout(AddWalletDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.nameLineEdit = QLineEdit(AddWalletDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.verticalLayout.addWidget(self.nameLineEdit)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")

        self.verticalLayout.addLayout(self.verticalLayout_5)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.wordsRadioButton = QRadioButton(AddWalletDialog)
        self.wordsRadioButton.setObjectName(u"wordsRadioButton")

        self.horizontalLayout_3.addWidget(self.wordsRadioButton)

        self.generateWordsPushButton = QPushButton(AddWalletDialog)
        self.generateWordsPushButton.setObjectName(u"generateWordsPushButton")

        self.horizontalLayout_3.addWidget(self.generateWordsPushButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(AddWalletDialog)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.widget)

        self.textEdit = QTextEdit(AddWalletDialog)
        self.textEdit.setObjectName(u"textEdit")

        self.horizontalLayout.addWidget(self.textEdit)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.verticalLayout_4)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.xprvRadioButton = QRadioButton(AddWalletDialog)
        self.xprvRadioButton.setObjectName(u"xprvRadioButton")

        self.horizontalLayout_4.addWidget(self.xprvRadioButton)

        self.generatexprvpushButton = QPushButton(AddWalletDialog)
        self.generatexprvpushButton.setObjectName(u"generatexprvpushButton")

        self.horizontalLayout_4.addWidget(self.generatexprvpushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.widget_2 = QWidget(AddWalletDialog)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(30, 0))

        self.horizontalLayout_2.addWidget(self.widget_2)

        self.xprvLineEdit = QLineEdit(AddWalletDialog)
        self.xprvLineEdit.setObjectName(u"xprvLineEdit")

        self.horizontalLayout_2.addWidget(self.xprvLineEdit)

        self.pushButton = QPushButton(AddWalletDialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.pushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.radioButton = QRadioButton(AddWalletDialog)
        self.radioButton.setObjectName(u"radioButton")

        self.verticalLayout_6.addWidget(self.radioButton)


        self.verticalLayout.addLayout(self.verticalLayout_6)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(AddWalletDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(AddWalletDialog)
        self.buttonBox.accepted.connect(AddWalletDialog.accept)
        self.buttonBox.rejected.connect(AddWalletDialog.reject)

        QMetaObject.connectSlotsByName(AddWalletDialog)
    # setupUi

    def retranslateUi(self, AddWalletDialog):
        AddWalletDialog.setWindowTitle(QCoreApplication.translate("AddWalletDialog", u"Dialog", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("AddWalletDialog", u"Wallet name", None))
        self.wordsRadioButton.setText(QCoreApplication.translate("AddWalletDialog", u"from words", None))
        self.generateWordsPushButton.setText(QCoreApplication.translate("AddWalletDialog", u"Generate", None))
        self.textEdit.setPlaceholderText(QCoreApplication.translate("AddWalletDialog", u"words", None))
        self.xprvRadioButton.setText(QCoreApplication.translate("AddWalletDialog", u"from xprv", None))
        self.generatexprvpushButton.setText(QCoreApplication.translate("AddWalletDialog", u"Generate", None))
        self.xprvLineEdit.setPlaceholderText(QCoreApplication.translate("AddWalletDialog", u"xprv", None))
        self.pushButton.setText(QCoreApplication.translate("AddWalletDialog", u"Scan QrCode image", None))
        self.radioButton.setText(QCoreApplication.translate("AddWalletDialog", u"just random private keys", None))
    # retranslateUi


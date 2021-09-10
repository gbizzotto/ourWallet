# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'privatekeydialog.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_PKeyDialog(object):
    def setupUi(self, PKeyDialog):
        if not PKeyDialog.objectName():
            PKeyDialog.setObjectName(u"PKeyDialog")
        PKeyDialog.resize(400, 332)
        self.verticalLayout_2 = QVBoxLayout(PKeyDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_2 = QWidget(PKeyDialog)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.widget_2)

        self.pkLineEdit = QLineEdit(PKeyDialog)
        self.pkLineEdit.setObjectName(u"pkLineEdit")

        self.verticalLayout.addWidget(self.pkLineEdit)

        self.warningLabel = QLabel(PKeyDialog)
        self.warningLabel.setObjectName(u"warningLabel")

        self.verticalLayout.addWidget(self.warningLabel)

        self.widget = QWidget(PKeyDialog)
        self.widget.setObjectName(u"widget")
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.widget)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(PKeyDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setEnabled(True)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(PKeyDialog)
        self.buttonBox.accepted.connect(PKeyDialog.accept)
        self.buttonBox.rejected.connect(PKeyDialog.reject)

        QMetaObject.connectSlotsByName(PKeyDialog)
    # setupUi

    def retranslateUi(self, PKeyDialog):
        PKeyDialog.setWindowTitle(QCoreApplication.translate("PKeyDialog", u"Load wallet from words", None))
        self.pkLineEdit.setPlaceholderText(QCoreApplication.translate("PKeyDialog", u"Private key", None))
        self.warningLabel.setText("")
    # retranslateUi


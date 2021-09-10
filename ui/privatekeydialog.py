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

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(PKeyDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.outpointLabel = QLabel(PKeyDialog)
        self.outpointLabel.setObjectName(u"outpointLabel")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.outpointLabel)

        self.label_3 = QLabel(PKeyDialog)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_3)

        self.vinLabel = QLabel(PKeyDialog)
        self.vinLabel.setObjectName(u"vinLabel")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.vinLabel)

        self.label_2 = QLabel(PKeyDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.scriptTypeLabel = QLabel(PKeyDialog)
        self.scriptTypeLabel.setObjectName(u"scriptTypeLabel")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.scriptTypeLabel)

        self.label_5 = QLabel(PKeyDialog)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self.confirmationsLabel = QLabel(PKeyDialog)
        self.confirmationsLabel.setObjectName(u"confirmationsLabel")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.confirmationsLabel)

        self.label_4 = QLabel(PKeyDialog)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.amountLabel = QLabel(PKeyDialog)
        self.amountLabel.setObjectName(u"amountLabel")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.amountLabel)


        self.verticalLayout.addLayout(self.formLayout)

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
        self.label.setText(QCoreApplication.translate("PKeyDialog", u"Outpoint", None))
        self.outpointLabel.setText("")
        self.label_3.setText(QCoreApplication.translate("PKeyDialog", u"vin in your tx", None))
        self.vinLabel.setText("")
        self.label_2.setText(QCoreApplication.translate("PKeyDialog", u"scriptpubkey type", None))
        self.scriptTypeLabel.setText("")
        self.label_5.setText(QCoreApplication.translate("PKeyDialog", u"Confirmations", None))
        self.confirmationsLabel.setText("")
        self.label_4.setText(QCoreApplication.translate("PKeyDialog", u"Amount", None))
        self.amountLabel.setText("")
        self.pkLineEdit.setPlaceholderText(QCoreApplication.translate("PKeyDialog", u"Private key", None))
        self.warningLabel.setText("")
    # retranslateUi


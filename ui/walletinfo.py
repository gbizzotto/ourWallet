# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'walletinfo.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_walletInfoDialog(object):
    def setupUi(self, walletInfoDialog):
        if not walletInfoDialog.objectName():
            walletInfoDialog.setObjectName(u"walletInfoDialog")
        walletInfoDialog.resize(449, 567)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(walletInfoDialog.sizePolicy().hasHeightForWidth())
        walletInfoDialog.setSizePolicy(sizePolicy)
        walletInfoDialog.setMinimumSize(QSize(256, 256))
        self.verticalLayout = QVBoxLayout(walletInfoDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(walletInfoDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.utxoTable = QTableWidget(self.tab_2)
        self.utxoTable.setObjectName(u"utxoTable")
        self.utxoTable.horizontalHeader().setStretchLastSection(True)
        self.utxoTable.verticalHeader().setVisible(False)

        self.verticalLayout_4.addWidget(self.utxoTable)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.tab_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.balanceEdit = QLineEdit(self.tab_2)
        self.balanceEdit.setObjectName(u"balanceEdit")
        self.balanceEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.balanceEdit)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.tab_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.utxoDerivationCombo = QComboBox(self.tab_2)
        self.utxoDerivationCombo.setObjectName(u"utxoDerivationCombo")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.utxoDerivationCombo.sizePolicy().hasHeightForWidth())
        self.utxoDerivationCombo.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.utxoDerivationCombo)

        self.utxoRefreshButton = QPushButton(self.tab_2)
        self.utxoRefreshButton.setObjectName(u"utxoRefreshButton")

        self.horizontalLayout_4.addWidget(self.utxoRefreshButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.saveButton = QPushButton(self.tab_2)
        self.saveButton.setObjectName(u"saveButton")

        self.verticalLayout_4.addWidget(self.saveButton)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.buttonBox = QDialogButtonBox(self.tab)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy2)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.NoButton)

        self.verticalLayout_3.addWidget(self.buttonBox)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.addressRadio = QRadioButton(self.tab)
        self.addressRadio.setObjectName(u"addressRadio")
        self.addressRadio.setChecked(True)

        self.horizontalLayout_2.addWidget(self.addressRadio)

        self.keyRadio = QRadioButton(self.tab)
        self.keyRadio.setObjectName(u"keyRadio")
        self.keyRadio.setChecked(False)

        self.horizontalLayout_2.addWidget(self.keyRadio)

        self.xpubRadio = QRadioButton(self.tab)
        self.xpubRadio.setObjectName(u"xpubRadio")

        self.horizontalLayout_2.addWidget(self.xpubRadio)

        self.xprvRadio = QRadioButton(self.tab)
        self.xprvRadio.setObjectName(u"xprvRadio")

        self.horizontalLayout_2.addWidget(self.xprvRadio)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.derivationCombo = QComboBox(self.tab)
        self.derivationCombo.setObjectName(u"derivationCombo")
        sizePolicy1.setHeightForWidth(self.derivationCombo.sizePolicy().hasHeightForWidth())
        self.derivationCombo.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.derivationCombo)

        self.derivationEdit = QLineEdit(self.tab)
        self.derivationEdit.setObjectName(u"derivationEdit")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.derivationEdit.sizePolicy().hasHeightForWidth())
        self.derivationEdit.setSizePolicy(sizePolicy3)
        self.derivationEdit.setMinimumSize(QSize(128, 0))
        self.derivationEdit.setBaseSize(QSize(128, 0))

        self.horizontalLayout_3.addWidget(self.derivationEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.qrcodeLabel = QLabel(self.tab)
        self.qrcodeLabel.setObjectName(u"qrcodeLabel")
        sizePolicy.setHeightForWidth(self.qrcodeLabel.sizePolicy().hasHeightForWidth())
        self.qrcodeLabel.setSizePolicy(sizePolicy)
        self.qrcodeLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.qrcodeLabel)

        self.valueEdit = QTextEdit(self.tab)
        self.valueEdit.setObjectName(u"valueEdit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.valueEdit.sizePolicy().hasHeightForWidth())
        self.valueEdit.setSizePolicy(sizePolicy4)
        self.valueEdit.setMinimumSize(QSize(0, 64))
        self.valueEdit.setMaximumSize(QSize(16777215, 64))
        self.valueEdit.setBaseSize(QSize(0, 64))
        self.valueEdit.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.valueEdit)

        self.tabWidget.addTab(self.tab, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(walletInfoDialog)
        self.buttonBox.accepted.connect(walletInfoDialog.accept)
        self.buttonBox.rejected.connect(walletInfoDialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(walletInfoDialog)
    # setupUi

    def retranslateUi(self, walletInfoDialog):
        walletInfoDialog.setWindowTitle(QCoreApplication.translate("walletInfoDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("walletInfoDialog", u"Balance", None))
        self.label_3.setText(QCoreApplication.translate("walletInfoDialog", u"Derivation scheme", None))
        self.utxoRefreshButton.setText(QCoreApplication.translate("walletInfoDialog", u"Refresh", None))
        self.saveButton.setText(QCoreApplication.translate("walletInfoDialog", u"Save", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("walletInfoDialog", u"UTXOs", None))
        self.addressRadio.setText(QCoreApplication.translate("walletInfoDialog", u"address", None))
        self.keyRadio.setText(QCoreApplication.translate("walletInfoDialog", u"private key", None))
        self.xpubRadio.setText(QCoreApplication.translate("walletInfoDialog", u"xpub", None))
        self.xprvRadio.setText(QCoreApplication.translate("walletInfoDialog", u"xprv", None))
        self.label_2.setText(QCoreApplication.translate("walletInfoDialog", u"Derivation", None))
        self.derivationCombo.setCurrentText("")
        self.derivationEdit.setText("")
        self.qrcodeLabel.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("walletInfoDialog", u"Addresses", None))
    # retranslateUi


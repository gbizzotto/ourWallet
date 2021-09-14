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
        walletInfoDialog.resize(514, 497)
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
        self.tab_utxos = QWidget()
        self.tab_utxos.setObjectName(u"tab_utxos")
        self.verticalLayout_4 = QVBoxLayout(self.tab_utxos)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.utxoTable = QTableWidget(self.tab_utxos)
        self.utxoTable.setObjectName(u"utxoTable")
        self.utxoTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.utxoTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.utxoTable.horizontalHeader().setStretchLastSection(True)
        self.utxoTable.verticalHeader().setVisible(False)

        self.verticalLayout_4.addWidget(self.utxoTable)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.tab_utxos)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.balanceEdit = QLineEdit(self.tab_utxos)
        self.balanceEdit.setObjectName(u"balanceEdit")
        self.balanceEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.balanceEdit)

        self.utxoRefreshButton = QPushButton(self.tab_utxos)
        self.utxoRefreshButton.setObjectName(u"utxoRefreshButton")

        self.horizontalLayout.addWidget(self.utxoRefreshButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.tabWidget.addTab(self.tab_utxos, "")
        self.tab_addresses = QWidget()
        self.tab_addresses.setObjectName(u"tab_addresses")
        self.verticalLayout_3 = QVBoxLayout(self.tab_addresses)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.buttonBox = QDialogButtonBox(self.tab_addresses)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy1)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.NoButton)

        self.verticalLayout_3.addWidget(self.buttonBox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.showChangeCheckBox = QCheckBox(self.tab_addresses)
        self.showChangeCheckBox.setObjectName(u"showChangeCheckBox")

        self.horizontalLayout_3.addWidget(self.showChangeCheckBox)

        self.showWIFCheckBox = QCheckBox(self.tab_addresses)
        self.showWIFCheckBox.setObjectName(u"showWIFCheckBox")

        self.horizontalLayout_3.addWidget(self.showWIFCheckBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.tab_addresses)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.fromEdit = QLineEdit(self.tab_addresses)
        self.fromEdit.setObjectName(u"fromEdit")

        self.horizontalLayout_2.addWidget(self.fromEdit)

        self.label_9 = QLabel(self.tab_addresses)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_2.addWidget(self.label_9)

        self.toEdit = QLineEdit(self.tab_addresses)
        self.toEdit.setObjectName(u"toEdit")

        self.horizontalLayout_2.addWidget(self.toEdit)

        self.showMoreButton = QPushButton(self.tab_addresses)
        self.showMoreButton.setObjectName(u"showMoreButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.showMoreButton.sizePolicy().hasHeightForWidth())
        self.showMoreButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.showMoreButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.addressTableWidget = QTableWidget(self.tab_addresses)
        self.addressTableWidget.setObjectName(u"addressTableWidget")
        self.addressTableWidget.horizontalHeader().setStretchLastSection(True)
        self.addressTableWidget.verticalHeader().setVisible(False)
        self.addressTableWidget.verticalHeader().setStretchLastSection(True)

        self.verticalLayout_3.addWidget(self.addressTableWidget)

        self.qrcodeLabel = QLabel(self.tab_addresses)
        self.qrcodeLabel.setObjectName(u"qrcodeLabel")
        sizePolicy.setHeightForWidth(self.qrcodeLabel.sizePolicy().hasHeightForWidth())
        self.qrcodeLabel.setSizePolicy(sizePolicy)
        self.qrcodeLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.qrcodeLabel)

        self.tabWidget.addTab(self.tab_addresses, "")
        self.tab_config = QWidget()
        self.tab_config.setObjectName(u"tab_config")
        self.verticalLayout_5 = QVBoxLayout(self.tab_config)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_8 = QLabel(self.tab_config)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_8)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.addressDerivationEdit = QLineEdit(self.tab_config)
        self.addressDerivationEdit.setObjectName(u"addressDerivationEdit")

        self.gridLayout.addWidget(self.addressDerivationEdit, 2, 1, 1, 1)

        self.whereFromComboBox = QComboBox(self.tab_config)
        self.whereFromComboBox.setObjectName(u"whereFromComboBox")

        self.gridLayout.addWidget(self.whereFromComboBox, 0, 1, 1, 1)

        self.label_6 = QLabel(self.tab_config)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)

        self.addressTypeComboBox = QComboBox(self.tab_config)
        self.addressTypeComboBox.setObjectName(u"addressTypeComboBox")

        self.gridLayout.addWidget(self.addressTypeComboBox, 4, 1, 1, 1)

        self.label_5 = QLabel(self.tab_config)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.changeDerivationEdit = QLineEdit(self.tab_config)
        self.changeDerivationEdit.setObjectName(u"changeDerivationEdit")

        self.gridLayout.addWidget(self.changeDerivationEdit, 3, 1, 1, 1)

        self.label_4 = QLabel(self.tab_config)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.label_2 = QLabel(self.tab_config)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_7 = QLabel(self.tab_config)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 4, 0, 1, 1)

        self.derivationSchemeComboBox = QComboBox(self.tab_config)
        self.derivationSchemeComboBox.setObjectName(u"derivationSchemeComboBox")

        self.gridLayout.addWidget(self.derivationSchemeComboBox, 1, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout)

        self.widget = QWidget(self.tab_config)
        self.widget.setObjectName(u"widget")
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)

        self.verticalLayout_5.addWidget(self.widget)

        self.tabWidget.addTab(self.tab_config, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.saveButton = QPushButton(walletInfoDialog)
        self.saveButton.setObjectName(u"saveButton")

        self.verticalLayout.addWidget(self.saveButton)


        self.retranslateUi(walletInfoDialog)
        self.buttonBox.accepted.connect(walletInfoDialog.accept)
        self.buttonBox.rejected.connect(walletInfoDialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(walletInfoDialog)
    # setupUi

    def retranslateUi(self, walletInfoDialog):
        walletInfoDialog.setWindowTitle(QCoreApplication.translate("walletInfoDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("walletInfoDialog", u"Balance", None))
        self.utxoRefreshButton.setText(QCoreApplication.translate("walletInfoDialog", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_utxos), QCoreApplication.translate("walletInfoDialog", u"UTXOs", None))
        self.showChangeCheckBox.setText(QCoreApplication.translate("walletInfoDialog", u"Show change addresses", None))
        self.showWIFCheckBox.setText(QCoreApplication.translate("walletInfoDialog", u"Also show private key (WIF format)", None))
        self.label_3.setText(QCoreApplication.translate("walletInfoDialog", u"From", None))
        self.fromEdit.setInputMask(QCoreApplication.translate("walletInfoDialog", u"0000000000", None))
        self.fromEdit.setText(QCoreApplication.translate("walletInfoDialog", u"0", None))
        self.label_9.setText(QCoreApplication.translate("walletInfoDialog", u"to", None))
        self.toEdit.setInputMask(QCoreApplication.translate("walletInfoDialog", u"0000000000", None))
        self.toEdit.setText(QCoreApplication.translate("walletInfoDialog", u"20", None))
        self.showMoreButton.setText(QCoreApplication.translate("walletInfoDialog", u"Show", None))
        self.qrcodeLabel.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addresses), QCoreApplication.translate("walletInfoDialog", u"Addresses", None))
        self.label_8.setText(QCoreApplication.translate("walletInfoDialog", u"Be sure to know what you're doing here", None))
        self.label_6.setText(QCoreApplication.translate("walletInfoDialog", u"Where I got this wallet from", None))
        self.label_5.setText(QCoreApplication.translate("walletInfoDialog", u"Change derivation", None))
        self.label_4.setText(QCoreApplication.translate("walletInfoDialog", u"Deposits derivation", None))
        self.label_2.setText(QCoreApplication.translate("walletInfoDialog", u"Standard derivation schemes", None))
        self.label_7.setText(QCoreApplication.translate("walletInfoDialog", u"Type of addresses to generate", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_config), QCoreApplication.translate("walletInfoDialog", u"Configuration", None))
        self.saveButton.setText(QCoreApplication.translate("walletInfoDialog", u"Save", None))
    # retranslateUi


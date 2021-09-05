# This Python file uses the following encoding: utf-8
import os
import sys
import binascii
from pathlib import Path
from io import BytesIO
import requests
import json
from copy import deepcopy

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox, QMenu, QTableWidgetItem, QCheckBox, QWidgetAction, QFileDialog
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap

from ui.mainwindow import Ui_MainWindow
from ui.addwalletfromwordsdialog import Ui_AddWalletFromWordsDialog
from ui.addwalletfromxprvdialog  import Ui_AddWalletFromXprvDialog
from ui.walletinfo import Ui_walletInfoDialog
from ui.chooseutxosdialog import Ui_ChooseUTXOsDialog

import qrcode

import bip39
import bip32utils

import explorer
import transactions
import util
import wallets
import ourCrypto

testnet = True

def set_qr_label(label, text):
    buf = BytesIO()
    img = qrcode.make(text)
    img.save(buf, "PNG")
    label.setText("")
    qt_pixmap = QPixmap()
    qt_pixmap.loadFromData(buf.getvalue(), "PNG")
    label.setPixmap(qt_pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio))


class WalletInfoDialog(QDialog):
    def __init__(self, wallet):
        super(WalletInfoDialog, self).__init__()
        self.wallet = wallet
        self.ui = Ui_walletInfoDialog()
        self.ui.setupUi(self)
        self.fill_combos()
        self.setWindowTitle(wallet.name)
        self.ui.derivationEdit.returnPressed.connect(self.updateQrCode)
        self.ui.derivationCombo.currentIndexChanged.connect(self.derivationComboChanged)
        self.ui.derivationCombo.setCurrentIndex(0)
        self.derivationComboChanged()
        self.ui.utxoDerivationCombo.setCurrentIndex(0)
        self.ui.addressRadio.toggled.connect(self.updateQrCode)
        self.ui.keyRadio    .toggled.connect(self.updateQrCode)
        self.ui.xpubRadio   .toggled.connect(self.updateQrCode)
        self.ui.xprvRadio   .toggled.connect(self.updateQrCode)
        utxo_columns_titles = ["confirmations", "amount", "derivation", "address"]
        self.ui.utxoTable.setColumnCount(len(utxo_columns_titles))
        self.ui.utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)
        self.ui.utxoRefreshButton.clicked.connect(self.refresh_utxos)
        self.ui.saveButton.clicked.connect(self.save)

        balance = add_utxos_to_table(wallet.utxos, self.ui.utxoTable)
        self.ui.balanceEdit.setText(str(balance))

    def fill_combos(self):
        # todo: get those from a config file or something
        self.ui.derivationCombo.addItem("Root", "m")
        network = "1" if testnet else "0"
        self.ui.derivationCombo.addItem("Bitcoin core (v0.13.0, 2016-08-23 onward)", "m/0'/0'/0'")
        self.ui.derivationCombo.addItem("Mycelium legacy addresses (2015 onward)", "m/44'/"+network+"'/0'/0/0")
        self.ui.derivationCombo.addItem("Mycelium P2SH addresses (2018 onward)"  , "m/49'/"+network+"'/0'/0/0")
        self.ui.derivationCombo.addItem("Mycelium segwit addresses (2018 onward)", "m/84'/"+network+"'/0'/0/0")
        self.ui.utxoDerivationCombo.addItem("Try everything (slow)", "m, m/x, m/0/x, m/1/x, m/0'/0'/x'")
        self.ui.utxoDerivationCombo.addItem("Root key only", "m")
        self.ui.utxoDerivationCombo.addItem("Simple derivations", "m/x")
        self.ui.utxoDerivationCombo.addItem("Bip44/49/84 Account key", "m/0/x, m/1/x")
        self.ui.utxoDerivationCombo.addItem("Bitcoin core (v0.13.0, 2016-08-23 onward)", "m/0'/0'/x'")

    def derivationComboChanged(self):
        self.ui.derivationEdit.setText(self.ui.derivationCombo.currentData())
        self.updateQrCode()

    def updateQrCode(self):
        derivation = self.ui.derivationEdit.text()
        text = ""
        if self.ui.addressRadio.isChecked():
            text = self.wallet.address(derivation)
        elif self.ui.keyRadio.isChecked():
            text = str(self.wallet.privkey(derivation))
        elif self.ui.xprvRadio.isChecked():
            text = self.wallet.xprv(derivation)
        elif self.ui.xpubRadio.isChecked():
            text = self.wallet.xpub(derivation)
        set_qr_label(self.ui.qrcodeLabel, text)
        self.ui.valueEdit.setText(text)

    def resizeEvent(self, event):
        set_qr_label(self.ui.qrcodeLabel, self.ui.valueEdit.toPlainText())

    def refresh_utxos(self):
        self.ui.utxoTable.setRowCount(0)
        derivation_patterns = [x.strip() for x in self.ui.utxoDerivationCombo.currentData().split(',')]
        balance = 0
        utxos = []
        for derivation_pattern in derivation_patterns:
            if 'x' in derivation_pattern:
                max = 2
                i = 0
                while i < max:
                    derivation = derivation_pattern.replace("x", str(i))
                    address = self.wallet.address(derivation)
                    for utxo in explorer.get_utxos(address, derivation, testnet):
                        utxos.append(utxo)
                        max = i+2
                    i += 1
            else:
                address = self.wallet.address(derivation_pattern)
                for utxo in explorer.get_utxos(address, derivation_pattern, testnet):
                    utxos.append(utxo)
        balance = add_utxos_to_table(utxos, self.ui.utxoTable)
        self.wallet.utxos = utxos
        self.ui.balanceEdit.setText(str(balance))

    def save(self):
        filename = self.wallet.filename
        if filename is None:
            filename = QFileDialog.getSaveFileName(self, 'Save wallet to file', filter="Wallet files(*.wlt);;All files(*)")[0]
            if len(filename) == 0:
                return
        j = json.dumps(self.wallet.to_dict())
        bin = ourCrypto.encrypt(j, b"ourPassword")
        file = open(filename, 'wb')
        file.write(bin)
        self.wallet.filename = filename

def add_utxos_to_table(utxos, utxoTable):
    balance = 0
    current_height = explorer.get_current_height(testnet)
    for utxo in utxos:
        balance += utxo.amount
        add_utxo_to_table(utxo, utxoTable, utxo.metadata.derivation, utxo.metadata.address, current_height)
    return balance

def add_utxo_to_table(utxo, utxoTable, derivation, address, current_height):
    row_idx = utxoTable.rowCount()
    utxoTable.insertRow(row_idx)
    if utxo.parent_tx is None:
        utxo.parent_tx = explorer.get_transaction(utxo.metadata.txid, testnet)
    utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(current_height - utxo.parent_tx.metadata.height)))
    utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
    utxoTable.setItem(row_idx, 2, QTableWidgetItem(derivation))
    utxoTable.setItem(row_idx, 3, QTableWidgetItem(address))

# wise topic three session hint worry auction audit tomorrow noodle will auction

class AddWalletFromWordsDialog(QDialog):
    def __init__(self):
        super(AddWalletFromWordsDialog, self).__init__()
        self.ui = Ui_AddWalletFromWordsDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.wordsPlainTextEdit.textChanged.connect(self.checks)
        self.ui.nameLineEdit      .textChanged.connect(self.checks)
    def checks(self):
        errors = []
        if len(self.ui.nameLineEdit.text()) == 0:
            errors.append("Give it a name")
        words = " ".join(str(self.ui.wordsPlainTextEdit.toPlainText()).split())
        if not bip39.check_phrase(words):
            errors.append("Bad checksum")
        self.ui.warningLabel.setText("; ".join(errors))
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(errors) == 0)
        return len(errors) == 0
    def accept(self):
        if not self.checks():
            return
        words = " ".join(str(self.ui.wordsPlainTextEdit.toPlainText()).split())
        password = str(self.ui.pwLineEdit.text())
        self.wallet = wallets.WordsWallet(self.ui.nameLineEdit.text(), words, password, testnet)
        super(AddWalletFromWordsDialog, self).accept()

class AddWalletFromXprvDialog(QDialog):
    def __init__(self):
        super(AddWalletFromXprvDialog, self).__init__()
        self.ui = Ui_AddWalletFromXprvDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.xprvPlainTextEdit.textChanged.connect(self.checks)
        self.ui.nameLineEdit     .textChanged.connect(self.checks)
    def checks(self):
        errors = []
        if len(self.ui.nameLineEdit.text()) == 0:
            errors.append("Give it a name")
        xkey = self.ui.xprvPlainTextEdit.toPlainText()
        try:
            k = bip32utils.BIP32Key.fromExtendedKey(xkey)
            if k.testnet and not testnet:
                errors.append("Expecting mainnet xprv")
            if not k.testnet and testnet:
                errors.append("Expecting testnet tprv")
            if k.public:
                errors.append("Expecting private key")
        except ValueError as v:
            errors.append(str(v))
        self.ui.warningLabel.setText("; ".join(errors))
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(errors) == 0)
        return len(errors) == 0
    def accept(self):
        if not self.checks():
            return
        self.wallet = wallets.ExtendedKeyWallet(self.ui.nameLineEdit.text(), self.ui.xprvPlainTextEdit.toPlainText())
        super(AddWalletFromXprvDialog, self).accept()

class ChooseUTXOsDialog(QDialog):
    def __init__(self, ws):
        super(ChooseUTXOsDialog, self).__init__()
        self.ui = Ui_ChooseUTXOsDialog()
        self.ui.setupUi(self)
        self.wallets = ws
        self.utxos = []

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["select", "amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)

        current_height = explorer.get_current_height(testnet)
        for wallet in self.wallets.values():
            for utxo in wallet.utxos:
                if utxo.parent_tx is None:
                    utxo.parent_tx = explorer.get_transaction(utxo.metadata.txid, testnet)
                row_idx = utxoTable.rowCount()
                utxoTable.insertRow(row_idx)
                cb = QCheckBox()
                cb.stateChanged.connect(self.calculateSum)
                utxoTable.setCellWidget(row_idx, 0, cb);
                utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
                utxoTable.setItem(row_idx, 2, QTableWidgetItem(wallet.name))
                utxoTable.setItem(row_idx, 3, QTableWidgetItem(str(current_height - utxo.parent_tx.metadata.height)))
                utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.metadata.derivation))
                utxoTable.setItem(row_idx, 5, QTableWidgetItem(utxo.metadata.address))
    def calculateSum(self):
        self.utxos = {}
        utxoTable = self.ui.UTXOsTableWidget
        sum = 0
        for row_idx in range(0,utxoTable.rowCount()):
            if utxoTable.cellWidget(row_idx, 0).isChecked():
                sum += int(utxoTable.item(row_idx, 1).text())
                wallet_name = utxoTable.item(row_idx, 2).text()
                derivation  = utxoTable.item(row_idx, 4).text()
                for utxo in self.wallets[wallet_name].utxos:
                    if utxo.metadata.derivation == derivation:
                        if wallet_name not in self.utxos:
                            self.utxos[wallet_name] = []
                        self.utxos[wallet_name].append(utxo)
                        break
        self.ui.sumLineEdit.setText(str(sum))

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionLoad_from_words.triggered.connect(self.add_wallet_from_words)
        self.ui.actionLoad_from_xprv .triggered.connect(self.add_wallet_from_xprv )
        self.ui.actionOpen           .triggered.connect(self.open_wallet_file     )
        self.wallets_menu = QMenu("Wallets info")
        self.ui.menuWallets.insertMenu(self.ui.actionLoad_from_words, self.wallets_menu)
        self.ui.menuWallets.insertSeparator(self.ui.actionLoad_from_words)
        self.ui.selectUTXOsPushButton.pressed.connect(self.chooseutxos)
        self.current_height = explorer.get_current_height(testnet)

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["Signed", "amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)

        self.wallets = {}

    def open_wallet_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open wallet', filter="Wallet files(*.wlt);;All files(*)")[0]
        if len(filename) == 0:
            return
        file = open(filename, 'rb')
        bin = file.read()
        j = ourCrypto.decrypt(bin, b"ourPassword")
        d = json.loads(j)
        w = wallets.from_dict(d)
        w.filename = filename
        self.wallets[w.name] = w
        menuaction = self.wallets_menu.addAction(w.name)
        menuaction.triggered.connect(lambda:self.menu_action_wallet_name(w.name))

    def add_wallet_from_dialog(self, dialog):
        if dialog.exec():
            w = dialog.wallet
            self.wallets[w.name] = w
            menuaction = self.wallets_menu.addAction(w.name)
            menuaction.triggered.connect(lambda:self.menu_action_wallet_name(w.name))
            dialog = WalletInfoDialog(self.wallets[w.name])
            if dialog.exec():
                pass
            filename = QFileDialog.getSaveFileName(self, 'Save wallet to file', filter="Wallet files(*.wlt);;All files(*)")[0]
            if len(filename) == 0:
                return
            j = json.dumps(w.to_dict())
            bin = ourCrypto.encrypt(j, b"ourPassword")
            file = open(filename, 'wb')
            file.write(bin)
            w.filename = filename

    def add_wallet_from_words(self, event):
        self.add_wallet_from_dialog(AddWalletFromWordsDialog())

    def add_wallet_from_xprv(self, event):
        self.add_wallet_from_dialog(AddWalletFromXprvDialog())

    def menu_action_wallet_name(self, name):
        if name not in self.wallets:
            return
        dialog = WalletInfoDialog(self.wallets[name])
        if dialog.exec():
            pass

    def chooseutxos(self):
        j = json.dumps(util.to_dict(self.wallets))
        dialog = ChooseUTXOsDialog(self.wallets)
        if dialog.exec():
            utxoTable = self.ui.UTXOsTableWidget
            utxoTable.setRowCount(0)
            for wallet_name,utxos in dialog.utxos.items():
                for utxo in utxos:
                    row_idx = utxoTable.rowCount()
                    utxoTable.insertRow(row_idx)
                    cb = QCheckBox()
                    cb.setCheckable(False)
                    utxoTable.setCellWidget(row_idx, 0, cb);
                    utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
                    utxoTable.setItem(row_idx, 2, QTableWidgetItem(wallet_name))
                    utxoTable.setItem(row_idx, 3, QTableWidgetItem(str(self.current_height - utxo.parent_tx.metadata.height)))
                    utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.metadata.derivation))
                    utxoTable.setItem(row_idx, 5, QTableWidgetItem(utxo.metadata.address))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


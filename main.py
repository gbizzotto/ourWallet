
# standard libs imports

import os
import sys
import binascii
from pathlib import Path
from io import BytesIO
import json
from copy import deepcopy
import hashlib
import importlib.util
import random

def auto_import(module_name):
    if importlib.util.find_spec(module_name) is None:
        if auto_import.install == None:
            x = input("Install missing modules? (Y/n)")
            auto_import.install = x in ("y", "Y", "")
        if auto_import.install:
            from pip._internal import main as pipmain
            pipmain(['install', module_name])
    globals()[module_name] = __import__(module_name)
auto_import.install = None

# pip libs imports

auto_import("requests")
auto_import("ecdsa")
auto_import("bech32")
auto_import("PySide6")
auto_import("qrcode")
auto_import("bip39")

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox, QMenu, QTableWidgetItem, QCheckBox, QWidgetAction, QFileDialog, QMessageBox
from PySide6.QtCore import QFile, QIODevice, Qt, QSize, QDateTime, QAbstractTableModel, QModelIndex
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QPalette, QBrush, QColor

# local imports

from ui.mainwindow import Ui_MainWindow
from ui.addwalletfromwordsdialog import Ui_AddWalletFromWordsDialog
from ui.addwalletfromxprvdialog  import Ui_AddWalletFromXprvDialog
from ui.walletinfo import Ui_walletInfoDialog
from ui.chooseutxosdialog import Ui_ChooseUTXOsDialog
from ui.privatekeydialog import Ui_PKeyDialog
from ui.createwordswallet import Ui_CreateWordWalletDialog

import explorer
import transactions
import util
import wallets
import ourCrypto
import scriptVM

# this should be a dependency
import bip32utils
from bip32utils import Base58

testnet = True

def set_qr_label(label, text):
    if text is None or len(text) == 0:
        label.setPixmap(QPixmap())
        return
    buf = BytesIO()
    img = qrcode.make(text)
    img.save(buf, "PNG")
    label.setText("")
    qt_pixmap = QPixmap()
    qt_pixmap.loadFromData(buf.getvalue(), "PNG")
    label.setPixmap(qt_pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio))

def save(wallet, parent_dialog):
    filename = wallet.filename
    if filename is None:
        filename = QFileDialog.getSaveFileName(parent_dialog, 'Save wallet ' + wallet.name + ' to file', filter="Wallet files(*.wlt);;All files(*)")[0]
        if len(filename) == 0:
            return
        if '.' not in filename:
            filename += ".wlt"
    j = json.dumps(wallet.to_dict())
    bin = ourCrypto.encrypt(j, b"ourPassword")
    file = open(filename, 'wb')
    file.write(bin)
    wallet.filename = filename
    wallet.dirty    = False

class WalletInfoDialog(QDialog):
    def __init__(self, wallet):
        super(WalletInfoDialog, self).__init__()
        self.wallet = wallet
        self.ui = Ui_walletInfoDialog()
        self.ui.setupUi(self)
        self.setWindowTitle(wallet.name)

        # todo: get those from a config file or something

        network = "1" if testnet else "0"
        words_wallet_schemes = \
            {
                "Legacy":        ["m/44'/"+network+"'/0'/0/x", "m/44'/"+network+"'/0'/1/x", 0],
                "Compatibility": ["m/49'/"+network+"'/0'/0/x", "m/49'/"+network+"'/0'/1/x", 1],
                "Segwit":        ["m/84'/"+network+"'/0'/0/x", "m/84'/"+network+"'/0'/1/x", 2]
            }
        self.schemes = {
            "Bitcoin core (v0.13.0, 2016-08-23 onward)":
                {"Legacy": ["m/0'/0'/0'", "m/0'/0'/0'", 0]},
            "12 words from ourWallet, Mycelium, Samourai, Coinomi or bitcoin.com":
                words_wallet_schemes,
            "12 words from Mycelium, Samourai or Coinomi":
                words_wallet_schemes,
            "12 words from bitcoin.com":
                words_wallet_schemes,
            "xprv from Mycelium, Samourai, Coinomi or bitcoin.com": {"Legacy":        ["m/0/x", "m/1/x", 0]},
            "yprv from Mycelium, Samourai, Coinomi or bitcoin.com": {"Compatibility": ["m/0/x", "m/1/x", 1]},
            "zprv from Mycelium, Samourai, Coinomi or bitcoin.com": {"Segwit":        ["m/0/x", "m/1/x", 2]},
            }
        self.ui.whereFromComboBox.addItem("")
        for k in self.schemes.keys():
            self.ui.whereFromComboBox.addItem(k)
        self.ui.whereFromComboBox.currentIndexChanged.connect(self.whereFromComboBoxChanged)

        self.ui.derivationSchemeComboBox.currentIndexChanged.connect(self.derivationSchemeChanged)

        self.ui.showMoreButton.clicked.connect(self.show_addresses)

        self.ui.addressTypeComboBox.addItem('Legacy', wallets.LEGACY)
        self.ui.addressTypeComboBox.addItem('Segwit-legacy compatibility', wallets.COMPATIBILITY)
        self.ui.addressTypeComboBox.addItem('Bech32/segwit', wallets.SEGWIT)
        self.ui.addressTypeComboBox.setCurrentIndex({wallets.LEGACY:0,wallets.COMPATIBILITY:1,wallets.SEGWIT:2}[self.wallet.address_type])
        self.ui.addressTypeComboBox.currentIndexChanged.connect(self.addressTypeComboChanged)

        addresses_columns_titles = ["Derivation", "Address", "Private key (WIF)"]
        self.ui.addressTableWidget.setColumnCount(len(addresses_columns_titles))
        self.ui.addressTableWidget.setHorizontalHeaderLabels(addresses_columns_titles)
        self.ui.addressTableWidget.resizeColumnsToContents()
        self.ui.addressTableWidget.itemSelectionChanged.connect(self.address_selection_changed)

        utxo_columns_titles = ["confirmations", "amount", "derivation", "address"]
        self.ui.utxoTable.setColumnCount(len(utxo_columns_titles))
        self.ui.utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)
        self.ui.utxoRefreshButton.clicked.connect(self.refresh_utxos)
        self.ui.       saveButton.clicked.connect(self.save)

        self.ui.addressDerivationEdit.setText(self.wallet.address_derivation)
        self.ui. changeDerivationEdit.setText(self.wallet. change_derivation)

        self.ui.addressDerivationEdit.textChanged.connect(self.addressDerivationEditChanged)
        self.ui. changeDerivationEdit.textChanged.connect(self. changeDerivationEditChanged)

        self.display_utxos(wallet.utxos)

    def resizeEvent(self, event):
        self.address_selection_changed()

    def derivationSchemeChanged(self):
        if len(self.ui.whereFromComboBox.currentText()) == 0 or len(self.ui.derivationSchemeComboBox.currentText()) == 0:
            return
        self.ui.addressDerivationEdit.setText      (self.schemes[self.ui.whereFromComboBox.currentText()][self.ui.derivationSchemeComboBox.currentText()][0])
        self.ui. changeDerivationEdit.setText      (self.schemes[self.ui.whereFromComboBox.currentText()][self.ui.derivationSchemeComboBox.currentText()][1])
        self.ui.addressTypeComboBox.setCurrentIndex(self.schemes[self.ui.whereFromComboBox.currentText()][self.ui.derivationSchemeComboBox.currentText()][2])

    def whereFromComboBoxChanged(self):
        if len(self.ui.whereFromComboBox.currentText()) == 0:
            return
        schemes = self.schemes[self.ui.whereFromComboBox.currentText()]
        self.ui.derivationSchemeComboBox.clear()
        for k in schemes.keys():
            self.ui.derivationSchemeComboBox.addItem(k)

    def address_selection_changed(self):
        table = self.ui.addressTableWidget

        if table.currentItem() is None or len(table.currentItem().text()) == 0:
            set_qr_label(self.ui.qrcodeLabel, "")
        else:
            set_qr_label(self.ui.qrcodeLabel, table.currentItem().text())

    def clear_address_table(self):
        self.ui.addressTableWidget.setRowCount(0)

    def show_addresses(self):
        table = self.ui.addressTableWidget
        show_wif = self.ui.showWIFCheckBox.isChecked()
        show_change = self.ui.showChangeCheckBox.isChecked()
        from_ = int(self.ui.fromEdit.text())
        to_   = int(self.ui.  toEdit.text())
        table.setRowCount(0)
        derivation_pattern = self.wallet.change_derivation if show_change else self.wallet.address_derivation
        for i in range(from_, to_+1):
            derivation = derivation_pattern.replace("x", str(i))
            address = self.wallet.address(derivation)
            row_idx = table.rowCount()
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QTableWidgetItem(derivation))
            table.setItem(row_idx, 1, QTableWidgetItem(address))
            if show_wif:
                wif = self.wallet.privkey_wif(derivation)
                table.setItem(row_idx, 2, QTableWidgetItem(wif))
        table.resizeColumnsToContents()

    def addressDerivationEditChanged(self):
        self.wallet.address_derivation = self.ui.addressDerivationEdit.text()
        self.wallet.dirty = True

    def changeDerivationEditChanged(self):
        self.wallet.change_derivation = self.ui.changeDerivationEdit.text()
        self.wallet.dirty = True

    def addressTypeComboChanged(self):
        self.wallet.address_type = int(self.ui.addressTypeComboBox.currentData())
        self.wallet.dirty = True
        self.ui.addressTableWidget.setRowCount(0)

    def display_utxos(self, utxos):
        current_height = explorer.get_current_height(testnet)
        utxoTable = self.ui.utxoTable
        utxoTable.setRowCount(0)
        balance = 0
        for utxo in utxos:
            balance += utxo.amount
            row_idx = utxoTable.rowCount()
            utxoTable.insertRow(row_idx)
            if utxo.parent_tx is None:
                utxo.parent_tx = explorer.get_transaction(utxo.metadata.txid, testnet)
            if utxo.parent_tx.metadata and utxo.parent_tx.metadata.height:
                utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(1 + current_height - utxo.parent_tx.metadata.height)))
            else:
                utxoTable.setItem(row_idx, 0, QTableWidgetItem("Unconfirmed"))
            utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
            utxoTable.setItem(row_idx, 2, QTableWidgetItem(utxo.metadata.derivation))
            utxoTable.setItem(row_idx, 3, QTableWidgetItem(utxo.metadata.address))
        self.ui.balanceEdit.setText(str(balance))

    def updateQrCode(self):
        derivation = self.ui.derivationEdit.text()
        text = ""
        if self.ui.addressRadio.isChecked():
            text = self.wallet.address(derivation)
        elif self.ui.keyRadio.isChecked():
            text = str(self.wallet.privkey_wif(derivation))
        elif self.ui.xprvRadio.isChecked():
            text = self.wallet.xprv(derivation)
        elif self.ui.xpubRadio.isChecked():
            text = self.wallet.xpub(derivation)
        set_qr_label(self.ui.qrcodeLabel, text)
        self.ui.valueEdit.setText(text)

    def refresh_utxos(self):
        changed = False
        for derivation_pattern in (self.wallet.address_derivation, self.wallet.change_derivation):
            if 'x' in derivation_pattern:
                max = 10
                i = 0
                while i < max:
                    derivation = derivation_pattern.replace("x", str(i))
                    address = self.wallet.address(derivation)
                    utxos = explorer.get_utxos(self.wallet.name, address, derivation, testnet)
                    if len(utxos) == 0:
                        changed = self.wallet.remove_utxos_by_address(address) or changed
                    else:
                        for utxo in utxos:
                            if utxo.metadata.spent:
                                changed = self.wallet.remove_utxo(utxo) or changed
                            else:
                                changed = self.wallet.add_utxo(utxo) or changed
                            max = i+10
                    i += 1
            else:
                address = self.wallet.address(derivation_pattern)
                for utxo in explorer.get_utxos(self.wallet.name, address, derivation_pattern, testnet):
                    changed = changed or self.wallet.add_utxo(utxo)
        if changed:
            self.wallet.dirty = True
            self.display_utxos(self.wallet.utxos)

    def save(self):
        save(self.wallet, self)

class CreateWordWalletDialog(QDialog):
    def __init__(self):
        super(CreateWordWalletDialog, self).__init__()
        self.ui = Ui_CreateWordWalletDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.wordsPlainTextEdit.textChanged.connect(self.checks)
        self.ui.nameLineEdit      .textChanged.connect(self.checks)
        self.ui.generatePushButton.clicked.connect(self.generate_passphrase)
    def generate_passphrase(self):
        entropy = random.randint(1<<120, 1<<128-1)
        entropy_bytes = util.int_to_bytes(entropy)
        cs = (hashlib.sha256(entropy_bytes).digest()[0] & 0xF0) >> 4
        entropy = (entropy << 4) | cs
        with open("english.txt", "r") as f:
            words = f.read().split()
        phrase = []
        for i in range(0,12):
            phrase.append(words[entropy & 0x7FF])
            entropy >>= 11
        assert entropy == 0
        self.ui.wordsPlainTextEdit.document().setPlainText(" ".join(phrase[::-1]))
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
        testnet_str = "1" if testnet else "0"
        self.wallet = wallets.WordsWallet(self.ui.nameLineEdit.text(), words, password, testnet, "m/84'/"+testnet_str+"'/0'/0/x", "m/84'/"+testnet_str+"'/0'/0/x", wallets.SEGWIT)
        super(CreateWordWalletDialog, self).accept()

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
        testnet_str = "1" if testnet else "0"
        self.wallet = wallets.WordsWallet(self.ui.nameLineEdit.text(), words, password, testnet, "m/84'/"+testnet_str+"'/0'/0/x", "m/84'/"+testnet_str+"'/0'/0/x", wallets.SEGWIT)
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

class PKeyDialog(QDialog):
    def __init__(self, transaction, vin):
        super(PKeyDialog, self).__init__()
        self.ui = Ui_PKeyDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.pkLineEdit.textChanged.connect(self.checks)
        self.key = None

        current_height = explorer.get_current_height(testnet)

        outpoint_str = transaction.inputs[vin].txoutput.metadata.txid.hex() + ":" + str(transaction.inputs[vin].txoutput.metadata.vout)
        height = 1 + current_height - transaction.inputs[vin].txoutput.parent_tx.metadata.height
        script_type = scriptVM.identify_scriptpubkey(transaction.inputs[vin].txoutput.scriptpubkey)
        if script_type == scriptVM.P2PK:
            script_type_str = "P2PK"
        elif script_type == scriptVM.P2SH:
            script_type_str = "P2SH"
        elif script_type == scriptVM.P2MS:
            script_type_str = "P2MS"
        elif script_type == scriptVM.P2PKH:
            script_type_str = "P2PKH"
        elif script_type == scriptVM.P2WPKH:
            script_type_str = "P2WPKH"
        elif script_type == scriptVM.P2WSH:
            script_type_str = "P2WSH"
        elif script_type == scriptVM.P2TR:
            script_type_str = "P2TR"
        else:
            script_type_str = "UNKNOWN YET"

        self.ui.     outpointLabel.setText(outpoint_str)
        self.ui.confirmationsLabel.setText(str(height))
        self.ui.   scriptTypeLabel.setText(script_type_str)
        self.ui.          vinLabel.setText(str(vin))
        self.ui.       amountLabel.setText(str(transaction.inputs[vin].txoutput.amount))
    def checks(self):
        errors = []
        if len(self.ui.pkLineEdit.text()) == 0:
            self.key = None
            self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.ui.warningLabel.setText("")
            return
        pk_text = self.ui.pkLineEdit.text()
        try:
            pk = Base58.check_decode(pk_text)
            if (pk[0] == 0x80 and testnet):
                errors.append("Key not for testnet")
            elif (pk[0] == 0xef and not testnet):
                errors.append("Key not for mainnet")
            self.key = pk[1:-1]
        except:
            try:
                pk = binascii.unhexlify(pk_text)
                sk = ecdsa.SigningKey.from_string(pk[1:-1], curve=ecdsa.SECP256k1)
                self.pk = pk
            except:
                errors.append("Bad format")

        self.ui.warningLabel.setText("; ".join(errors))
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(errors) == 0)
        return len(errors) == 0
    def accept(self):
        if not self.checks():
            return
        super(PKeyDialog, self).accept()

class ChooseUTXOsDialog(QDialog):
    def __init__(self, ws):
        super(ChooseUTXOsDialog, self).__init__()
        self.ui = Ui_ChooseUTXOsDialog()
        self.ui.setupUi(self)
        self.wallets = ws
        self.known_utxos = []
        self. w_utxos = []
        self.ff_utxos = []

        self.ui.ffDLDataButton.clicked.connect(self.add_free_floating)
        self.accepted.connect(self.dialog_accepted)

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)
        utxoTable.itemSelectionChanged.connect(self.selection_changed)

        ffutxoTable = self.ui.ffUTXOsTableWidget
        ffutxo_columns_titles = ["amount", "confirmations"]
        ffutxoTable.setColumnCount(len(ffutxo_columns_titles))
        ffutxoTable.setHorizontalHeaderLabels(ffutxo_columns_titles)

        self.ui.walletComboBox.addItem("All")
        for wallet in self.wallets.values():
            self.ui.walletComboBox.addItem(wallet.name)

        self.ui.walletComboBox.currentIndexChanged.connect(self.wallet_changed)
        self.populate_utxos()

    def populate_utxos(self):
        self.ui.UTXOsTableWidget.setRowCount(0)
        if self.ui.walletComboBox.currentIndex() == 0:
            for wallet in self.wallets.values():
                self.populate_utxos_with_wallet(wallet)
        else:
            self.populate_utxos_with_wallet(self.wallets[self.ui.walletComboBox.currentText()])

    def populate_utxos_with_wallet(self, wallet):
        utxoTable = self.ui.UTXOsTableWidget
        current_height = explorer.get_current_height(testnet)
        for utxo in wallet.utxos:
            if utxo.parent_tx is None:
                utxo.parent_tx = explorer.get_transaction(utxo.metadata.txid, testnet)
            self.known_utxos.append(utxo)
            row_idx = utxoTable.rowCount()
            utxoTable.insertRow(row_idx)
            utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(utxo.amount)))
            utxoTable.setItem(row_idx, 1, QTableWidgetItem(wallet.name))
            if utxo.parent_tx.metadata.height:
                utxoTable.setItem(row_idx, 2, QTableWidgetItem(str(1 + current_height - utxo.parent_tx.metadata.height)))
            else:
                utxoTable.setItem(row_idx, 2, QTableWidgetItem("Unconfirmed"))
            utxoTable.setItem(row_idx, 3, QTableWidgetItem(utxo.metadata.derivation))
            utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.metadata.address))

    def wallet_changed(self):
        self.populate_utxos()

    def dialog_accepted(self):
        if self.ui.tabWidget.currentIndex() == 0:
            self.utxos = self.w_utxos
        elif self.ui.tabWidget.currentIndex() == 1:
            self.utxos = self.ff_utxos

    def selection_changed(self):
        utxoTable = self.ui.UTXOsTableWidget
        selected_indexes = list(set([qmi.row() for qmi in self.ui.UTXOsTableWidget.selectedIndexes()]))
        self.ui.sumLineEdit.setText(str(sum([int(utxoTable.item(row_idx, 0).text()) for row_idx in selected_indexes])))
        self.w_utxos = [self.known_utxos[row_idx] for row_idx in selected_indexes]

    def add_free_floating(self):
        txid_hex = self.ui.ffTxidEdit.text()
        vout = int(self.ui.ffVoutEdit.text())

        utxo = explorer.get_utxo(txid_hex, vout, testnet)
        if utxo is None:
            return

        utxoTable = self.ui.ffUTXOsTableWidget

        for i,u in enumerate(self.ff_utxos):
            if u.metadata.txid == utxo.metadata.txid and u.metadata.vout == utxo.metadata.vout:
                del self.ff_utxos[i]
                utxoTable.removeRow(i)
                break

        self.ff_utxos.append(utxo)
        row_idx = utxoTable.rowCount()
        utxoTable.insertRow(row_idx)
        utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(utxo.amount)))
        if utxo.parent_tx.metadata.height:
            current_height = explorer.get_current_height(testnet)
            utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(1 + current_height - utxo.parent_tx.metadata.height)))
        else:
            utxoTable.setItem(row_idx, 1, QTableWidgetItem("Unconfirmed"))


class InputsTableModel(QAbstractTableModel):
    def __init__(self, inputs):
        QAbstractTableModel.__init__(self)
        self.inputs = inputs
        self.columns = ["signed", "sequence", "amount", "wallet", "confirmations", "derivation", "address"]

    def set_selected(self, selected_rows_set):
        self.all_rows_affected = False
        for input in self.inputs:
            if scriptVM.contains_anyonecanpay_sighash(input.scriptsig):
                self.all_rows_affected = True
                break

    def rowCount(self, parent=QModelIndex()):
        return len(self.inputs)
    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)
    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.columns[section]
        else:
            return "{}".format(section)
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role != Qt.EditRole:
            return False
        row = index.row()
        if row < 0 or row >= len(self.inputs):
            return False
        column = index.column()
        if column != 1:
            return False
        self.inputs[row].sequence = int(value)
        self.dataChanged.emit(index, index)
        return True
    def flags(self, index):
        f = super(self.__class__,self).flags(index)
        f |= Qt.ItemIsSelectable
        f |= Qt.ItemIsEnabled
        if index.column() == 1:
            f |= Qt.ItemIsEditable
        return f
    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row    = index.row()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            input = self.inputs[row]
            if column == 0:
                verification = input.parent_tx.verify(row)
                if verification is None:
                    return ""
                elif verification == True:
                    return "Yes"
                else:
                    return "ERROR"
            elif column == 1:
                return "{}".format(input.sequence)
            elif column == 2:
                return "{}".format(input.txoutput.amount)
            elif column == 3:
                if input.txoutput and input.txoutput.metadata and input.txoutput.metadata.wallet_name:
                    return input.txoutput.metadata.wallet_name
                else:
                    return ""
            elif column == 4:
                if input.txoutput and input.txoutput.parent_tx.metadata and input.txoutput.parent_tx.metadata.height:
                    current_height = explorer.get_current_height(testnet)
                    return "{}".format(1 + current_height - input.txoutput.parent_tx.metadata.height)
                else:
                    return "Unconfirmed"
            elif column == 5:
                if input.txoutput and input.txoutput.metadata and input.txoutput.metadata.derivation:
                    return "{}".format(input.txoutput.metadata.derivation)
                else:
                    return ""
            elif column == 6:
                if input.txoutput and input.txoutput.metadata and input.txoutput.metadata.address:
                    return input.txoutput.metadata.address
                else:
                    return ""
        elif role == Qt.BackgroundRole:
            if column == 1:
                return QColor.fromRgb(255,255,255)
            return QColor.fromRgb(245,245,245)
        elif role == Qt.TextAlignmentRole:
            if column in [1,2,4]:
                return int(Qt.AlignVCenter | Qt.AlignRight)
            elif column == 0:
                return int(Qt.AlignVCenter | Qt.AlignCenter)
            else:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionLoad_from_words.triggered.connect(self.add_wallet_from_words)
        self.ui.actionLoad_from_xprv .triggered.connect(self.add_wallet_from_xprv )
        self.ui.actionNew_HD         .triggered.connect(self.create_words_wallet  )
        self.ui.actionOpen           .triggered.connect(self.open_wallet_file     )
        self.ui.   addInputsPushButton.clicked.connect(self.add_inputs   )
        self.ui.    removeInputsButton.clicked.connect(self.del_inputs   )
        self.ui.   addOutputPushButton.clicked.connect(self.add_output   )
        self.ui.removeOutputPushButton.clicked.connect(self.del_output   )
        self.ui.     signAllPUshButton.clicked.connect(self.sign_all_mine)
        self.ui.         signOneButton.clicked.connect(lambda: self.sign_selected(transactions.SIGHASH_ALL))
        self.ui.      verifyPushButton.clicked.connect(self.verify       )
        self.ui.      exportPushButton.clicked.connect(self.export       )
        self.ui.   broadcastPushButton.clicked.connect(self.broadcast    )
        self.ui.           clearButton.clicked.connect(self.clear        )
        self.ui.PreventFeeSnipingCheckBox.toggled.connect(self.prevent_fee_sniping_toggled)
        self.ui.locktimeLineEdit.textChanged.connect(self.locktime_changed)
        self.ui.dateTimeEdit.dateTimeChanged.connect(self.locktime_datetime_changed)
        self.propagate_locktime_change = True

        self.ui.broadcastPushButton.setEnabled(False)

        outputsTable = self.ui.outputsTableWidget
        outputs_columns_titles = ["Amount", "Address", "ScriptPubKey type"]
        outputsTable.setColumnCount(len(outputs_columns_titles))
        outputsTable.setHorizontalHeaderLabels(outputs_columns_titles)

        outputsTable.cellChanged.connect(self.output_changed)

        self.wallets = {}
        self.transaction = transactions.Transaction()

        self.inputs_view_model = InputsTableModel(self.transaction.inputs)
        self.ui.inputsView.setModel(self.inputs_view_model)
        self.ui.inputsView.clicked.connect(self.selected_inputs_changed)

        #unix_time = int(QDateTime.currentDateTime().toMSecsSinceEpoch()/1000)
        self.transaction.locktime = 0
        self.ui.locktimeLineEdit.setText(str("0"))

        self.transaction_fee = 0
        self.transaction_virtual_size = 0

        m = QMenu(self)
        a = m.addAction("with SIGHASH_ALL (inputs locked, outputs locked: standard)")
        a.triggered.connect(lambda: self.sign_selected(transactions.SIGHASH_ALL))
        a = m.addAction("with SIGHASH_NONE (inputs locked, ouptuts not mine: blank check)")
        a.triggered.connect(lambda: self.sign_selected(transactions.SIGHASH_NONE))
        a = m.addAction("with SIGHASH_SINGLE (inputs locked, one output mine others open)")
        a.triggered.connect(lambda: self.sign_selected(transactions.SIGHASH_SINGLE))
        a = m.addAction("with ANYONECANPAY and SIGHASH_ALL, (inputs open, outputs locked: crowdfunding)")
        a.triggered.connect(lambda: self.sign_selected(transactions.SIGHASH_ALL    | transactions.SIGHASH_ANYONECANPAY))
        a = m.addAction("with ANYONECANPAY and SIGHASH_NONE, (inputs open, outputs not mine: blank check)")
        a.triggered.connect(lambda: self.sign_selected(transactions.SIGHASH_NONE   | transactions.SIGHASH_ANYONECANPAY))
        a = m.addAction("with ANYONECANPAY and SIGHASH_ONE, (inputs open, one output mine: coin mixing)")
        a.triggered.connect(lambda: self.sign_selected(transactions.SIGHASH_SINGLE | transactions.SIGHASH_ANYONECANPAY))
        self.ui.signOneButton.setMenu(m)

    def selected_inputs_changed(self, index):
        selected_indexes = set([x.row() for x in self.ui.inputsView.selectedIndexes()])
        self.inputs_view_model.set_selected(selected_indexes)

    def locktime_datetime_changed(self):
        if self.propagate_locktime_change == False:
            return

        unix_time = int(self.ui.dateTimeEdit.dateTime().toMSecsSinceEpoch()/1000)
        if unix_time <= 500000000:
            print("Bad dateTime")
            return
        self.transaction.locktime = unix_time
        self.propagate_locktime_change = False
        self.ui.locktimeLineEdit.setText(str(unix_time))
        self.propagate_locktime_change = True

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()

    def locktime_changed(self):
        if self.propagate_locktime_change == False:
            return
        if len(self.ui.locktimeLineEdit.text()) == 0:
            return

        value = int(self.ui.locktimeLineEdit.text())
        self.transaction.locktime = value

        if value < 500000000:
            current_height = explorer.get_current_height(testnet)
            blocks_from_now = value - current_height
            if testnet:
                # testnet seems to go way faster than mainnet. this is an attempt to correction
                blocks_from_now = int(blocks_from_now / 3.752)
            unix_time = int(QDateTime.currentDateTime().toMSecsSinceEpoch()/1000)
            unix_time += blocks_from_now * 10 * 60
        else:
            unix_time = value

        date_time = QDateTime();
        date_time.setMSecsSinceEpoch(unix_time*1000);

        self.propagate_locktime_change = False
        self.ui.dateTimeEdit.setDateTime(date_time)
        self.propagate_locktime_change = True

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()

    def prevent_fee_sniping_toggled(self):
        checked = self.ui.PreventFeeSnipingCheckBox.isChecked()
        self.ui.dateTimeEdit.setEnabled(not checked)
        self.ui.locktimeLineEdit.setEnabled(not checked)

        if checked:
            self.transaction.locktime = explorer.get_current_height(testnet)
            #self.ui.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        else:
            self.transaction.locktime = int(self.ui.locktimeLineEdit.text())

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()

    def closeEvent(self,event):
        msg = []
        for w in self.wallets.values():
            if w.dirty or w.filename is None:
                msg.append(w.name + " needs Jesus, save it?")

        if len(msg) == 0:
            event.accept()
            return
        action = QMessageBox.question(self, "Save?", '\n'.join(msg), QMessageBox.Yes| QMessageBox.No| QMessageBox.Cancel)
        if action == QMessageBox.Yes:
            for w in self.wallets.values():
                if w.dirty or w.filename is None:
                    save(w, self)
        if action == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def export(self):
        print("serialized transaction", self.transaction.to_bin().hex())

    def verify_one(self, vin):
        verification = self.transaction.verify(vin)
        if verification is None:
            #msg = ""
            good = False
        elif verification == True:
            #msg = "Yes"
            good = True
        else:
            #msg = "ERROR"
            good = False
        return good

    def verify_all(self):
        saul_goodman = True
        for vin in range(0, len(self.transaction.inputs)):
            saul_goodman = saul_goodman & self.verify_one(vin)
        return saul_goodman

    def verify(self):
        if self.verify_all():
            self.ui.broadcastPushButton.setEnabled(True)

    def sign_selected(self, sighash_type):
        selected_indexes = set([x.row() for x in self.ui.inputsView.selectedIndexes()])
        for vin in selected_indexes:
            if False == self.transaction.sign_one(sighash_type, vin, wallets=self.wallets):
                dialog = PKeyDialog(self.transaction, vin)
                if dialog.exec():
                    self.transaction.sign_one(sighash_type, vin, private_key=dialog.key)
                else:
                    print("No key for input")

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_size()

    def sign_all_mine(self):
        self.transaction.sign_all(self.wallets, transactions.SIGHASH_ALL)
        #self.verify_all()
        self.update_inputs_view()
        self.update_size()

    def output_changed(self, row, col):
        outputsTable = self.ui.outputsTableWidget
        if col == 0:
            # change Amount
            sum = 0
            for row_idx in range(0, outputsTable.rowCount()):
                try:
                    v = int(outputsTable.item(row_idx, 0).text())
                    sum += v
                    self.transaction.outputs[row_idx].amount = v
                except:
                    #widget = outputsTable.cellWidget(row_idx, 0)
                    #widget.setBackgroundRole(QPalette.highlight())
                    pass
            self.ui.outputSumEdit.setText(str(sum))
            self.update_fee()
        elif col == 1:
            # change address
            address = outputsTable.item(row, col).text()
            try:
                self.transaction.outputs[row].scriptpubkey = bytearray()
                if len(address) == 0:
                    scheme = ""
                elif scriptVM.address_is_testnet(address) and not testnet:
                    scheme = "ERROR: address is testnet, network is mainnet"
                elif scriptVM.address_is_mainnet(address) and testnet:
                    scheme = "ERROR: address is mainnet, network is testnet"
                else:
                    address_type = scriptVM.address_type(address)
                    if address_type == scriptVM.P2PKH:
                        scheme = "P2PKH"
                        bin_address = Base58.check_decode(address)[1:]
                        self.transaction.outputs[row].scriptpubkey = scriptVM.make_P2PKH_scriptpubkey(bin_address)
                    elif address_type == scriptVM.P2SH:
                        scheme = "P2SH"
                        # TODO
                    elif address_type == scriptVM.P2MS:
                        scheme = "P2MS"
                        # TODO
                    elif address_type == scriptVM.P2WPKH:
                        scheme = "P2WPKH"
                        bin_address = bytes(bech32.decode('tb' if testnet else 'bc', address)[1])
                        self.transaction.outputs[row].scriptpubkey = scriptVM.make_P2PWPKH_scriptpubkey(bin_address)
                    elif address_type == scriptVM.P2WSH:
                        scheme = "P2WSH"
                        # TODO
                    elif address_type == scriptVM.P2TR:
                        scheme = "P2TR"
                        # TODO
                    else:
                        scheme = "ERROR: unknown address type"
            except ValueError as e:
                scheme = "Bad base58 checksum"
            outputsTable.setItem(row, 2, QTableWidgetItem(scheme))
        else:
            return
        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_size()

    def add_output(self):
        outputTable = self.ui.outputsTableWidget
        outputTable.insertRow(outputTable.rowCount())
        self.transaction.outputs.append(transactions.TxOutput())
        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_size()

    def del_output(self):
        outputsTable = self.ui.outputsTableWidget
        selected_indexes = list(set([qmi.row() for qmi in outputsTable.selectedIndexes()]))
        selected_indexes.sort()
        for idx in selected_indexes[::-1]:
            outputsTable.removeRow(idx)
            del self.transaction.outputs[idx]

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_fee()
        self.update_size()


    def update_inputs_view(self):
        self.ui.inputsView.setModel(None)
        self.ui.inputsView.setModel(self.inputs_view_model)
        self.ui.inputsView.resizeColumnsToContents()


    def add_inputs(self):
        j = json.dumps(util.to_dict(self.wallets))
        dialog = ChooseUTXOsDialog(self.wallets)
        if not dialog.exec():
            return
        current_height = explorer.get_current_height(testnet)
        for utxo in dialog.utxos:
            if self.transaction.has(utxo):
                continue
            vin = self.transaction.add(utxo)

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_fee()
        self.update_size()

    def del_inputs(self):
        selected_indexes = list(set([x.row() for x in self.ui.inputsView.selectedIndexes()]))
        for idx in selected_indexes[::-1]:
            del self.transaction.inputs[idx]

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_fee()
        self.update_size()

    def update_fee(self):
        input_total = sum([input.txoutput.amount for input in self.transaction.inputs])
        output_total = sum([out.amount for out in self.transaction.outputs])
        self.transaction_fee = input_total - output_total
        self.ui.inputSumEdit.setText(str(input_total))
        self.ui.outputSumEdit.setText(str(output_total))
        self.ui.feeEdit.setText(str(self.transaction_fee))
        self.update_fee_per_byte()

    def update_size(self):
        self.transaction_size, self.transaction_virtual_size = self.transaction.get_approximate_size()
        self.ui.transactionSizeEdit.setText(str(self.transaction_size))
        self.ui.transactionVSizeEdit.setText(str(self.transaction_virtual_size))
        self.update_fee_per_byte()

    def update_fee_per_byte(self):
        if self.transaction_virtual_size == 0:
            self.ui.feePerByteEdit.setText("")
            return
        fee_per_byte = self.transaction_fee / self.transaction_virtual_size
        self.ui.feePerByteEdit.setText(str(fee_per_byte))

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
        menuaction = self.ui.menuWallets.addAction(w.name)
        menuaction.triggered.connect(lambda:self.menu_action_wallet_name(w.name))

    def add_wallet_from_dialog(self, dialog):
        if dialog.exec():
            w = dialog.wallet
            self.wallets[w.name] = w
            menuaction = self.ui.menuWallets.addAction(w.name)
            menuaction.triggered.connect(lambda:self.menu_action_wallet_name(w.name))
            dialog = WalletInfoDialog(self.wallets[w.name])
            if dialog.exec():
                pass

    def add_wallet_from_words(self, event):
        self.add_wallet_from_dialog(AddWalletFromWordsDialog())
    def add_wallet_from_xprv(self, event):
        self.add_wallet_from_dialog(AddWalletFromXprvDialog())
    def create_words_wallet(self):
        self.add_wallet_from_dialog(CreateWordWalletDialog())

    def menu_action_wallet_name(self, name):
        if name not in self.wallets:
            return
        dialog = WalletInfoDialog(self.wallets[name])
        if dialog.exec():
            pass

    def broadcast(self):
        txid_hex = explorer.go_push_transaction(self.transaction, testnet)
        if txid_hex is not None:
            print("Broadcast OK", txid_hex)

    def clear(self):
        self.transaction = transactions.Transaction()
        self.inputs_view_model = InputsTableModel(self.transaction.inputs)

        self.ui.outputsTableWidget.setRowCount(0)
        self.update_inputs_view()
        self.update_fee()
        self.update_size()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


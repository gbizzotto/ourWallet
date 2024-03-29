
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

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox, QMenu, QTableWidgetItem, QCheckBox, QWidgetAction, QFileDialog, QMessageBox, QAbstractItemView, QProgressDialog
from PySide6.QtCore import QFile, QIODevice, Qt, QSize, QDateTime, QAbstractTableModel, QModelIndex, QItemSelectionModel, SIGNAL
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
from ui.passworddialog import Ui_passwordDialog

import explorer
import transactions
import util
import wallets
import ourCrypto
import scriptVM

# this should be a dependency
import bip32utils
from bip32utils import Base58

testnet = False

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

    pw = b""
    dialog = PasswordDialog(parent_dialog)
    if dialog.exec():
        pw = str.encode(dialog.pw)
    if hasattr(wallet, 'pwCheck') and wallet.pwCheck:
        if ourCrypto.decrypt(wallet.pwCheck, pw) != "ourPassword":
            QMessageBox.warning(parent_dialog, "Wrong password", "Wrong password")
            return

    j = json.dumps(wallet.to_dict())
    bin = ourCrypto.encrypt(j, pw)
    file = open(filename, 'wb')
    file.write(bin)
    wallet.filename = filename
    wallet.dirty    = False

class PasswordDialog(QDialog):
    def __init__(self, wallet):
        super(self.__class__, self).__init__()
        self.wallet = wallet
        self.ui = Ui_passwordDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Password")
    def accept(self):
        self.pw = self.ui.passwordEdit.text()
        super(self.__class__, self).accept()

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
        self.ui.refreshSelectedAddressButton.clicked.connect(self.refresh_selected_utxos)

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

        utxo_columns_titles = ["Spent", "confirmations", "amount", "derivation", "address"]
        self.ui.utxoTable.setColumnCount(len(utxo_columns_titles))
        self.ui.utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)
        self.ui.utxoRefreshButton.clicked.connect(self.refresh_utxos)
        self.ui.       saveButton.clicked.connect(self.save)

        self.ui.addressDerivationEdit.setText(self.wallet.address_derivation)
        self.ui. changeDerivationEdit.setText(self.wallet. change_derivation)

        self.ui.addressDerivationEdit.textChanged.connect(self.addressDerivationEditChanged)
        self.ui. changeDerivationEdit.textChanged.connect(self. changeDerivationEditChanged)

        self.current_height = explorer.get_current_height(testnet)
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
        utxoTable = self.ui.utxoTable
        utxoTable.setRowCount(0)
        total_in = 0
        total_out = 0
        for utxo in utxos:
            if utxo.metadata.spent:
                total_out += utxo.amount
            total_in += utxo.amount
            row_idx = utxoTable.rowCount()
            utxoTable.insertRow(row_idx)
            if utxo.parent_tx is None or utxo.parent_tx.metadata is None: # or utxo.parent_tx.metadata.height is None:
                utxo.parent_tx = explorer.get_transaction(utxo.metadata.txid, testnet)
            utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(utxo.metadata.spent)))
            if utxo.parent_tx.metadata and utxo.parent_tx.metadata.height:
                utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(1 + self.current_height - utxo.parent_tx.metadata.height)))
            else:
                utxoTable.setItem(row_idx, 1, QTableWidgetItem("Unconfirmed"))
            utxoTable.setItem(row_idx, 2, QTableWidgetItem(str(utxo.amount)))
            utxoTable.setItem(row_idx, 3, QTableWidgetItem(utxo.metadata.derivation))
            utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.metadata.address))
        self.ui.balanceEdit.setText(str(total_in-total_out))
        self.ui.totalInEdit.setText(str(total_in))
        self.ui.totalOutEdit.setText(str(total_out))

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

    def refresh_selected_utxos(self):
        changed = False

        table = self.ui.addressTableWidget
        if len(table.selectedIndexes()) == 0:
            return

        rows = []
        prev_row_idx = -1
        for cell in table.selectedIndexes():
            if cell.row() == prev_row_idx:
                continue
            rows.append(cell.row())
            prev_row_idx = cell.row()

        progress = QProgressDialog("Refreshing...", "Abort", 0, len(rows), self)
        progress.setWindowTitle("Updating " + self.wallet.name)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        progress.update()
        for i in range(0, len(rows)):
            progress.setValue(i)
            progress.repaint()
            if progress.wasCanceled():
                break
            derivation = table.item(rows[i], 0).text()
            address    = table.item(rows[i], 1).text()
            utxos = explorer.get_txos(self.wallet.name, address, derivation, testnet)
            if len(utxos) == 0:
                changed = self.wallet.remove_utxos_by_address(address) or changed
            else:
                for utxo in utxos:
                    changed = self.wallet.add_utxo(utxo) or changed
        progress.setValue(len(rows))
        progress.update()

        if changed:
            self.wallet.dirty = True
            self.display_utxos(self.wallet.utxos)

    def refresh_utxos(self):
        ahead = 20
        total = ahead * 2
        total_done = 0
        changed = False

        progress = QProgressDialog("Refreshing...", "Abort", 0, 100, self)
        progress.setWindowTitle("Updating " + self.wallet.name)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        progress.repaint()

        for derivation_pattern in (self.wallet.address_derivation, self.wallet.change_derivation):
            if 'x' in derivation_pattern:
                max = ahead
                i = 0
                while i < max:
                    progress.setValue(100*total_done / total)
                    progress.repaint()
                    if progress.wasCanceled():
                        break

                    derivation = derivation_pattern.replace("x", str(i))
                    address = self.wallet.address(derivation)
                    utxos = explorer.get_txos(self.wallet.name, address, derivation, testnet)
                    if len(utxos) == 0:
                        changed = self.wallet.remove_utxos_by_address(address) or changed
                    else:
                        for utxo in utxos:
                            changed = self.wallet.add_utxo(utxo) or changed
                            total = total - max + i + ahead
                            max = i+ahead
                    i += 1
                    total_done += 1
                if progress.wasCanceled():
                    break
            else:
                address = self.wallet.address(derivation_pattern)
                for utxo in explorer.get_utxos(self.wallet.name, address, derivation_pattern, testnet):
                    changed = changed or self.wallet.add_utxo(utxo)

        progress.setValue(100)
        progress.repaint()

        current_height = explorer.get_current_height(testnet)
        if self.current_height != current_height:
            self.current_height = current_height
            changed = True

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
        self.wallet = wallets.WordsWallet(self.ui.nameLineEdit.text(), words, password, testnet, "m/84'/"+testnet_str+"'/0'/0/x", "m/84'/"+testnet_str+"'/0'/1/x", wallets.SEGWIT)
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
        self.wallet = wallets.WordsWallet(self.ui.nameLineEdit.text(), words, password, testnet, "m/84'/"+testnet_str+"'/0'/0/x", "m/84'/"+testnet_str+"'/0'/1/x", wallets.SEGWIT)
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
            if utxo.metadata is None or utxo.metadata.spent == True:
                continue
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
        self.affected_rows = set()
    def set_affected_rows(self, affected_rows_set):
        self.affected_rows = affected_rows_set
        self.dataChanged.emit(self.index(0,0), self.index(len(self.inputs), len(self.columns)))
    def update(self):
        self.dataChanged.emit(self.index(0,0), self.index(len(self.inputs), len(self.columns)))
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
            darker = 40 if row in self.affected_rows else 0
            if column == 1:
                return QColor.fromRgb(255-darker,255-darker,255)
            return QColor.fromRgb(245-darker,245-darker,245)
        elif role == Qt.TextAlignmentRole:
            if column in [1,2,4]:
                return int(Qt.AlignVCenter | Qt.AlignRight)
            elif column == 0:
                return int(Qt.AlignVCenter | Qt.AlignCenter)
            else:
                return int(Qt.AlignVCenter | Qt.AlignLeft)
        return None

class OutputsTableModel(QAbstractTableModel):
    def __init__(self, outputs):
        QAbstractTableModel.__init__(self)
        self.outputs = outputs
        self.columns = ["Amount", "Address", "ScriptPubKey type"]
        self.affected_rows = set()
    def set_affected_rows(self, affected_rows_set):
        self.affected_rows = affected_rows_set
        self.dataChanged.emit(self.index(0,0), self.index(len(self.outputs), len(self.columns)))
    def rowCount(self, parent=QModelIndex()):
        return len(self.outputs)
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
        if row < 0 or row >= len(self.outputs):
            return False
        column = index.column()
        if column >= 2:
            return False
        if column == 0:
            if len(value) > 0:
                self.outputs[row].amount = int(value)
        elif column == 1:
            output = self.outputs[row]
            output.metadata.address = value
            address_type = scriptVM.address_type(value)
            if address_type == scriptVM.P2PKH:
                bin_address = Base58.check_decode(value)[1:]
                output.scriptpubkey = scriptVM.make_P2PKH_scriptpubkey(bin_address)
            elif address_type == scriptVM.P2SH:
                bin_address = Base58.check_decode(value)[1:]
                output.scriptpubkey = scriptVM.make_P2SH_scriptpubkey(bin_address)
            # TODO elif address_type == scriptVM.P2MS:
            elif address_type == scriptVM.P2WPKH:
                bin_address = bytes(bech32.decode('tb' if testnet else 'bc', value)[1])
                output.scriptpubkey = scriptVM.make_P2PWPKH_scriptpubkey(bin_address)
            # TODO elif address_type == scriptVM.P2WSH:
            # TODO elif address_type == scriptVM.P2TR:
            else:
                output.scriptpubkey = bytearray()
        self.dataChanged.emit(index, index)
        return True
    def flags(self, index):
        f = super(self.__class__,self).flags(index)
        f |= Qt.ItemIsSelectable
        f |= Qt.ItemIsEnabled
        if index.column() < 2:
            f |= Qt.ItemIsEditable
        return f
    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row    = index.row()
        output = self.outputs[row]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return "{}".format(output.amount)
            elif column == 1:
                if not output.metadata or not output.metadata.address:
                    return ""
                return "{}".format(output.metadata.address)
            elif column == 2:
                if not output.metadata or not output.metadata.address:
                    return ""
                address = output.metadata.address
                if len(address) == 0:
                    return ""
                elif scriptVM.address_is_testnet(address) and not testnet:
                    return "ERROR: address is testnet, network is mainnet"
                elif scriptVM.address_is_mainnet(address) and testnet:
                    return "ERROR: address is mainnet, network is testnet"
                else:
                    address_type = scriptVM.address_type(address)
                    if address_type == scriptVM.P2PKH:
                        return "P2PKH"
                    elif address_type == scriptVM.P2SH:
                        return "P2SH"
                    elif address_type == scriptVM.P2MS:
                        return "P2MS"
                    elif address_type == scriptVM.P2WPKH:
                        return "P2WPKH"
                    elif address_type == scriptVM.P2WSH:
                        return "P2WSH"
                    elif address_type == scriptVM.P2TR:
                        return "P2TR"
                    else:
                        return "ERROR: unknown address type"
        elif role == Qt.BackgroundRole:
            darker = 40 if row in self.affected_rows else 0
            if column in [0,1]:
                return QColor.fromRgb(255-darker,255-darker,255)
            return QColor.fromRgb(245-darker,245-darker,245)
        elif role == Qt.TextAlignmentRole:
            if column == 0:
                return int(Qt.AlignVCenter | Qt.AlignRight)
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
        self.ui.     signAllPUshButton.triggered.connect(self.sign_all_mine)
        self.ui.         signOneButton.clicked.connect(lambda: self.sign_selected(transactions.SIGHASH_ALL))
        self.ui.      verifyPushButton.triggered.connect(self.verify       )
        self.ui.      exportPushButton.triggered.connect(self.export       )
        self.ui.      importPushButton.triggered.connect(self.import_      )
        self.ui.   broadcastPushButton.triggered.connect(self.broadcast    )
        self.ui.           clearButton.triggered.connect(self.clear        )
        self.ui.PreventFeeSnipingCheckBox.toggled.connect(self.prevent_fee_sniping_toggled)
        self.ui.locktimeLineEdit.textChanged.connect(self.locktime_changed)
        self.ui.dateTimeEdit.dateTimeChanged.connect(self.locktime_datetime_changed)
        self.propagate_locktime_change = True

        self.ui.broadcastPushButton.setEnabled(False)

        self.wallets = {}
        self.transaction = transactions.Transaction()

        self.ui.inputsView.setModel(InputsTableModel(self.transaction.inputs))
        self.ui.inputsView.selectionModel().selectionChanged.connect(self.selected_inputs_changed)
        self.ui.inputsView.model().dataChanged.connect(self.inputs_changed)

        self.ui.outputsView.setModel(OutputsTableModel(self.transaction.outputs))
        self.ui.outputsView.model().dataChanged.connect(self.outputs_changed)

        #unix_time = int(QDateTime.currentDateTime().toMSecsSinceEpoch()/1000)
        self.transaction.locktime = 0
        self.ui.locktimeLineEdit.setText(str("0"))

        self.transaction_fee = 0
        self.transaction_virtual_size = 0

        self.locktime_changed()

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

        if testnet:
            pixmap = QPixmap(os.path.dirname(os.path.realpath(__file__)) + "/bitcoin_testnet.png")
            txt = "Testnet"
        else:
            pixmap = QPixmap(os.path.dirname(os.path.realpath(__file__)) + "/bitcoin_mainnet.png")
            txt = "Mainnet"
        self.ui.labelLogo.setPixmap(pixmap.scaled(45, 45, Qt.KeepAspectRatio))
        self.ui.labelNetwork.setText(txt)

    #def store_current_selection(self, newSelection, oldSelection):
    #    print("changed")
    #    #self.model().selection_changed(newSelection)

    def get_affected_inout(self, input_idxs_set):
        all_inputs  = False
        all_outputs = False
        affected_inputs = input_idxs_set
        affected_outputs = set()
        for i in input_idxs_set:
            input = self.transaction.inputs[i]
            sighashes = scriptVM.get_signatures_sighashes(input.scriptsig)
            anyonecanpay_sighashes = [s for s in sighashes if (s & transactions.SIGHASH_ANYONECANPAY) == 0]
            if len(anyonecanpay_sighashes) > 0:
                affected_inputs = set([idx for idx in range(0, len(self.transaction.inputs))])
                all_inputs = True
            for sighash in sighashes:
                if (sighash & 0xF) == transactions.SIGHASH_ALL:
                    affected_outputs = set([idx for idx in range(0, len(self.transaction.outputs))])
                    all_outputs = True
                    break
                elif (sighash & 0xF) == transactions.SIGHASH_SINGLE:
                    affected_outputs.add(i)
            if all_inputs and all_outputs:
                break
        return affected_inputs, affected_outputs

    def selected_inputs_changed(self, index):
        selected_indexes = set([x.row() for x in self.ui.inputsView.selectedIndexes()])
        affected_inputs, affected_outputs = self.get_affected_inout(selected_indexes)

        self.ui. inputsView.model().set_affected_rows(affected_inputs)
        self.ui.outputsView.model().set_affected_rows(affected_outputs)

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
            self.old_locktime = self.ui.locktimeLineEdit.text()
            self.transaction.locktime = explorer.get_current_height(testnet)
            self.ui.locktimeLineEdit.setText(str(self.transaction.locktime))
        else:
            self.ui.locktimeLineEdit.setText(self.old_locktime)

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
        filename = QFileDialog.getSaveFileName(self, 'Export transaction', filter="Tx files(*.tx);;All files(*)")[0]
        if len(filename) == 0:
            filename = None
            return
        if '.' not in filename:
            filename += ".tx"

        tx_hex = self.transaction.to_bin().hex()

        file = open(filename, 'w')
        file.write(tx_hex)
        for input in self.transaction.inputs:
            file.write(",")
            if input.txoutput and input.txoutput.metadata and input.txoutput.metadata.wallet_name:
                file.write(input.txoutput.metadata.wallet_name)
            file.write(",")
            if input.txoutput and input.txoutput.metadata and input.txoutput.metadata.derivation:
                file.write(input.txoutput.metadata.derivation)

        print("serialized transaction", tx_hex)

    def import_(self):
        filename = QFileDialog.getOpenFileName(self, 'Import transaction', filter="Tx files(*.tx);;All files(*)")[0]
        if len(filename) == 0:
            return

        file = open(filename, 'r')
        tx_with_metadata = file.read().split(",")
        tx_hex = tx_with_metadata[0]
        del tx_with_metadata[0]
        tx_bin = binascii.unhexlify(tx_hex)

        tx = transactions.Transaction.from_bin(tx_bin)
        for input in tx.inputs:
            input.parent_tx = tx
            input.txoutput  = explorer.get_utxo(input.txid.hex(), input.vout, testnet)
            input.txoutput.scriptpubkey = explorer.get_output_scriptpubkey(input.txid, input.vout, testnet)
            input.txoutput.metadata = transactions.TxOutput.Metadata()
            input.txoutput.metadata.txid = input.txid
            input.txoutput.metadata.vout = input.vout
            input.txoutput.metadata.address = scriptVM.get_address(input.txoutput.scriptpubkey, testnet)
            input.txoutput.metadata.wallet_name = tx_with_metadata[0]
            input.txoutput.metadata.derivation  = tx_with_metadata[1]
            if len(input.txoutput.metadata.wallet_name) == 0:
                input.txoutput.metadata.wallet_name = None
            if len(input.txoutput.metadata.derivation) == 0:
                input.txoutput.metadata.derivation = None
            del tx_with_metadata[0]
            del tx_with_metadata[0]
        for output in tx.outputs:
            output.metadata = transactions.TxOutput.Metadata()
            output.metadata.address = scriptVM.get_address(output.scriptpubkey, testnet)

        self.set_transaction(tx)

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
        if self.ui.PreventFeeSnipingCheckBox.isChecked():
            if not self.transaction.has_any_signature():
                self.transaction.locktime = explorer.get_current_height(testnet)
                self.ui.locktimeLineEdit.setText(str(self.transaction.locktime))

        selected_indexes = set([x.row() for x in self.ui.inputsView.selectedIndexes()])
        for vin in selected_indexes:
            if self.transaction.inputs[vin].txoutput and self.transaction.inputs[vin].txoutput.metadata and self.transaction.inputs[vin].txoutput.metadata.wallet_name and self.transaction.inputs[vin].txoutput.metadata.wallet_name not in self.wallets:
                QMessageBox.warning(self, 'Wallet not found', 'Wallet "' + self.transaction.inputs[vin].txoutput.metadata.wallet_name + '" not loaded.')
                continue
            if False == self.transaction.sign_one(sighash_type, vin, wallets=self.wallets):
                dialog = PKeyDialog(self.transaction, vin)
                if dialog.exec():
                    self.transaction.sign_one(sighash_type, vin, private_key=dialog.key)
                else:
                    print("No key for input")
        self.selected_inputs_changed(None)
        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_size()

    def sign_all_mine(self):
        if self.ui.PreventFeeSnipingCheckBox.isChecked():
            if not self.transaction.has_any_signature():
                self.transaction.locktime = explorer.get_current_height(testnet)
                self.ui.locktimeLineEdit.setText(str(self.transaction.locktime))

        selected_indexes = set([x.row() for x in self.ui.inputsView.selectedIndexes()])
        for vin in selected_indexes:
            if not self.transaction.inputs[vin].txoutput or not self.transaction.inputs[vin].txoutput.metadata or not self.transaction.inputs[vin].txoutput.metadata.wallet_name:
                continue
            if self.transaction.inputs[vin].txoutput.metadata.wallet_name not in self.wallets:
                QMessageBox.warning(self, 'Wallet not found', 'Wallet "' + self.transaction.inputs[vin].txoutput.metadata.wallet_name + '" not loaded.')

        self.transaction.sign_all(self.wallets, transactions.SIGHASH_ALL)
        #self.verify_all()
        self.update_inputs_view()
        self.update_size()

    def outputs_changed(self):
        self.ui.outputsView.resizeColumnsToContents()
        self.ui.inputsView.model().update()
        self.update_fee()
        self.update_size()

    def update_outputs_view(self):
        self.ui.outputsView.resizeColumnsToContents()

    def inputs_changed(self):
        self.ui.inputsView.resizeColumnsToContents()
        self.update_fee()
        self.update_size()

    def update_inputs_view(self, keep_selection=True):
        self.ui.inputsView.model().update()

    def add_output(self):
        self.ui.outputsView.model().beginInsertRows(self.ui.outputsView.rootIndex(), len(self.transaction.outputs), len(self.transaction.outputs))
        self.transaction.outputs.append(transactions.TxOutput())
        self.ui.outputsView.model().endInsertRows()
        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_outputs_view()
        self.update_size()

    def del_output(self):
        selected_indexes = list(set([qmi.row() for qmi in self.ui.outputsView.selectedIndexes()]))
        for idx in selected_indexes[::-1]:
            self.ui.outputsView.model().beginRemoveRows(self.ui.outputsView.rootIndex(), idx, idx)
            del self.transaction.outputs[idx]
            self.ui.outputsView.model().endRemoveRows()

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_outputs_view()
        self.update_fee()
        self.update_size()

    def add_inputs(self):
        j = json.dumps(util.to_dict(self.wallets))
        dialog = ChooseUTXOsDialog(self.wallets)
        if not dialog.exec():
            return
        current_height = explorer.get_current_height(testnet)
        for utxo in dialog.utxos:
            if self.transaction.has(utxo):
                continue
            self.ui.inputsView.model().beginInsertRows(self.ui.inputsView.rootIndex(), len(self.transaction.inputs), len(self.transaction.inputs))
            vin = self.transaction.add(utxo)
            self.ui.inputsView.model().endInsertRows()

        self.ui.broadcastPushButton.setEnabled(False)
        self.update_inputs_view()
        self.update_fee()
        self.update_size()

    def del_inputs(self):
        selected_indexes = list(set([x.row() for x in self.ui.inputsView.selectedIndexes()]))
        for idx in selected_indexes[::-1]:
            self.ui.inputsView.model().beginRemoveRows(self.ui.inputsView.rootIndex(), idx, idx)
            del self.transaction.inputs[idx]
            self.ui.inputsView.model().endRemoveRows()

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
        pw = b""
        dialog = PasswordDialog(self)
        if dialog.exec():
            pw = str.encode(dialog.pw)
        file = open(filename, 'rb')
        bin = file.read()
        j = ourCrypto.decrypt(bin, pw)
        if j is None:
            QMessageBox.warning(self, "Wrong password", "Wrong password")
            return
        d = json.loads(j)
        w = wallets.from_dict(d)
        if w.is_testnet() != testnet:
            if testnet:
                QMessageBox.warning(self, "Open wallet", "Wallet is NOT testnet while system was run with -testnet command line option")
            else:
                QMessageBox.warning(self, "Open wallet", "Wallet is testnet while system was NOT run with -testnet command line option")
            return
        w.filename = filename
        w.pwCheck = ourCrypto.encrypt("ourPassword", pw)
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
        self.set_transaction(transactions.Transaction())

    def set_transaction(self, tx):
        self.transaction = tx
        self.ui. inputsView.setModel(InputsTableModel(self.transaction.inputs))
        self.ui. inputsView.selectionModel().selectionChanged.connect(self.selected_inputs_changed)
        self.ui. inputsView.model().dataChanged.connect(self.inputs_changed)
        self.ui.outputsView.setModel(OutputsTableModel(self.transaction.outputs))
        self.ui.outputsView.model().dataChanged.connect(self.outputs_changed)
        self.ui.broadcastPushButton.setEnabled(False)

        self.update_inputs_view()
        self.update_outputs_view()
        self.update_fee()
        self.update_size()

if __name__ == "__main__":
    testnet = len(sys.argv) > 1 and sys.argv[1] == "-testnet"
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



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
from PySide6.QtCore import QFile, QIODevice, Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QPalette

# local imports

from ui.mainwindow import Ui_MainWindow
from ui.addwalletfromwordsdialog import Ui_AddWalletFromWordsDialog
from ui.addwalletfromxprvdialog  import Ui_AddWalletFromXprvDialog
from ui.walletinfo import Ui_walletInfoDialog
from ui.chooseutxosdialog import Ui_ChooseUTXOsDialog
from ui.privatekeydialog import Ui_PKeyDialog

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
        self.ui.       saveButton.clicked.connect(self.save)

        self.display_utxos(wallet.utxos)

        # workaround for qrcode size glitch
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tabWidget.setCurrentIndex(0)

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
            if utxo.parent_tx.metadata.height:
                utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(1 + current_height - utxo.parent_tx.metadata.height)))
            else:
                utxoTable.setItem(row_idx, 0, QTableWidgetItem("Unconfirmed"))
            utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
            utxoTable.setItem(row_idx, 2, QTableWidgetItem(utxo.metadata.derivation))
            utxoTable.setItem(row_idx, 3, QTableWidgetItem(utxo.metadata.address))

        self.ui.balanceEdit.setText(str(balance))

    def fill_combos(self):
        # todo: get those from a config file or something
        self.ui.derivationCombo.addItem("Root", "m")
        network = "1" if testnet else "0"
        self.ui.derivationCombo.addItem("Bitcoin core (v0.13.0, 2016-08-23 onward)", "m/0'/0'/0'")
        self.ui.derivationCombo.addItem("Mycelium legacy addresses (2015 onward)", "m/44'/"+network+"'/0'/0/0")
        self.ui.derivationCombo.addItem("Mycelium P2SH addresses (2018 onward)"  , "m/49'/"+network+"'/0'/0/0")
        self.ui.derivationCombo.addItem("Mycelium segwit addresses (2018 onward)", "m/84'/"+network+"'/0'/0/0")
        self.ui.utxoDerivationCombo.addItem("Try everything (slow)", "m, m/x, m/0/x, m/1/x, m/0'/0'/x', m/44'/"+network+"'/0'/0/x, m/44'/"+network+"'/0'/1/x, m/49'/"+network+"'/0'/0/x, m/49'/"+network+"'/0'/1/x, m/84'/"+network+"'/0'/0/x, m/84'/"+network+"'/0'/1/x")
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
            text = str(self.wallet.privkey_wif(derivation))
        elif self.ui.xprvRadio.isChecked():
            text = self.wallet.xprv(derivation)
        elif self.ui.xpubRadio.isChecked():
            text = self.wallet.xpub(derivation)
        set_qr_label(self.ui.qrcodeLabel, text)
        self.ui.valueEdit.setText(text)

    def resizeEvent(self, event):
        set_qr_label(self.ui.qrcodeLabel, self.ui.valueEdit.toPlainText())

    def refresh_utxos(self):
        derivation_patterns = [x.strip() for x in self.ui.utxoDerivationCombo.currentData().split(',')]
        balance = 0
        utxos = []
        for derivation_pattern in derivation_patterns:
            if 'x' in derivation_pattern:
                max = 5
                i = 0
                while i < max:
                    derivation = derivation_pattern.replace("x", str(i))
                    address = self.wallet.address(derivation)
                    for utxo in explorer.get_utxos(self.wallet.name, address, derivation, testnet):
                        utxos.append(utxo)
                        max = i+5
                    i += 1
            else:
                address = self.wallet.address(derivation_pattern)
                for utxo in explorer.get_utxos(self.wallet.name, address, derivation_pattern, testnet):
                    utxos.append(utxo)

        old_utxos = set([utxo.metadata.txid.hex()+str(utxo.metadata.vout) for utxo in self.wallet.utxos])
        new_utxos = set([utxo.metadata.txid.hex()+str(utxo.metadata.vout) for utxo in             utxos])
        if new_utxos != old_utxos:
            self.wallet.utxos = utxos
            self.wallet.dirty = True
            self.display_utxos(utxos)

    def save(self):
        filename = self.wallet.filename
        if filename is None:
            filename = QFileDialog.getSaveFileName(self, 'Save wallet to file', filter="Wallet files(*.wlt);;All files(*)")[0]
            if len(filename) == 0:
                return
            if '.' not in filename:
                filename += ".wlt"
        j = json.dumps(self.wallet.to_dict())
        bin = ourCrypto.encrypt(j, b"ourPassword")
        file = open(filename, 'wb')
        file.write(bin)
        self.wallet.filename = filename
        self.wallet.dirty    = False

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

class PKeyDialog(QDialog):
    def __init__(self):
        super(PKeyDialog, self).__init__()
        self.ui = Ui_PKeyDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.pkLineEdit.textChanged.connect(self.checks)
        self.key = None
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

        current_height = explorer.get_current_height(testnet)
        for wallet in self.wallets.values():
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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionLoad_from_words.triggered.connect(self.add_wallet_from_words)
        self.ui.actionLoad_from_xprv .triggered.connect(self.add_wallet_from_xprv )
        self.ui.actionOpen           .triggered.connect(self.open_wallet_file     )
        self.ui.    addUTXOsPushButton.clicked.connect(self.add_utxos    )
        self.ui.      removeUTXOButton.clicked.connect(self.del_utxos    )
        self.ui.   addOutputPushButton.clicked.connect(self.add_output   )
        self.ui.removeOutputPushButton.clicked.connect(self.del_output   )
        self.ui.     signAllPUshButton.clicked.connect(self.sign_all_mine)
        self.ui.      verifyPushButton.clicked.connect(self.verify_all   )
        self.ui.      exportPushButton.clicked.connect(self.export       )
        self.ui.            signButton.clicked.connect(self.sign_selected)

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["Signed", "sequence", "amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)

        outputsTable = self.ui.outputsTableWidget
        outputs_columns_titles = ["Amount", "Address", "ScriptPubKey type"]
        outputsTable.setColumnCount(len(outputs_columns_titles))
        outputsTable.setHorizontalHeaderLabels(outputs_columns_titles)
        outputsTable.cellChanged.connect(self.output_changed)

        self.wallets = {}
        self.transaction = transactions.Transaction()

    def closeEvent(self,event):
        msg = []
        for w in self.wallets.values():
            if w.dirty or w.filename is None:
                msg.append(w.name + " needs Jesus, exit without saving it?")

        if len(msg) == 0:
            event.accept()
            return
        if QMessageBox.Yes == QMessageBox.question(self, "Confirm Exit...", '\n'.join(msg), QMessageBox.Yes| QMessageBox.No):
            event.accept()
        else:
            event.ignore()

    def export(self):
        print("serialized transaction", self.transaction.to_bin().hex())

    def verify_all(self):
        for vin in range(0, len(self.transaction.inputs)):
            verification = self.transaction.verify(vin)
            if verification is None:
                msg = ""
            elif verification == True:
                msg = "Yes"
            else:
                msg = "ERROR"
            self.ui.UTXOsTableWidget.setItem(vin, 0, QTableWidgetItem(msg))

    def sign_selected(self):
        utxoTable = self.ui.UTXOsTableWidget
        selected_indexes = set([x.row() for x in utxoTable.selectedIndexes()])

        for vin in selected_indexes:
            if False == self.transaction.sign_one(transactions.SIGHASH_ALL, vin, wallets=self.wallets):
                dialog = PKeyDialog()
                if dialog.exec():
                    print(dialog.key.hex())
                    self.transaction.sign_one(transactions.SIGHASH_ALL, vin, private_key=dialog.key)
                else:
                    print("No key for input")

        self.verify_all()

    def sign_all_mine(self):
        self.transaction.sign_all(self.wallets, transactions.SIGHASH_ALL)
        self.verify_all()

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
                if len(address) == 0:
                    scheme = ""
                elif not testnet:
                    if address[0] == '1':
                        scheme = "P2PKH"
                        bin_address = Base58.check_decode(address)[1:]
                        self.transaction.outputs[row].scriptpubkey = binascii.unhexlify('76a914') + bin_address + binascii.unhexlify('88ac')
                    elif address[0] == '3':
                        scheme = "P2SH"
                    elif address[0:4] == "bc1q":
                        scheme = "Bech32"
                        bin_address = bech32.decode('bc', address)[1]
                        self.transaction.outputs[row].scriptpubkey = b'\x00\x14' + bytes(bin_address)
                    elif address[0:4] == "bc1p":
                        scheme = "P2TR"
                    else:
                        scheme = "ERROR"
                else:
                    if address[0] == "m" or address[0] == "n":
                        scheme = "P2PKH testnet"
                        bin_address = Base58.check_decode(address)[1:]
                        self.transaction.outputs[row].scriptpubkey = binascii.unhexlify('76a914') + bin_address + binascii.unhexlify('88ac')
                    elif address[0] == '2':
                        scheme = "P2SH testnet"
                    elif address[0:4] == "tb1q":
                        scheme = "Bech32 testnet"
                        bin_address = bech32.decode('tb', address)[1]
                        self.transaction.outputs[row].scriptpubkey = b'\x00\x14' + bytes(bin_address)
                    elif address[0:4] == "tb1p":
                        scheme = "P2TR testnet"
                    else:
                        scheme = "ERROR"
            except ValueError as e:
                outputsTable.setItem(row, 2, QTableWidgetItem("Bad base58 checksum"))
                return
            outputsTable.setItem(row, 2, QTableWidgetItem(scheme))
        else:
            pass

    def add_output(self):
        outputTable = self.ui.outputsTableWidget
        outputTable.insertRow(outputTable.rowCount())
        self.transaction.outputs.append(transactions.TxOutput())

    def del_output(self):
        outputsTable = self.ui.outputsTableWidget
        selected_indexes = list(set([qmi.row() for qmi in outputsTable.selectedIndexes()]))
        selected_indexes.sort()
        for idx in selected_indexes[::-1]:
            outputsTable.removeRow(idx)
            del self.transaction.outputs[idx]
        self.update_fee()

    def add_utxos(self):
        j = json.dumps(util.to_dict(self.wallets))
        dialog = ChooseUTXOsDialog(self.wallets)
        if dialog.exec():
            utxoTable = self.ui.UTXOsTableWidget
            current_height = explorer.get_current_height(testnet)
            for utxo in dialog.utxos:
                if self.transaction.has(utxo):
                    continue
                vin = self.transaction.add(utxo)
                input = self.transaction.inputs[vin]

                assert vin == utxoTable.rowCount()
                utxoTable.insertRow(vin)
                utxoTable.setItem(vin, 1, QTableWidgetItem(str(input.sequence)));
                utxoTable.setItem(vin, 2, QTableWidgetItem(str(utxo.amount)))
                utxoTable.setItem(vin, 3, QTableWidgetItem(utxo.metadata.wallet_name))
                if utxo.parent_tx.metadata.height:
                    utxoTable.setItem(vin, 4, QTableWidgetItem(str(1 + current_height - utxo.parent_tx.metadata.height)))
                else:
                    utxoTable.setItem(vin, 4, QTableWidgetItem("Unconfirmed"))
                utxoTable.setItem(vin, 5, QTableWidgetItem(utxo.metadata.derivation))
                utxoTable.setItem(vin, 6, QTableWidgetItem(utxo.metadata.address))

            utxoTable.resizeColumnsToContents()
            self.update_fee()

    def del_utxos(self):
        utxoTable = self.ui.UTXOsTableWidget
        selected_indexes = list(set([qmi.row() for qmi in utxoTable.selectedIndexes()]))
        selected_indexes.sort()
        for idx in selected_indexes[::-1]:
            utxoTable.removeRow(idx)
            del self.transaction.inputs[idx]
        self.update_fee()

    def update_fee(self):
        input_total = sum([utxo.txoutput.amount for utxo in self.transaction.inputs])
        output_total = sum([out.amount for out in self.transaction.outputs])
        fee = input_total - output_total
        self.ui.inputSumEdit.setText(str(input_total))
        self.ui.outputSumEdit.setText(str(output_total))
        self.ui.feeEdit.setText(str(fee))

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

    def menu_action_wallet_name(self, name):
        if name not in self.wallets:
            return
        dialog = WalletInfoDialog(self.wallets[name])
        if dialog.exec():
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


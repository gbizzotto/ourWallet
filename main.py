# This Python file uses the following encoding: utf-8
import os
import sys
import binascii
from pathlib import Path
from io import BytesIO
import requests
import json
from copy import deepcopy
import hashlib
import ecdsa

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox, QMenu, QTableWidgetItem, QCheckBox, QWidgetAction, QFileDialog
from PySide6.QtCore import QFile, QIODevice, Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QPalette

from ui.mainwindow import Ui_MainWindow
from ui.addwalletfromwordsdialog import Ui_AddWalletFromWordsDialog
from ui.addwalletfromxprvdialog  import Ui_AddWalletFromXprvDialog
from ui.walletinfo import Ui_walletInfoDialog
from ui.chooseutxosdialog import Ui_ChooseUTXOsDialog

import qrcode

import bip39
import bip32utils
from bip32utils import Base58

import explorer
import transactions
import util
import wallets
import ourCrypto
import scriptVM

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
                    for utxo in explorer.get_utxos(self.wallet.name, address, derivation, testnet):
                        utxos.append(utxo)
                        max = i+2
                    i += 1
            else:
                address = self.wallet.address(derivation_pattern)
                for utxo in explorer.get_utxos(self.wallet.name, address, derivation_pattern, testnet):
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
        self.known_utxos = []
        self.utxos       = []

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)
        utxoTable.itemSelectionChanged.connect(self.selection_changed)

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
                utxoTable.setItem(row_idx, 2, QTableWidgetItem(str(current_height - utxo.parent_tx.metadata.height)))
                utxoTable.setItem(row_idx, 3, QTableWidgetItem(utxo.metadata.derivation))
                utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.metadata.address))
    def selection_changed(self):
        utxoTable = self.ui.UTXOsTableWidget
        selected_indexes = list(set([qmi.row() for qmi in self.ui.UTXOsTableWidget.selectedIndexes()]))
        self.ui.sumLineEdit.setText(str(sum([int(utxoTable.item(row_idx, 0).text()) for row_idx in selected_indexes])))
        self.utxos = [self.known_utxos[row_idx] for row_idx in selected_indexes]

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
        self.ui.   addOutputPushButton.clicked.connect(self.add_output   )
        self.ui.removeOutputPushButton.clicked.connect(self.del_output   )
        self.ui.     signAllPUshButton.clicked.connect(self.sign_all_mine)
        self.ui.      verifyPushButton.clicked.connect(self.verify       )

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["Signed", "Final", "amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)

        outputsTable = self.ui.outputsTableWidget
        outputs_columns_titles = ["Amount", "Address", "ScriptPubKey type"]
        outputsTable.setColumnCount(len(outputs_columns_titles))
        outputsTable.setHorizontalHeaderLabels(outputs_columns_titles)
        outputsTable.cellChanged.connect(self.output_changed)

        self.wallets = {}
        self.transaction = transactions.Transaction()

    def verify(self):
        inputsTable = self.ui.UTXOsTableWidget
        i = 0
        for input in self.transaction.inputs:
            full_script = input.scriptsig + input.txoutput.scriptpubkey
            print(scriptVM.RunnerVM.run(self.transaction, i, full_script, debug=True))
            i += 1

    def sign_all_mine(self):
        inputsTable = self.ui.UTXOsTableWidget
        for row_idx in range(0, inputsTable.rowCount()):
            utxo = self.transaction.inputs[row_idx].txoutput
            script_type = scriptVM.identify_scriptpubkey(utxo.scriptpubkey)
            if script_type == scriptVM.P2PKH:
                tx_copy = deepcopy(self.transaction)
                tx_copy.strip_for_signature(row_idx, transactions.SIGHASH_ALL)
                tx_bin = tx_copy.to_bin()
                tx_bin.append(transactions.SIGHASH_ALL)
                tx_bin += b"\x00\x00\x00"

                print("tx", tx_bin.hex())

                wallet     = self.wallets[utxo.metadata.wallet_name]
                derivation = utxo.metadata.derivation
                private_key = wallet.privkey(derivation)
                print("pv key", private_key.hex())
                pubkey = wallet.pubkey(derivation)
                print("pub key", pubkey.hex())

                data = hashlib.sha256(tx_bin).digest()
                print("data", data.hex())
                vk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
                signature = vk.sign(data, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der)

                signature = ourCrypto.normalize(signature)

                sighash = bytes([transactions.SIGHASH_ALL])
                print("sighash", sighash.hex())
                signature = signature + sighash

                print("signature", signature.hex())

                self.transaction.inputs[row_idx].scriptsig = bytearray()
                stream = scriptVM.ScriptByteStream(self.transaction.inputs[row_idx].scriptsig)
                stream.add_chunk(signature)
                stream.add_chunk(pubkey)

                print("scriptsig", self.transaction.inputs[row_idx].scriptsig.hex())
                print("serialized transaction", self.transaction.to_bin().hex())

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
            b58_address = outputsTable.item(row, col).text()
            try:
                if not testnet:
                    if b58_address[0] == '1':
                        scheme = "P2PKH"
                        hex_address = Base58.check_decode(b58_address)[1:]
                        self.transaction.outputs[row].scriptpubkey = binascii.unhexlify('76a914') + hex_address + binascii.unhexlify('88ac')
                    elif b58_address[0] == '3':
                        scheme = "P2SH"
                    elif b58_address[0:4] == "bc1q":
                        scheme = "Bech32"
                    elif b58_address[0:4] == "bc1p":
                        scheme = "P2TR"
                    else:
                        scheme = "ERROR"
                else:
                    if b58_address[0] == "m" or b58_address[0] == "n":
                        scheme = "P2PKH testnet"
                        hex_address = Base58.check_decode(b58_address)[1:]
                        self.transaction.outputs[row].scriptpubkey = binascii.unhexlify('76a914') + hex_address + binascii.unhexlify('88ac')
                    elif b58_address[0] == '2':
                        scheme = "P2SH testnet"
                    elif b58_address[0:4] == "tb1q":
                        scheme = "Bech32 testnet"
                    elif b58_address[0:4] == "tb1p":
                        scheme = "P2TR testnet"
                    else:
                        scheme = "ERROR"
            except ValueError as e:
                outputsTable.setItem(row, 2, QTableWidgetItem("Bad base58 checksum"))
                return
            outputsTable.setItem(row, 2, QTableWidgetItem(scheme))
        else:
            pass

        print(self.transaction)

    def add_output(self):
        outputTable = self.ui.outputsTableWidget
        outputTable.insertRow(outputTable.rowCount())
        self.update_fee()
        self.transaction.outputs.append(transactions.TxOutput())

    def del_output(self):
        outputsTable = self.ui.outputsTableWidget
        selected_indexes = list(set([qmi.row() for qmi in outputsTable.selectedIndexes()]))
        selected_indexes.sort()
        for idx in selected_indexes[::-1]:
            outputsTable.removeRow(idx)
            del self.transaction.outputs[idx]
        if len(selected_indexes) > 0:
            self.update_fee()

    def chooseutxos(self):
        j = json.dumps(util.to_dict(self.wallets))
        dialog = ChooseUTXOsDialog(self.wallets)
        if dialog.exec():
            utxoTable = self.ui.UTXOsTableWidget
            utxoTable.setRowCount(0)
            current_height = explorer.get_current_height(testnet)
            sum = 0
            self.transaction.inputs = []
            for utxo in dialog.utxos:
                txin = transactions.TxInput()
                txin.txid = utxo.metadata.txid
                txin.vout = utxo.metadata.vout
                txin.scriptsig = b''
                txin.sequence = 0
                txin.parent_tx = self.transaction
                txin.txoutput = utxo
                self.transaction.inputs.append(txin)

                sum += utxo.amount
                row_idx = utxoTable.rowCount()
                utxoTable.insertRow(row_idx)
                cb = QCheckBox()
                cb.setCheckable(False)
                utxoTable.setCellWidget(row_idx, 0, cb);
                utxoTable.setCellWidget(row_idx, 1, QCheckBox());
                utxoTable.setItem(row_idx, 2, QTableWidgetItem(str(utxo.amount)))
                utxoTable.setItem(row_idx, 3, QTableWidgetItem(utxo.metadata.wallet_name))
                utxoTable.setItem(row_idx, 4, QTableWidgetItem(str(current_height - utxo.parent_tx.metadata.height)))
                utxoTable.setItem(row_idx, 5, QTableWidgetItem(utxo.metadata.derivation))
                utxoTable.setItem(row_idx, 6, QTableWidgetItem(utxo.metadata.address))
            utxoTable.resizeColumnsToContents()
            self.ui.inputSumEdit.setText(str(sum))
            self.update_fee()

        print(self.transaction)

    def update_fee(self):
        input_total = int(self.ui.inputSumEdit.text())
        output_total = int(self.ui.outputSumEdit.text())
        fee = input_total - output_total
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
            w.filename = filename
            j = json.dumps(w.to_dict())
            bin = ourCrypto.encrypt(j, b"ourPassword")
            file = open(filename, 'wb')
            file.write(bin)

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


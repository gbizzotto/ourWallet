# This Python file uses the following encoding: utf-8
import os
import sys
import binascii
from pathlib import Path
from io import BytesIO
import requests
import json
from copy import deepcopy

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox, QMenu, QTableWidgetItem, QCheckBox, QWidgetAction
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

testnet = True

def set_qr_label(label, text):
    buf = BytesIO()
    img = qrcode.make(text)
    img.save(buf, "PNG")
    label.setText("")
    qt_pixmap = QPixmap()
    qt_pixmap.loadFromData(buf.getvalue(), "PNG")
    label.setPixmap(qt_pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio))

class utxo:
    def __init__(self, address, derivation, height, txid, vout, amount):
        self.address = address
        self.derivation = derivation
        self.height = height
        self.txid   = txid
        self.vout   = vout
        self.amount = amount
    #def fromJson(self, json_utxo):
    #    self.__dict__ = json.loads(json_utxo)
    @staticmethod
    def fromDict(d):
        return utxo(d["address"], d["derivation"], d["height"], d["txid"], d["vout"], d["amount"])

class Wallet:
    def __init__(self, name):
        self.name = name
        self.is_hd = False
        self.from_words = False
        self.utxos = []
    @staticmethod
    def fromDict(d):
        if d["is_hd"]:
            return HDWallet.fromDict(d)
        w = Wallet(d["name"])
        w.utxos = [utxo.fromDict(u) for u in d["utxos"]]
        return w

class OurJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "toJsonDict"):
            return self.default(obj.toJsonDict())
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return obj

class KeysWallet(Wallet):
    def __init__(self, name):
        super(KeysWallet, self).__init__(name)

class HDWallet(Wallet):
    def __init__(self, name, root_key):
        super(HDWallet, self).__init__(name)
        self.is_hd = True
        self.root_key = root_key
    def address(self, derivation):
        k = HDWallet.Derive(self.root_key, derivation)
        return k.Address()
    def privkey(self, derivation):
        k = HDWallet.Derive(self.root_key, derivation)
        return k.WalletImportFormat()
    def xprv(self, derivation):
        k = HDWallet.Derive(self.root_key, derivation)
        return k.ExtendedKey(private=True)
    def xpub(self, derivation):
        k = HDWallet.Derive(self.root_key, derivation)
        return k.ExtendedKey(private=False)
    def Derive(root_key, derivation):
        k = root_key
        for d in derivation.split('/'):
            if d == 'm':
                continue
            elif d[-1] == "'":
                k = k.CKDpriv(int(d[:-1])+bip32utils.BIP32_HARDEN)
            else:
                k = k.CKDpriv(int(d))
        return k
    def toJsonDict(self):
        d = deepcopy(self.__dict__)
        d["root_key"] = self.root_key.ExtendedKey()
        return d
    @staticmethod
    def fromDict(d):
        w = HDWallet(d["name"], bip32utils.BIP32Key.fromExtendedKey(d["root_key"]))
        w.utxos = [utxo.fromDict(u) for u in d["utxos"]]
        return w

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
        utxo_columns_titles = ["height", "amount", "derivation", "address"]
        self.ui.utxoTable.setColumnCount(len(utxo_columns_titles))
        self.ui.utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)
        self.ui.utxoRefreshButton.clicked.connect(self.refresh_utxos)

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
                    print(derivation)
                    for utxo in get_utxos(address, derivation):
                        utxos.append(utxo)
                        max = i+2
                    i += 1
            else:
                address = self.wallet.address(derivation_pattern)
                for utxo in get_utxos(address, derivation_pattern):
                    utxos.append(utxo)
        balance = add_utxos_to_table(utxos, self.ui.utxoTable)
        self.wallet.utxos = utxos
        self.ui.balanceEdit.setText(str(balance))

        print(json.dumps(self.wallet, cls=OurJsonEncoder))

def add_utxos_to_table(utxos, utxoTable):
    balance = 0
    for utxo in utxos:
        balance += utxo.amount
        add_utxo_to_table(utxo, utxoTable, utxo.derivation, utxo.address)
    return balance

def add_utxo_to_table(utxo, utxoTable, derivation, address):
    row_idx = utxoTable.rowCount()
    utxoTable.insertRow(row_idx)
    utxoTable.setItem(row_idx, 0, QTableWidgetItem(str(utxo.height)))
    utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
    utxoTable.setItem(row_idx, 2, QTableWidgetItem(derivation))
    utxoTable.setItem(row_idx, 3, QTableWidgetItem(address))

def get_utxos(address, derivation):

    print(address)

    # getting data from blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/address/"+address+"/utxo")
    utxos = json.loads(page.text)
    result = []
    for u in utxos:
        result.append(utxo(address, derivation, u["status"]["block_height"], u["txid"], u["vout"], u["value"]))
    return result

    # from blockcypher
    #network = "test3/" if testnet else "main/"
    #page = requests.get("https://api.blockcypher.com/v1/btc/"+network+"addrs/"+address+"?unspentOnly=1")
    #utxos = json.loads(page.text)
    #if "txrefs" not in utxos:
    #    return []
    #print(utxos)
    #utxos = utxos["txrefs"]
    #result = []
    #for u in utxos:
    #    result.append(utxo(address, derivation, u["block_height"], u["tx_hash"], u["tx_output_n"], u["value"]))
    #return result

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
        seed = bip39.phrase_to_seed(words, password)
        key = bip32utils.BIP32Key.fromEntropy(seed, testnet=testnet)
        self.wallet = HDWallet(self.ui.nameLineEdit.text(), key)
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
        xkey = self.ui.xprvPlainTextEdit.toPlainText()
        key = bip32utils.BIP32Key.fromExtendedKey(xkey)
        self.wallet = HDWallet(self.ui.nameLineEdit.text(), key)
        super(AddWalletFromXprvDialog, self).accept()

class ChooseUTXOsDialog(QDialog):
    def __init__(self, wallets):
        super(ChooseUTXOsDialog, self).__init__()
        self.ui = Ui_ChooseUTXOsDialog()
        self.ui.setupUi(self)
        self.wallets = wallets
        self.utxos = []

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["select", "amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)

        for wallet in self.wallets.values():
            for utxo in wallet.utxos:
                row_idx = utxoTable.rowCount()
                utxoTable.insertRow(row_idx)
                cb = QCheckBox()
                cb.stateChanged.connect(self.calculateSum)
                utxoTable.setCellWidget(row_idx, 0, cb);
                utxoTable.setItem(row_idx, 1, QTableWidgetItem(str(utxo.amount)))
                utxoTable.setItem(row_idx, 2, QTableWidgetItem(wallet.name))
                utxoTable.setItem(row_idx, 3, QTableWidgetItem(str(utxo.height)))
                utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.derivation))
                utxoTable.setItem(row_idx, 5, QTableWidgetItem(utxo.address))
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
                    if utxo.derivation == derivation:
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
        self.wallets_menu = QMenu("Wallets info")
        self.ui.menuWallets.insertMenu(self.ui.actionLoad_from_words, self.wallets_menu)
        self.ui.menuWallets.insertSeparator(self.ui.actionLoad_from_words)
        self.ui.selectUTXOsPushButton.pressed.connect(self.chooseutxos)

        utxoTable = self.ui.UTXOsTableWidget
        utxo_columns_titles = ["Signed", "amount", "wallet", "confirmations", "derivation", "address"]
        utxoTable.setColumnCount(len(utxo_columns_titles))
        utxoTable.setHorizontalHeaderLabels(utxo_columns_titles)

        # TODO load wallets from ciphered file
        j = '{"kjk": {"name": "kjk", "is_hd": true, "from_words": false, "utxos": [{"address": "tb1qlqh7r9q8pl2cuteegphp6sqt84j007fqjhwac2", "derivation": "m/0/0", "height": 2063046, "txid": "28cf752b51ec17d580231fb2beaa41948ddc39b17b7c2e356daaff8b3cf1f190", "vout": 1, "amount": 33000}], "root_key": "vprv9LDabV4oq3PVrmnqHcL3yiyRLVmL9W9M4w5VME2T2bMukCu8fMLGotEXKfo49xuCTtyeCkGsdK1CitKhWbvB9fyBxVYA3iGAvJWwKdPMzjd"}, "t": {"name": "t", "is_hd": true, "from_words": false, "utxos": [{"address": "mubWtZaRawp6KhLZkV9AQ9tGbRApy87UGA", "derivation": "m/0/0", "height": 2066017, "txid": "5168f1e5a2d68e4eb63626be78007463963ec30202247e5cfcf0e4cf2c631312", "vout": 1, "amount": 100000}, {"address": "msmVjeewKf2j8YazUEmJxkdvUzv4P9VaBM", "derivation": "m/1/0", "height": 2066017, "txid": "5168f1e5a2d68e4eb63626be78007463963ec30202247e5cfcf0e4cf2c631312", "vout": 0, "amount": 4578049}], "root_key": "tprv8gi3CTjd8fLft631wpevMQQYumH4AG8xXoxDR3szAihP1a8zQSUppijRJ8xChJo8W7SZTsd5yYgDxfDiHDRUdpZizGxxXjXhfeoH5xe77XU"}}'
        self.wallets = {k:Wallet.fromDict(v) for (k,v) in json.loads(j).items()}
        for w in self.wallets.values():
            print(w.name)
            menuaction = self.wallets_menu.addAction(w.name)
            menuaction.triggered.connect(lambda *args,name=w.name:self.menu_action_wallet_name(name))
            #print(menuaction)

    def add_wallet_from_words(self, event):
        dialog = AddWalletFromWordsDialog()
        if dialog.exec():
            w = dialog.wallet
            self.wallets[w.name] = w
            menuaction = self.wallets_menu.addAction(w.name)
            menuaction.triggered.connect(lambda:self.menu_action_wallet_name(w.name))

    def add_wallet_from_xprv(self, event):
        dialog = AddWalletFromXprvDialog()
        if dialog.exec():
            w = dialog.wallet
            self.wallets[w.name] = w
            menuaction = self.wallets_menu.addAction(w.name)
            menuaction.triggered.connect(lambda:self.menu_action_wallet_name(w.name))

    def menu_action_wallet_name(self, name):
        print(name)
        if name not in self.wallets:
            return
        dialog = WalletInfoDialog(self.wallets[name])
        if dialog.exec():
            pass

    def chooseutxos(self):
        j = json.dumps(self.wallets, cls=OurJsonEncoder)
        print(j)
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
                    utxoTable.setItem(row_idx, 3, QTableWidgetItem(str(utxo.height)))
                    utxoTable.setItem(row_idx, 4, QTableWidgetItem(utxo.derivation))
                    utxoTable.setItem(row_idx, 5, QTableWidgetItem(utxo.address))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


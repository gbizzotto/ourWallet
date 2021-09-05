
import bip39
import bip32utils
import transactions
from copy import deepcopy
import json

import util

def from_dict(d):
    cls = globals()[d["wallet_type"]]
    w = cls.from_dict(d)
    w.utxos = [transactions.TxOutput.from_dict(u) for u in d["utxos"]]
    w.filename = None
    return w

class Wallet:
    def __init__(self, name, filename=None):
        self.name = name
        self.utxos = []
        self.filename = filename
    def to_dict(self):
        d = deepcopy(self)
        # returns the class name of the correct subclass
        del d.__dict__["filename"]
        d.wallet_type = type(self).__name__
        return util.to_dict(d.__dict__)

# abstract class
class HDWallet(Wallet):
    def __init__(self, name):
        super(HDWallet, self).__init__(name)
    def to_dict(self):
        d = super(HDWallet, self).to_dict()
        del d["root_key"]
        return d
    def address(self, derivation, bip=None):
        k = HDWallet.Derive(self.root_key, derivation, bip)
        return k.Address()
    def privkey(self, derivation, bip=None):
        k = HDWallet.Derive(self.root_key, derivation, bip)
        return k.WalletImportFormat()
    def xprv(self, derivation, bip=None):
        k = HDWallet.Derive(self.root_key, derivation, bip)
        return k.ExtendedKey(private=True)
    def xpub(self, derivation, bip=None):
        k = HDWallet.Derive(self.root_key, derivation, bip)
        return k.ExtendedKey(private=False)
    @staticmethod
    def Derive(root_key, derivation, bip=None):
        k = root_key
        for d in derivation.split('/'):
            if d == 'm':
                continue
            elif d[-1] == "'":
                k = k.CKDpriv(int(d[:-1])+bip32utils.BIP32_HARDEN)
            else:
                k = k.CKDpriv(int(d))
        if bip is not None:
            k.bip = bip
        return k

class WordsWallet(HDWallet):
    def __init__(self, name, phrase, passwd, testnet):
        super(WordsWallet, self).__init__(name)
        self.phrase  = phrase
        self.passwd  = passwd
        self.testnet = testnet
        seed = bip39.phrase_to_seed(" ".join(str(self.phrase).split()), self.passwd)
        self.root_key = bip32utils.BIP32Key.fromEntropy(seed, testnet=self.testnet)
    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["phrase"], d["passwd"], d["testnet"])

class ExtendedKeyWallet(HDWallet):
    def __init__(self, name, extendedkey):
        super(ExtendedKeyWallet, self).__init__(name)
        self.extendedkey = extendedkey
        self.root_key = bip32utils.BIP32Key.fromExtendedKey(self.extendedkey)
    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["extendedkey"])

class KeysWallet(Wallet):
    def __init__(self, name):
        super(KeysWallet, self).__init__(name)
    # TODO


if __name__ == "__main__":
    ww = WordsWallet("test_ww", "run fog exhibit wolf whisper wet luxury tiger spell exercise aunt way", "", True)
    d = ww.to_dict()
    ww2 = from_dict(d)
    assert json.dumps(ww.to_dict()) == json.dumps(ww2.to_dict())

    ekw = ExtendedKeyWallet("test_ekw", "tprv8ZgxMBicQKsPdPMUwkx6qrBjTPbA1kq1DXdvcaGfrhRDsGY6yN7uEGUBcvQ9VcD43fxMQXTHb7jjetcea4R8RMQLeArQLJPWiCSQ9WtrK8J")
    d = ekw.to_dict()
    ekw2 = from_dict(d)
    assert json.dumps(ekw.to_dict()) == json.dumps(ekw2.to_dict())

    print("Ok")

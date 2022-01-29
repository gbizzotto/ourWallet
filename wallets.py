
import bip39
import bip32utils
import transactions
from copy import deepcopy
import json
import binascii

import util

LEGACY = 44
COMPATIBILITY = 49
SEGWIT = 84

def from_dict(d):
    cls = globals()[d["wallet_type"]]
    w = cls.from_dict(d)
    w.utxos = [transactions.TxOutput.from_dict(u) for u in d["utxos"]]
    w.filename = None
    return w

class Wallet:
    def __init__(self, name, address_derivation, change_derivation, address_type, filename=None):
        self.name = name
        self.utxos = []
        self.filename = filename
        self.dirty = False
        self.pwcheck = None
        self.address_derivation = address_derivation
        self.change_derivation  = change_derivation
        self.address_type       = address_type
    def to_dict(self):
        d = deepcopy(self)
        # returns the class name of the correct subclass
        del d.__dict__["filename"]
        del d.__dict__["pwcheck"]
        del d.__dict__["dirty"]
        d.wallet_type = type(self).__name__
        return util.to_dict(d.__dict__)

    def add_utxo(self, utxo):
        for u in self.utxos:
            if u.eq(utxo):
                return False
        self.utxos.append(utxo)
        return True

    def remove_utxo(self, utxo):
        old_size = len(self.utxos)
        self.utxos[:] = [u for u in self.utxos if not u.eq(utxo)]
        new_size = len(self.utxos)
        return old_size != new_size

    def remove_utxos_by_address(self, address):
        old_size = len(self.utxos)
        self.utxos[:] = [u for u in self.utxos if not u.metadata.address==address]
        new_size = len(self.utxos)
        return old_size != new_size

# abstract class
class HDWallet(Wallet):
    def __init__(self, name, root_key, address_derivation, change_derivation, address_type):
        testnet_derivation_str = "1" if root_key.testnet else "0"
        purpose_str = str(root_key.bip)
        super(HDWallet, self).__init__(name, address_derivation, change_derivation, address_type)
        self.root_key = root_key
    def is_testnet(self):
        return self.root_key.testnet
    def to_dict(self):
        d = super(HDWallet, self).to_dict()
        del d["root_key"]
        return d
    def address(self, derivation, bip=None):
        return self.derive(derivation, bip).Address()
    def pubkey(self, derivation, bip=None):
        return self.derive(derivation, bip).PublicKey()
    def privkey_wif(self, derivation, bip=None):
        return self.derive(derivation, bip).WalletImportFormat()
    def privkey(self, derivation, bip=None):
        return self.derive(derivation, bip).PrivateKey()
    def xprv(self, derivation, bip=None):
        return self.derive(derivation, bip).ExtendedKey(private=True)
    def xpub(self, derivation, bip=None):
        return self.derive(derivation, bip).ExtendedKey(private=False)
    def derive(self, derivation, bip=None):
        if bip is None:
            bip = self.address_type
        k = self.root_key
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
    def __init__(self, name, phrase, passwd, testnet, address_derivation, change_derivation, address_type):
        seed = bip39.phrase_to_seed(" ".join(str(phrase).split()), passwd)
        root_key = bip32utils.BIP32Key.fromEntropy(seed, testnet=testnet)
        root_key.bip = SEGWIT
        super(WordsWallet, self).__init__(name, root_key, address_derivation, change_derivation, address_type)
        self.phrase  = phrase
        self.passwd  = passwd
        self.testnet = testnet
    @classmethod
    def from_dict(cls, d):
        if "address_derivation" not in d:
            testnet_derivation_str = "1" if d["testnet"] else "0"
            d["address_derivation"] = "m/" + str(SEGWIT) + "'/" + testnet_derivation_str + "'/0'/0/x"
            d[ "change_derivation"] = "m/" + str(SEGWIT) + "'/" + testnet_derivation_str + "'/0'/1/x"
            d["address_type"] = SEGWIT
        return cls(d["name"], d["phrase"], d["passwd"], d["testnet"], d["address_derivation"], d["change_derivation"], d["address_type"])

class ExtendedKeyWallet(HDWallet):
    def __init__(self, name, extendedkey, address_derivation=None, change_derivation=None, address_type=None):
        self.extendedkey = extendedkey
        root_key = bip32utils.BIP32Key.fromExtendedKey(self.extendedkey)
        if address_derivation is None:
            address_derivation = "m/0/x"
            change_derivation  = "m/1/x"
            address_type = root_key.bip
        super(ExtendedKeyWallet, self).__init__(name, root_key, address_derivation, change_derivation, address_type)
    @classmethod
    def from_dict(cls, d):
        if "address_derivation" not in d:
            d["address_derivation"] = None
            d[ "change_derivation"] = None
            d["address_type"] = None
        return cls(d["name"], d["extendedkey"], d["address_derivation"], d["change_derivation"], d["address_type"])

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

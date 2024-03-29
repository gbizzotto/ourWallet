
import io
import binascii
import json
import util
import hashlib
from copy import deepcopy

import ecdsa

import ourCrypto
import scriptVM

SIGHASH_ALL    = 1 # outputs locked
SIGHASH_NONE   = 2 # outputs open
SIGHASH_SINGLE = 3 # outputs not mine
SIGHASH_ANYONECANPAY = 0x80 # inputs locked/open

class TxByteStream:
    def __init__(self, bytearray):
        self.buffer = bytearray
        self.stream = io.BufferedReader(io.BytesIO(self.buffer))
    def peek(self):
        if self.eof():
            return None
        return self.buffer[self.stream.tell()]
    def eof(self):
        return self.stream.tell() >= len(self.buffer)
    def read_chunk(self, size):
        return self.stream.read(size)
    def read_int(self, size):
        result = 0
        shift = 0
        while size > 0:
            result += self.read_chunk(1)[0] << shift
            size -= 1
            shift += 8
        return result
    def read_varint(self):
        c = self.read_int(1)
        if c < 0xFD:
            return c
        elif c == 0xFD:
            return self.read_int(2)
        elif c == 0xFE:
            return self.read_int(4)
        elif c == 0xFF:
            return self.read_int(8)

    def write(self, byte):
        self.buffer.append(byte)
    def write_chunk(self, b):
        self.buffer.extend(b)
    def write_int(self, size, value):
        self.buffer.extend(util.to_bytes(size, value))
    def write_varint(self, value):
        self.buffer.extend(util.to_varint_bytes(value))


class TxInput:
    # self.txid
    # self.vout
    # self.scriptsig
    # self.sequence
    # ---------------
    # self.parent_tx
    # self.txoutput

    def make_script_code(self):
        scriptpubkey = self.txoutput.scriptpubkey
        assert scriptpubkey[0] == 0
        assert scriptpubkey[1] == 20
        # TODO how about P2WSH?
        return scriptVM.make_P2PKH_scriptpubkey(scriptpubkey[2:])

    def to_dict(self):
        d = deepcopy(self.__dict__)
        if "parent_tx" in d:
            del d["parent_tx"]
        return util.to_dict(d)

    def to_bin(self):
        bin = bytearray()
        stream = TxByteStream(bin)
        stream.write_chunk(self.txid[::-1])
        stream.write_int(4, self.vout)
        stream.write_varint(len(self.scriptsig))
        stream.write_chunk(self.scriptsig)
        stream.write_int(4, self.sequence)
        return bin

    @staticmethod
    def from_txbytestream(stream):
        txin = TxInput()
        txin.txid      = stream.read_chunk(32)[::-1]
        txin.vout      = stream.read_int(4)
        txin.scriptsig = stream.read_chunk(stream.read_varint())
        txin.sequence  = stream.read_int(4)
        txin.parent_tx = None
        txin.txoutput  = None
        return txin

    @classmethod
    def from_dict(cls, d):
        txin = cls()
        txin.txid       = binascii.unhexlify(d["txid"])
        txin.vout       = d["vout"]
        txin.scriptsig  = binascii.unhexlify(d["scriptsig"])
        txin.sequence   = d["sequence"]
        txin.parent_tx  = None
        txin.txoutput   = Metadata.from_dict(d["txoutput"])



class TxOutput:
    # self.amount
    # self.scriptpubkey
    # ---------------
    # self.parent_tx
    # self.metadata

    class Metadata:
        # self.wallet_name
        # self.address
        # self.derivation
        # self.spent
        # self.txid
        # self.vout
        def __init__(self):
            self.wallet_name = None
            self.address     = None
            self.derivation  = None
            self.spent       = None
            self.txid        = None
            self.vout        = None
        @classmethod
        def from_dict(cls, d):
            c = cls()
            c.__dict__ = d
            c.txid = binascii.unhexlify(c.txid)
            return c

    def __init__(self):
        self.amount = 0
        self.scriptpubkey = bytearray()
        self.metadata = self.Metadata()

    def eq(self, other):
        return self.metadata.txid == other.metadata.txid and self.metadata.vout == other.metadata.vout

    def update_spent(self, other):
        if self.metadata.spent == other.metadata.spent:
            return False
        self.metadata.spent = other.metadata.spent
        return True
    def update_parent_height(self, other):
        if self.parent_tx.metadata.height == other.parent_tx.metadata.height:
            return False
        self.parent_tx.metadata.height = other.parent_tx.metadata.height
        return True

    def to_dict(self):
        d = deepcopy(self.__dict__)
        if "parent_tx" in d:
            del d["parent_tx"]
        return util.to_dict(d)

    def to_bin(self):
        bin = bytearray()
        stream = TxByteStream(bin)
        stream.write_int(8, self.amount)
        stream.write_varint(len(self.scriptpubkey))
        stream.write_chunk(self.scriptpubkey)
        return bin

    @staticmethod
    def from_txbytestream(stream):
        txout = TxOutput()
        txout.amount = stream.read_int(8)
        txout.scriptpubkey = stream.read_chunk(stream.read_varint())
        txout.parent_tx    = None
        txout.metadata     = None
        return txout

    @classmethod
    def from_dict(cls, d):
        txout = cls()
        txout.amount       = d["amount"]
        txout.scriptpubkey = binascii.unhexlify(d["scriptpubkey"])
        txout.parent_tx    = None
        txout.metadata     = TxOutput.Metadata.from_dict(d["metadata"])
        return txout

class Transaction:
    # self.version    int
    # self.inputs     TxInput[]
    # self.outputs    TxOutput[]
    # self.witnesses  bytes[]
    # self.locktime   int
    # ---------------
    # self.metadata

    class Metadata:
        # self.txid
        # self.height
        # self.block_hash
        pass

    def __init__(self):
        self.version = 2
        self.inputs = []
        self.outputs = []
        self.witnesses = []
        self.locktime = 0

    def has(self, utxo):
        for input in self.inputs:
            if input.txid == utxo.metadata.txid and input.vout == utxo.metadata.vout:
                return True
        return False

    def add(self, utxo):
        for input in self.inputs:
            if input.txid == utxo.metadata.txid and input.vout == utxo.metadata.vout:
                return vin
        txin = TxInput()
        txin.txid = utxo.metadata.txid
        txin.vout = utxo.metadata.vout
        txin.scriptsig = bytearray()
        txin.sequence = 0
        txin.parent_tx = self
        txin.txoutput = utxo
        self.inputs.append(txin)
        self.witnesses.append([])

        return len(self.inputs) - 1

    def has_segwit(self):
        for input in self.inputs:
            script_type = scriptVM.identify_scriptpubkey(input.txoutput.scriptpubkey)
            if script_type in (scriptVM.P2WPKH, scriptVM.P2WSH):
                return True

    def to_bin(self, with_segwit=True):
        bin = bytearray()
        stream = TxByteStream(bin)
        stream.write_int(4, self.version)
        has_segwit = self.has_segwit()
        if has_segwit and with_segwit:
            stream.write(0x00)
            stream.write(0x01)
        stream.write_varint(len(self.inputs))
        for input in self.inputs:
            bin.extend(input.to_bin())
        stream.write_varint(len(self.outputs))
        for output in self.outputs:
            bin.extend(output.to_bin())

        if has_segwit and with_segwit:
            segwit_bin = bytearray()
            segwit_stream = TxByteStream(segwit_bin)
            for entries in self.witnesses:
                segwit_stream.write_varint(len(entries))
                for entry in entries:
                    segwit_stream.write_varint(len(entry))
                    segwit_stream.write_chunk(entry)
            stream.write_chunk(segwit_bin)

        stream.write_int(4, self.locktime)
        return bin

    def get_approximate_size(self):
        sig_size = 72
        key_size = 33

        size = 4
        size += len(util.to_varint_bytes(len(self.inputs)))
        for input in self.inputs:
            size += 32 + 4
            if len(input.scriptsig) > 0:
                scriptsig_size = len(input.scriptsig)
            elif input.txoutput is not None:
                script_type = scriptVM.identify_scriptpubkey(input.txoutput.scriptpubkey)
                if script_type == scriptVM.P2PK:
                    scriptsig_size = sig_size
                elif script_type == scriptVM.P2PKH:
                    scriptsig_size = key_size + sig_size + 2
                elif script_type == scriptVM.P2SH:
                    scriptsig_size = 1 # can't tell
                elif script_type == scriptVM.P2MS:
                    # OP_1 is 81. i guess we won't have a multisig with 0 signatures required...
                    sig_count = input.txoutput.outputs[input.vout].scriptpubkey[-1] - 80
                    scriptsig_size = 1 + sig_count * sig_size
                elif script_type == scriptVM.P2WPKH:
                    scriptsig_size = 0 # it's in witnesses
                elif script_type == scriptVM.P2WSH:
                    scriptsig_size = 0 # it's in witnesses
                elif script_type == scriptVM.P2TR:
                    scriptsig_size = 0 # it's in witnesses
            size += len(util.to_varint_bytes(scriptsig_size))
            size += scriptsig_size
            size += 4
        size += len(util.to_varint_bytes(len(self.outputs)))
        for output in self.outputs:
            size += 8
            if len(output.scriptpubkey):
                size += len(util.to_varint_bytes(len(output.scriptpubkey)))
                size += len(output.scriptpubkey)
        segwit_size = 0
        if self.has_segwit():
            segwit_size = 2
            for entries in self.witnesses:
                segwit_size += len(util.to_varint_bytes(len(entries)))
                for entry in entries:
                    segwit_size += len(util.to_varint_bytes(len(entry)))
                    segwit_size += len(entry)
        size += 4
        return size+segwit_size, size+segwit_size/4

    @classmethod
    def from_hex(cls, hex_str):
        return cls.from_bin(binascii.unhexlify(hex_str))
    @staticmethod
    def from_bin(bin):
        stream = TxByteStream(bin)

        t = Transaction()
        t.version = stream.read_int(4)
        has_segwit = stream.peek() == 0
        if has_segwit:
            assert stream.read_chunk(2)[1] == 1

        t.inputs = []
        for i in range(stream.read_varint()):
            txin = TxInput.from_txbytestream(stream)
            txin.parent_tx = t
            t.inputs.append(txin)
            t.witnesses.append([])

        t.outputs = []
        for i in range(stream.read_varint()):
            txout = TxOutput.from_txbytestream(stream)
            txout.parent_tx = t
            t.outputs.append(txout)

        if has_segwit:
            t.witnesses = []
            for idx in range(len(t.inputs)):
                entries = []
                wit_count = stream.read_varint()
                for i in range(wit_count):
                    wit_length = stream.read_varint()
                    wit_script = stream.read_chunk(wit_length)
                    entries.append(wit_script)
                t.witnesses.append(entries)

        t.locktime = stream.read_int(4)
        return t

    #@staticmethod from_dict(d):
    #    t = Transaction()
    #    t.__dict__ = d
    #    t.inputs  = [TxInput .from_dict(i) for i in t. inputs]
    #    t.outputs = [TxOutput.from_dict(o) for o in t.outputs]
    #    metadata = Transaction.Metadata()
    #    metadata.__dict__ = t.metadata
    #    t.metadata = metadata
    #    return t

    def get_binary_for_segwit_signature(self, vin, hashtype):
        empty_hash = bytearray([0]*32)

        if (hashtype & 0x80) != SIGHASH_ANYONECANPAY:
            prevouts = bytearray()
            for input in self.inputs:
                prevouts.extend(input.txid[::-1])
                prevouts.extend(bytes([ input.vout     &0xFF]))
                prevouts.extend(bytes([(input.vout>> 8)&0xFF]))
                prevouts.extend(bytes([(input.vout>>16)&0xFF]))
                prevouts.extend(bytes([(input.vout>>24)&0xFF]))
            hash_prevouts = hashlib.sha256(hashlib.sha256(prevouts).digest()).digest()
        else:
            hash_prevouts = empty_hash

        if (hashtype & 0x80) != SIGHASH_ANYONECANPAY and (hashtype & 0x1f) != SIGHASH_SINGLE and (hashtype & 0x1f) != SIGHASH_NONE:
            sequences = bytearray()
            for input in self.inputs:
                sequences.extend(bytes([ input.sequence     &0xFF]))
                sequences.extend(bytes([(input.sequence>> 8)&0xFF]))
                sequences.extend(bytes([(input.sequence>>16)&0xFF]))
                sequences.extend(bytes([(input.sequence>>24)&0xFF]))
            hash_sequences = hashlib.sha256(hashlib.sha256(sequences).digest()).digest()
        else:
            hash_sequences = empty_hash

        if (hashtype & 0x1f) != SIGHASH_SINGLE and (hashtype & 0x1f) != SIGHASH_NONE:
            outs = bytearray()
            for out in self.outputs:
                outs.extend(out.to_bin())
            hash_outs = hashlib.sha256(hashlib.sha256(outs).digest()).digest()
        elif (hashtype & 0x1f) == SIGHASH_SINGLE and vin < len(self.outputs):
            outs = self.outputs[vin].to_bin()
            hash_outs = hashlib.sha256(hashlib.sha256(outs).digest()).digest()
        else:
            hash_outs = empty_hash

        preimage = bytearray()
        stream = TxByteStream(preimage)
        stream.write_int(4, self.version)
        stream.write_chunk(hash_prevouts)
        stream.write_chunk(hash_sequences)
        stream.write_chunk(self.inputs[vin].txid[::-1])
        stream.write_int(4, self.inputs[vin].vout) # outpoint
        scriptcode = self.inputs[vin].make_script_code()
        stream.write_varint(len(scriptcode))
        stream.write_chunk(scriptcode)
        stream.write_int(8, self.inputs[vin].txoutput.amount)
        stream.write_int(4, self.inputs[vin].sequence)
        stream.write_chunk(hash_outs)
        stream.write_int(4, self.locktime)
        stream.write_int(4, hashtype)
        return preimage

    def get_binary_for_legacy_signature(self, vin, sighash_type):
        tx_copy = deepcopy(self)

        if tx_copy.inputs[vin].txoutput is None:
            raise
        else:
            subscript = tx_copy.inputs[vin].txoutput.scriptpubkey

        for input in tx_copy.inputs:
            input.scriptsig = bytearray()
        tx_copy.inputs[vin].scriptsig = subscript
        # TODO: filter subscript. check the rules

        if sighash_type&3 == SIGHASH_ALL:
            pass
        elif sighash_type&3 == SIGHASH_NONE:
            tx_copy.outputs = []
            for i in range(0,vin):
                tx_copy.inputs[i].sequence = 0
            for i in range(vin+1,len(tx_copy.inputs)):
                tx_copy.inputs[i].sequence = 0
        elif sighash_type&3 == SIGHASH_SINGLE:
            tx_copy.outputs = tx_copy.outputs[0:vin+1]
            for output in tx_copy.outputs[0:-1]:
                output.amount = -1
                output.scriptpubkey = bytearray()
            for i in range(0,vin):
                tx_copy.inputs[i].sequence = 0
            for i in range(vin+1,len(tx_copy.inputs)):
                tx_copy.inputs[i].sequence = 0
        if sighash_type&0x80 == SIGHASH_ANYONECANPAY:
            tx_copy.inputs = [tx_copy.inputs[vin]]

        tx_bin = tx_copy.to_bin(with_segwit=False)
        tx_bin.append(sighash_type)
        tx_bin += b"\x00\x00\x00"
        return tx_bin

    def get_binary_for_signature(self, vin, sighash_type):
        input = self.inputs[vin]
        utxo = input.txoutput
        script_type = scriptVM.identify_scriptpubkey(utxo.scriptpubkey)
        if script_type == scriptVM.P2PKH:
            return self.get_binary_for_legacy_signature(vin, sighash_type)
        elif script_type == scriptVM.P2WPKH:
            return self.get_binary_for_segwit_signature(vin, sighash_type)
        else:
            print("I do not know how to serialize the transaction for this type of script")
            raise

    def verify(self, vin):
        if vin >= len(self.inputs):
            return None
        input = self.inputs[vin]
        script_type = scriptVM.identify_scriptpubkey(input.txoutput.scriptpubkey)

        if script_type == scriptVM.P2PK or script_type == scriptVM.P2PKH:
            if not input.scriptsig or len(input.scriptsig) == 0:
                return None

        if script_type == scriptVM.P2PK:
            full_script = input.scriptsig + input.txoutput.scriptpubkey
        elif script_type == scriptVM.P2SH:
            return False
        elif script_type == scriptVM.P2MS:
            return False
        elif script_type == scriptVM.P2PKH:
            full_script = input.scriptsig + input.txoutput.scriptpubkey
        elif script_type == scriptVM.P2WPKH:
            witness = bytearray()
            stream = scriptVM.ScriptByteStream(witness)
            for item in self.witnesses[vin]:
                stream.add_chunk(item)
            full_script = witness + input.scriptsig + scriptVM.make_P2PKH_scriptpubkey(self.inputs[vin].txoutput.scriptpubkey[2:])
        elif script_type == scriptVM.P2WSH:
            return False
        elif script_type == scriptVM.P2TR:
            return False
        else:
            return False

        return scriptVM.RunnerVM.run(self, vin, full_script)

    def sign_one(self, sighash_type, vin, wallets=None, private_key=None):
        input = self.inputs[vin]
        utxo = input.txoutput
        if private_key is None and wallets is None:
            return
        if wallets is not None:
            if utxo.metadata.wallet_name is None:
                return False
            wallet = wallets[utxo.metadata.wallet_name]
            if wallet is None:
                return False
            derivation = utxo.metadata.derivation
            private_key = wallet.privkey(derivation)
            pubkey = wallet.pubkey(derivation)
        else:
            sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
            pubkey = sk.verifying_key.to_string("compressed")

        script_type = scriptVM.identify_scriptpubkey(utxo.scriptpubkey)
        preimage = self.get_binary_for_signature(vin, sighash_type)
        signature = sign(preimage, private_key) + bytes([sighash_type])
        if script_type == scriptVM.P2PKH:
            input.scriptsig = bytearray()
            stream = scriptVM.ScriptByteStream(input.scriptsig)
            stream.add_chunk(signature)
            stream.add_chunk(pubkey)
            self.witnesses[vin] = [] # empty
        elif script_type == scriptVM.P2WPKH:
            witness = [signature, pubkey]
            input.scriptsig = bytearray() # empty
            self.witnesses[vin] = witness
        else:
            print("Unknown scriptpubkey")
            return False

        return True

    def sign_all(self, wallets, sighash_type):
        for vin in range(0, len(self.inputs)):
            self.sign_one(sighash_type, vin, wallets=wallets)

    def get_affected_inout(self, input_idxs_set):
        all_inputs  = False
        all_outputs = False
        affected_inputs = input_idxs_set
        affected_outputs = set()
        for i in input_idxs_set:
            input = self.inputs[i]
            sighashes = scriptVM.get_signatures_sighashes(input.scriptsig)
            anyonecanpay_sighashes = [s for s in sighashes if (s & SIGHASH_ANYONECANPAY) == 0]
            if len(anyonecanpay_sighashes) > 0:
                affected_inputs = set([idx for idx in range(0, len(self.inputs))])
                all_inputs = True
            for sighash in sighashes:
                if (sighash & 0xF) == SIGHASH_ALL:
                    affected_outputs = set([idx for idx in range(0, len(self.outputs))])
                    all_outputs = True
                    break
                elif (sighash & 0xF) == SIGHASH_SINGLE:
                    affected_outputs.add(i)
            if all_inputs and all_outputs:
                break
        return affected_inputs, affected_outputs

    def has_any_signature(self):
        for input in self.inputs:
            if len(scriptVM.get_signatures(input.scriptsig)) > 0:
                return True
        return False

    def __repr__(self):
        return json.dumps(util.to_dict(self), indent=2)

def sign(preimage, private_key):
    tx_hash = hashlib.sha256(preimage).digest()
    vk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    while True:
        signature = vk.sign(tx_hash, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der)
        if ourCrypto.is_signature_standard(signature):
            break
    return signature

if __name__ == "__main__":
    tx = Transaction.from_hex('0100000002fff7f7881a8099afa6940d42d1e7f6362bec38171ea3edf433541db4e4ad969f0000000000eeffffffef51e1b804cc89d182d279655c3aa89e815b1b309fe287d9b2b55d57b90ec68a0100000000ffffffff02202cb206000000001976a9148280b37df378db99f66f85c95a783a76ac7a6d5988ac9093510d000000001976a9143bde42dbee7e4dbe6a21b2d50ce2f0167faa815988ac11000000')
    import explorer
    print(tx)
    out0 = TxOutput()
    out0.amount = 0x2540BE40
    out0.scriptpubkey = binascii.unhexlify('2103c9f4836b9a4f77fc0d81f7bcb01b7f1b35916864b9476c241ce9fc198bd25432ac')
    out1 = TxOutput()
    out1.amount = 0x23C34600
    out1.scriptpubkey = binascii.unhexlify('00141d0f172a0ecb48aee1be1f2687d2963ae33f71a1')
    tx.inputs[0].txoutput = out0
    tx.inputs[1].txoutput = out1
    print(tx)
    hash_preimage = tx.get_binary_for_segwit_signature(1, SIGHASH_ALL)
    print(hash_preimage.hex())
    assert hash_preimage == binascii.unhexlify('0100000096b827c8483d4e9b96712b6713a7b68d6e8003a781feba36c31143470b4efd3752b0a642eea2fb7ae638c36f6252b6750293dbe574a806984b8e4d8548339a3bef51e1b804cc89d182d279655c3aa89e815b1b309fe287d9b2b55d57b90ec68a010000001976a9141d0f172a0ecb48aee1be1f2687d2963ae33f71a188ac0046c32300000000ffffffff863ef3e1a92afbfdb97f31ad0fc7683ee943e9abcf2501590ff8f6551f47e5e51100000001000000')


import io
import binascii
import json
import util

from copy import deepcopy

SIGHASH_ALL    = 1
SIGHASH_NONE   = 2
SIGHASH_SINGLE = 3
SIGHASH_ANYONECANPAY = 0x80

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
    def write_chunk(self, bytes):
        self.buffer.extend(bytes)
    def write_int(self, size, value):
        while size > 0:
            self.buffer.append(value & 0xFF)
            value >>= 8
            size -= 1
    def write_varint(self, value):
        if value < 0xFD:
            self.buffer.append(value)
        elif value <= 0xFFFF:
            self.write(0xFD)
            self.write_int(2, value)
        elif value <= 0xFFFFFFFF:
            self.write(0xFE)
            self.write_int(4, value)
        else:
            self.write(0xFF)
            self.write_int(8, value)


class TxInput:
    # self.txid
    # self.vout
    # self.scriptsig
    # self.sequence
    # ---------------
    # self.parent_tx
    # self.txoutput

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
            pass
        @classmethod
        def from_dict(cls, d):
            c = cls()
            c.__dict__ = d
            c.txid = binascii.unhexlify(c.txid)
            return c

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
    # self.has_segwit bool
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
        self.version = 1
        self.has_segwit = False
        self.inputs = []
        self.outputs = []
        self.witnesses = []
        self.locktime = 0

    def to_bin(self):
        bin = bytearray()
        stream = TxByteStream(bin)
        stream.write_int(4, self.version)
        if self.has_segwit:
            stream.write(0x00)
            stream.write(0x01)
        stream.write_varint(len(self.inputs))
        for input in self.inputs:
            bin.extend(input.to_bin())
        stream.write_varint(len(self.outputs))
        for output in self.outputs:
            bin.extend(output.to_bin())
        if self.has_segwit:
            raise NotImplementedError
        stream.write_int(4, self.locktime)
        return bin

    @classmethod
    def from_hex(cls, hex_str):
        return cls.from_bin(binascii.unhexlify(hex_str))
    @staticmethod
    def from_bin(bin):
        stream = TxByteStream(bin)

        t = Transaction()
        t.version = stream.read_int(4)
        t.has_segwit = stream.peek() == 0
        if t.has_segwit:
            assert stream.read_chunk(2)[1] == 1

        t.inputs = []
        for i in range(stream.read_varint()):
            txin = TxInput.from_txbytestream(stream)
            txin.parent_tx = t
            t.inputs.append(txin)

        t.outputs = []
        for i in range(stream.read_varint()):
            txout = TxOutput.from_txbytestream(stream)
            txout.parent_tx = t
            t.outputs.append(txout)

        if t.has_segwit:
            t.witnesses = []
            wit_count = stream.read_varint()
            for i in range(wit_count):
                wit_length = stream.read_varint()
                wit_script = stream.read_chunk(wit_length)
                t.witnesses.append(wit_script)

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

    def strip_for_signature(self, vin, sighash):
        if self.inputs[vin].txoutput is None:
            raise
        else:
            subscript = self.inputs[vin].txoutput.scriptpubkey

        for input in self.inputs:
            input.scriptsig = b'\x00'
        self.inputs[vin].scriptsig = subscript

        if sighash&3 == SIGHASH_ALL:
            pass
        elif sighash&3 == SIGHASH_NONE:
            self.outputs = []
            for i in range(0,vin):
                self.inputs[i].sequence = 0
            for i in range(vin+1,len(self.inputs)):
                self.inputs[i].sequence = 0
        elif sighash&3 == SIGHASH_SINGLE:
            self.outputs = self.outputs[0:vin+1]
            for output in self.outputs[0:-1]:
                output.amount = -1
                output.scriptpubkey = bytearray()
            for i in range(0,vin):
                self.inputs[i].sequence = 0
            for i in range(vin+1,len(self.inputs)):
                self.inputs[i].sequence = 0
        if sighash&0x80 == SIGHASH_ANYONECANPAY:
            self.inputs = [self.inputs[vin]]

    def __repr__(self):
        return json.dumps(util.to_dict(self), indent=2)




import io
import binascii
import json
import util

from copy import deepcopy

class TxByteStream:
    def __init__(self, bytes_buffer):
        self.buffer = bytes_buffer
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
        del d["parent_tx"]
        return d

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
        txin.txid       = d["txid"]
        txin.vout       = d["vout"]
        txin.scriptsig  = d["scriptsig"]
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
            return c

    def to_dict(self):
        d = deepcopy(self.__dict__)
        del d["parent_tx"]
        return util.to_dict(d)

    @staticmethod
    def from_txbytestream(stream):
        txout = TxInput()
        txout.amount = stream.read_int(8)
        txout.scriptpubkey = stream.read_chunk(stream.read_varint())
        txout.parent_tx    = None
        txout.metadata     = None
        return txout

    @classmethod
    def from_dict(cls, d):
        txout = cls()
        txout.amount       = d["amount"]
        txout.scriptpubkey = d["scriptpubkey"]
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


    def __repr__(self):
        return json.dumps(util.to_dict(self), indent=2)

if __name__ == "__main__":
    tx_hex = '020000000186ef0d3c482f2eda2e1e1429fb27e8bb499d4cf47bfb070c18aad024ec2ecaea050000006a473044022054f10c0b888d149f7ef70f58586582b81d396fd8aa4ec959c22446bf14d80da502200b2ce0e64ea416c177eaf817f8d3bdb464b6126c01a36d9de960f45a4f1f46bf012103c9039f05d2260068c372656ee7e642f62cce37c6f53602bf995530be49d0dfc8ffffffff0628ad0200000000001976a914b4b4bebdcdc66e9706950b18d881568b04a44d1888ac4bd001000000000017a9141acd9b2b59d022d764685467c5ce7f42d5884a5d878a3c4101000000001976a914b10ddcc04f00fe99c3fa89e5d83d5b14d2f71c3a88ac09be02000000000017a9145de37aa191e2d5a6ea02b4d0c613b1e2664a3a898793150300000000001600142c76bd34431176904b2d56831f74fc844f4789102379b410000000001976a9142c311ac7324b51d37dbbee63dd1bfbdb7a056d6c88ac00000000'
    #s = TxByteStream(binascii.unhexlify(tx_hex))
    tx = Transaction.from_hex(tx_hex)
    print(tx)

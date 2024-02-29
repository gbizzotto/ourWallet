import io
import hashlib
import ecdsa
import binascii
import bip32utils
import bech32

from bip32utils.BIP32Key import PREFIX_TESTNET_SH, PREFIX_MAINNET_SH, PREFIX_MAINNET_PKH, PREFIX_TESTNET_PKH

from copy import deepcopy
from hashlib import sha256

import transactions

P2PK   = 0
P2PKH  = 1
P2SH   = 2
P2MS   = 3
P2WPKH = 4
P2WSH  = 5
P2TR   = 6

def identify_scriptpubkey(script):
    parsed_script = ScriptByteStream(script).read_all()
    if len(parsed_script) == 2 and parsed_script[1] == RunnerVM.OP_CHECKSIG:
        return P2PK
    elif len(parsed_script) == 5 \
            and parsed_script[0] == RunnerVM.OP_DUP \
            and parsed_script[1] == RunnerVM.OP_HASH160 \
            and parsed_script[3] == RunnerVM.OP_EQUALVERIFY \
            and parsed_script[4] == RunnerVM.OP_CHECKSIG:
        return P2PKH
    elif len(parsed_script) == 3 and parsed_script[0] == RunnerVM.OP_HASH160 and parsed_script[2] == RunnerVM.OP_EQUAL:
        return P2SH
    elif len(parsed_script) >= 4 and parsed_script[-1] == RunnerVM.OP_CHECKMULTISIG \
            and RunnerVM.OP_1 <= parsed_script[-2] <= RunnerVM.OP_16 \
            and RunnerVM.OP_1 <= parsed_script[ 0] <= RunnerVM.OP_16:
        n = parsed_script[-2]
        if len(parsed_script) == n+4:
            return P2MS
    elif len(parsed_script) == 2 and parsed_script[0] == RunnerVM.OP_0:
        if len(parsed_script[1]) == 20:
            return P2WPKH
        elif  len(parsed_script[1]) == 32:
            return P2WSH
    elif len(parsed_script) == 2 and parsed_script[0] == RunnerVM.OP_1 and len(parsed_script[1]) == 32:
        return P2TR
    return None

def get_address(script, testnet):
    parsed_script = ScriptByteStream(script).read_all()
    if len(parsed_script) == 2 and parsed_script[1] == RunnerVM.OP_CHECKSIG:
        return parsed_script[0].hex()
    elif len(parsed_script) == 5 \
            and parsed_script[0] == RunnerVM.OP_DUP \
            and parsed_script[1] == RunnerVM.OP_HASH160 \
            and parsed_script[3] == RunnerVM.OP_EQUALVERIFY \
            and parsed_script[4] == RunnerVM.OP_CHECKSIG:
        addressversion = PREFIX_MAINNET_PKH if not testnet else PREFIX_TESTNET_PKH
        vh160 = addressversion + parsed_script[2]
        return bip32utils.Base58.check_encode(vh160)
    elif len(parsed_script) == 3 and parsed_script[0] == RunnerVM.OP_HASH160 and parsed_script[2] == RunnerVM.OP_EQUAL:
        addressversion = PREFIX_MAINNET_SH if not testnet else PREFIX_TESTNET_SH
        addressBytes = hashlib.new('ripemd160', sha256(parsed_script[1]).digest()).digest()
        vh160 = addressversion + parsed_script[1]
        return bip32utils.Base58.check_encode(vh160)
    elif len(parsed_script) >= 4 and parsed_script[-1] == RunnerVM.OP_CHECKMULTISIG \
            and RunnerVM.OP_1 <= parsed_script[-2] <= RunnerVM.OP_16 \
            and RunnerVM.OP_1 <= parsed_script[ 0] <= RunnerVM.OP_16:
        n = parsed_script[-2]
        if len(parsed_script) == n+4:
            return "Multisig"
    elif len(parsed_script) == 2 and parsed_script[0] == RunnerVM.OP_0:
        if len(parsed_script[1]) == 20:
            return bech32.encode('bc' if not testnet else 'tb', 0, parsed_script[1])
        elif  len(parsed_script[1]) == 32:
            return bech32.encode('bc' if not testnet else 'tb', 0, parsed_script[1])
    elif len(parsed_script) == 2 and parsed_script[0] == RunnerVM.OP_1 and len(parsed_script[1]) == 32:
        return bech32.encode('bc' if not testnet else 'tb', 0, parsed_script[1])
    return None

def address_is_testnet(address):
    return address[0] == "m" or address[0] == "n" or address[0] == '2' or address[0:4] == "tb1q" or address[0:4] == "tb1p"

def address_is_mainnet(address):
    return address[0] == "1" or address[0] == '3' or address[0:4] == "bc1q" or address[0:4] == "bc1p"

def address_type(address):
    if len(address) == 0:
        return None
    if address[0] == '1' or address[0] == "m" or address[0] == "n":
        return P2PKH
    if address[0] == '3' or address[0] == '2':
        return P2SH
    if address[:4] == 'bc1q' or address[:4] == 'tb1q':
        return P2WPKH
    if address[:4] == 'bc1p' or address[:4] == 'tb1p':
        return P2TR

def make_P2PKH_scriptpubkey(bin_address):
    return bytearray([0x76, 0xa9, len(bin_address)]) + bin_address + bytes([0x88, 0xac])

def make_P2SH_scriptpubkey(bin_address):
    return bytearray([0xa9, len(bin_address)]) + bin_address + bytes([0x87])

def make_P2PWPKH_scriptpubkey(bin_address):
    return bytes([0x00, len(bin_address)]) + bin_address

def get_signatures(scriptsig):
    script_elements = ScriptByteStream(scriptsig).read_all()
    return [elm for elm in script_elements if len(elm) > 70 and elm[0] == 0x30]

def get_signatures_sighashes(scriptsig):
    return [elm[-1] for elm in get_signatures(scriptsig)]

def contains_anyonecanpay_sighash(scriptsig):
    script_elements = ScriptByteStream(scriptsig).read_all()
    for elm in script_elements:
        if len(elm) > 70 and elm[0] == 0x30:
            # probably a signature
            if elm[-1] & transactions.SIGHASH_ANYONECANPAY == 0:
                return True
    return False

class ScriptByteStream:
    def __init__(self, bytes_buffer):
        self.buffer = bytes_buffer
        self.stream = io.BufferedReader(io.BytesIO(self.buffer))
    def peek(self):
        if self.eof():
            return None
        return self.buffer[self.stream.tell()]
    def eof(self):
        return self.stream.tell() >= len(self.buffer)
    def read_all(self):
        result = []
        while not self.eof():
            result.append(self.next())
        return result
    def read_chunk(self, size):
        return self.stream.read(size)
    def read_byte(self):
        return self.read_chunk(1)[0]
    def read_int(self, size):
        result = 0
        shift = 0
        while size > 0:
            result += self.read_chunk(1)[0] << shift
            size -= 1
            shift += 8
        return result
    def next(self):
        op = self.read_byte()
        if op >= 1 and op < RunnerVM.OP_PUSHDATA1:
            return self.read_chunk(op)
        elif op == RunnerVM.OP_PUSHDATA1:
            op = self.read_byte()
            return self.read_chunk(op)
        elif op == RunnerVM.OP_PUSHDATA2:
            op = self.read_int(2)
            return self.read_chunk(op)
        elif op == RunnerVM.OP_PUSHDATA4:
            op = self.read_int(4)
            return self.read_chunk(op)
        else:
            return op

    def add_byte(self, v):
        self.buffer.append(v)
    def add_int(self, v, size):
        for i in range(0,size):
            self.add_byte(v&0xFF)
            v >>= 8
    def add_chunk(self, chunk):
        if len(chunk) < RunnerVM.OP_PUSHDATA1:
            self.add_byte(len(chunk))
        elif len(chunk) <= 0xFF:
            self.add_byte(RunnerVM.OP_PUSHDATA1)
            self.add_byte(len(chunk))
        elif len(chunk) <= 0xFFFF:
            self.add_byte(RunnerVM.OP_PUSHDATA2)
            self.add_int(len(chunk), 2)
        else:
            self.add_byte(RunnerVM.OP_PUSHDATA4)
            self.add_int(len(chunk), 4)
        self.buffer.extend(chunk)


    #def read_varint(self):
    #    c = self.read_int(1)
    #    if c < 0xFD:
    #        return c
    #    elif c == 0xFD:
    #        return self.read_int(2)
    #    elif c == 0xFE:
    #        return self.read_int(4)
    #    elif c == 0xFF:
    #        return self.read_int(8)

class InvalidOpcode(Exception):
    def __init__(self, op):
        super().__init__(PrinterVM.to_string(op))

class RunnerVM:
    @classmethod
    def run(cls, tx, vin, full_script, debug=False):
        stream = ScriptByteStream(full_script)
        stack = []
        try:
            while not stream.eof():
                if debug:
                    cls.print_stack(stack)
                op = stream.next()
                if debug:
                    print("op:", PrinterVM.to_string(op))
                if isinstance(op, bytes):
                    stack.append(op)
                elif op == cls.OP_FALSE:
                    stack.append(0)
                elif op == cls.OP_TRUE:
                    stack.append(1)
                elif op >= 82 and op <= 92:
                    stack.append(op-80)
                elif op == 80:
                    raise InvalidOpcode(op)
                elif op == cls.OP_DUP:
                    stack.append(stack[-1])
                elif op == cls.OP_HASH160:
                    ok = hashlib.sha256(stack[-1]).digest()
                    hash = hashlib.new('ripemd160', ok).digest()
                    del stack[-1]
                    stack.append(hash)
                elif op == cls.OP_EQUALVERIFY:
                    if stack[-1] != stack[-2]:
                        return False
                    del stack[-1]
                    del stack[-1]
                elif op == cls.OP_CHECKSIG:
                    pubkey = stack[-1]
                    del stack[-1]
                    signature = stack[-1]
                    del stack[-1]
                    sighash_type = signature[-1]
                    signature = signature[:-1]
                    preimage = tx.get_binary_for_signature(vin, sighash_type)
                    # append 4 bytes of sighash_type
                    data_to_sign = hashlib.sha256(preimage).digest()
                    vk = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
                    try:
                        if vk.verify(signature, data_to_sign, hashlib.sha256, sigdecode=ecdsa.util.sigdecode_der):
                            stack.append(1)
                        else:
                            stack.append(0)
                    except:
    
                        stack.append(0)
                else:
                    raise NotImplementedError(PrinterVM.to_string(op))
            if debug:
                cls.print_stack(stack)
            if len(stack) == 0 or stack[-1] == 0:
                return False
            return True
        except:
            return False

    @classmethod
    def print_stack(cls, stack):
        print("Stack:")
        i = 0
        for o in stack:
            if isinstance(o, bytes):
                print("   ", i, ":", o.hex())
            else:
                print("   ", i, ":", o)
            i += 1

    OP_FALSE = 0
    OP_0 = 0
    # OP_PUSHDATA0 from 1 to 75
    OP_PUSHDATA1 = 76
    OP_PUSHDATA2 = 77
    OP_PUSHDATA4 = 78
    OP_1NEGATE = 79
    OP_RESERVED = 80
    OP_TRUE = 81
    OP_1 = 81
    # OP_N
    OP_16 = 96
    OP_NOP = 97
    OP_VER = 98
    OP_IF  = 99
    OP_NOTIF = 100
    OP_VERIF = 101
    OP_VERNOTIF = 102
    OP_ELSE = 103
    OP_ENDIF = 104
    OP_VERIFY = 105
    OP_RETURN = 106
    OP_TOALTSTACK = 107
    OP_FROMALTSTACK = 108
    OP_2DROP = 109
    OP_2DUP = 110
    OP_3DUP = 111
    OP_2OVER = 112
    OP_2ROT = 113
    OP_2SWAP = 114
    OP_IFDUP = 115
    OP_DEPTH = 116
    OP_DROP = 117
    OP_DUP = 118
    OP_NIP = 119
    OP_OVER = 120
    OP_PICK = 121
    OP_ROLL = 122
    OP_ROT = 123
    OP_SWAP = 124
    OP_TUCK = 125
    OP_CAT = 126
    OP_SUBSTR = 271
    OP_LEFT = 128
    OP_RIGHT = 129
    OP_SIZE = 130
    OP_INVERT = 131
    OP_AND = 132
    OP_OR = 133
    OP_XOR = 134
    OP_EQUAL = 135
    OP_EQUALVERIFY = 136
    OP_RESERVED1 = 137
    OP_RESERVED2 = 138
    OP_1ADD = 139
    OP_1SUB = 140
    OP_2MUL = 141
    OP_2DIV = 142
    OP_NEGATE = 143
    OP_ABS = 144
    OP_NOT = 145
    OP_0NOTEQUAL = 146
    OP_ADD = 147
    OP_SUB = 148
    OP_MUL = 149
    OP_DIV = 150
    OP_MOD = 151
    OP_LSHIFT = 152
    OP_RSHIFT = 153
    OP_BOOLAND = 154
    OP_BOOLOR = 155
    OP_NUMEQUAL = 156
    OP_NUMEQUALVERIFY = 157
    OP_NUMNOTEQUAL = 158
    OP_LESSTHAN = 159
    OP_GREATERTHAN = 160
    OP_LESSTHANOREQUAL = 161
    OP_GREATERTHANOREQUAL = 162
    OP_MIN = 163
    OP_MAX = 164
    OP_WITHIN = 165
    OP_RIPEMD160 = 166
    OP_SHA1 = 167
    OP_SHA256 = 168
    OP_HASH160 = 169
    OP_HASH256 = 170
    OP_CODESEPARATOR = 171
    OP_CHECKSIG = 172
    OP_CHECKSIGVERIFY = 173
    OP_CHECKMULTISIG = 174
    OP_CHECKMULTISIGVERIFY = 175
    OP_NOP1 = 176
    OP_CHECKLOCKTIMEVERIFY = 177
    OP_CHECKSEQUENCEVERIFY = 178
    OP_NOP4 = 179
    OP_NOP5 = 180
    OP_NOP6 = 181
    OP_NOP7 = 182
    OP_NOP8 = 183
    OP_NOP9 = 184
    OP_NOP10 = 185

class PrinterVM:
    @classmethod
    def to_string(cls, op):
        if isinstance(op, bytes):
            return op.hex()
        if op == 0:
            return "OP_FALSE"
        elif op == 80:
            return "OP_RESERVED (invalid)"
        elif op == 81:
            return "OP_TRUE"
        elif op >= 82 and op <= 92:
            return "OP_" + str(op-80)
        else:
            return cls.opcode_names[op-97]
    @classmethod
    def run(cls, bin):
         stream = ScriptByteStream(bin)
         while not stream.eof():
             print(cls.to_string(stream.next()))
    opcode_names = [
        "OP_NOP", # 97
        "OP_VER",
        "OP_IF",
        "OP_NOTIF",
        "OP_VERIF (invalid)",
        "OP_VERNOTIF (invalid)", # 102
        "OP_ELSE",
        "OP_ENDIF",
        "OP_VERIFY",
        "OP_RETURN",
        "OP_TOALTSTACK",
        "OP_FROMALTSTACK", # 108
        "OP_2DROP",
        "OP_2DUP",
        "OP_3DUP",
        "OP_2OVER",
        "OP_2ROT",
        "OP_2SWAP",
        "OP_IFDUP", # 115
        "OP_DEPTH",
        "OP_DROP",
        "OP_DUP",
        "OP_NIP",
        "OP_OVER",
        "OP_PICK",
        "OP_ROLL",
        "OP_ROT",
        "OP_SWAP",
        "OP_TUCK", # 125
        "OP_CAT (disabled)",
        "OP_SUBSTR (disabled)",
        "OP_LEFT (disabled)",
        "OP_RIGHT (disabled)",
        "OP_SIZE", # 130
        "OP_INVERT (disabled)",
        "OP_AND (disabled)",
        "OP_OR (disabled)",
        "OP_XOR (disabled)",
        "OP_EQUAL",
        "OP_EQUALVERIFY", # 136
        "OP_RESERVED1 (invalid)",
        "OP_RESERVED2 (invalid)",
        "OP_1ADD",
        "OP_1SUB",
        "OP_2MUL (disabled)",
        "OP_2DIV (disabled)",
        "OP_NEGATE",
        "OP_ABS",
        "OP_NOT",
        "OP_0NOTEQUAL",
        "OP_ADD",
        "OP_SUB",
        "OP_MUL (disabled)",
        "OP_DIV (disabled)",
        "OP_MOD (disabled)",
        "OP_LSHIFT (disabled)",
        "OP_RSHIFT (disabled)",
        "OP_BOOLAND",
        "OP_BOOLOR",
        "OP_NUMEQUAL",
        "OP_NUMEQUALVERIFY",
        "OP_NUMNOTEQUAL",
        "OP_LESSTHAN",
        "OP_GREATERTHAN",
        "OP_LESSTHANOREQUAL",
        "OP_GREATERTHANOREQUAL",
        "OP_MIN",
        "OP_MAX",
        "OP_WITHIN", #165
        "OP_RIPEMD160",
        "OP_SHA1",
        "OP_SHA256",
        "OP_HASH160",
        "OP_HASH256",
        "OP_CODESEPARATOR",
        "OP_CHECKSIG",
        "OP_CHECKSIGVERIFY",
        "OP_CHECKMULTISIG",
        "OP_CHECKMULTISIGVERIFY",
        "OP_NOP1 (ignored)",
        "OP_CHECKLOCKTIMEVERIFY",
        "OP_CHECKSEQUENCEVERIFY",
        "OP_NOP4 (ignored)",
        "OP_NOP5 (ignored)",
        "OP_NOP6 (ignored)",
        "OP_NOP7 (ignored)",
        "OP_NOP8 (ignored)",
        "OP_NOP9 (ignored)",
        "OP_NOP10 (ignored)",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
        "OP_",
    ]

if __name__ == "__main__":
    #tx_hex = '020000000186ef0d3c482f2eda2e1e1429fb27e8bb499d4cf47bfb070c18aad024ec2ecaea050000006a473044022054f10c0b888d149f7ef70f58586582b81d396fd8aa4ec959c22446bf14d80da502200b2ce0e64ea416c177eaf817f8d3bdb464b6126c01a36d9de960f45a4f1f46bf012103c9039f05d2260068c372656ee7e642f62cce37c6f53602bf995530be49d0dfc8ffffffff0628ad0200000000001976a914b4b4bebdcdc66e9706950b18d881568b04a44d1888ac4bd001000000000017a9141acd9b2b59d022d764685467c5ce7f42d5884a5d878a3c4101000000001976a914b10ddcc04f00fe99c3fa89e5d83d5b14d2f71c3a88ac09be02000000000017a9145de37aa191e2d5a6ea02b4d0c613b1e2664a3a898793150300000000001600142c76bd34431176904b2d56831f74fc844f4789102379b410000000001976a9142c311ac7324b51d37dbbee63dd1bfbdb7a056d6c88ac00000000'
    tx_hex = '0100000001c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd3704000000004847304402204e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd410220181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d0901ffffffff0200ca9a3b00000000434104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac00286bee0000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3ac00000000'
    tx = transactions.Transaction.from_hex(tx_hex)
    print(tx)
    txid = hashlib.sha256(hashlib.sha256(binascii.unhexlify(tx_hex)).digest()).digest()[::-1]
    print("txid:", txid.hex())

    import explorer
    prev_tx = explorer.get_transaction(tx.inputs[0].txid, False)
    tx.inputs[0].txoutput = prev_tx.outputs[tx.inputs[0].vout]
    print("-------")
    #print(tx.inputs[0].scriptsig.hex(), tx.inputs[0].txoutput.scriptpubkey.hex())
    PrinterVM.run(tx.inputs[0].scriptsig)
    PrinterVM.run(tx.inputs[0].txoutput.scriptpubkey)

    full_script = tx.inputs[0].scriptsig + tx.inputs[0].txoutput.scriptpubkey
    print(RunnerVM.run(tx, 0, full_script, debug=True))



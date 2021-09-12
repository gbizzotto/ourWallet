import sys
import requests
import json
import time
import os, os.path
import binascii
import copy

import transactions
import util

cache_folder = './cache/'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

def go_push_transaction(tx, testnet):
    tx_hex = tx.to_bin().hex()

    print("explorer broadcast", tx_hex)

    #blockstream
    network = "testnet/" if testnet else ""
    page = requests.post("https://blockstream.info/"+network+"api/tx", data=tx_hex)
    if page.status_code != 200:
        print("page.status_code", page.status_code)
        print("page.text", page.text)
        return None
    txid = page.text
    print("txid", txid)

    # add it to the local cache
    get_transaction(binascii.unhexlify(txid), testnet)

    # write tx to list of our own
    # TODO evaluate privacy concerns around this
    with open("ourTransactions", "a") as f:
        f.write(tx_hex+"\n")

    return txid

def go_get_transaction_metadata(txid, testnet):
    print("explorer go_get_transaction_metadata", txid.hex(), testnet)

    #blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid.hex())
    if page.status_code != 200:
        print("No metadata for tx", txid.hex())
        return None
    contents = json.loads(page.text)
    metadata = transactions.Transaction.Metadata()
    if contents["status"]["confirmed"]:
        metadata.height     = contents["status"]["block_height"]
        metadata.block_hash = contents["status"]["block_hash"]
    else:
        metadata.height     = None
        metadata.block_hash = None
    return metadata

def get_transaction_metadata(txid, testnet):
    if get_transaction_metadata.cache is None:
        get_transaction_metadata.cache = {}
        # load cache from file
        if os.path.isfile(cache_folder+"txsmd.cache"):
            with open(cache_folder+"txsmd.cache", "r") as f:
                get_transaction_metadata.cache = json.loads(f.read())

    if txid.hex() in get_transaction_metadata.cache and get_transaction_metadata.cache[txid.hex()]["height"] is not None:
        md = transactions.Transaction.Metadata()
        md.__dict__ = copy.copy(get_transaction_metadata.cache[txid.hex()])
    else:
        md = go_get_transaction_metadata(txid, testnet)
        if md is None:
            return None
        # make a copy of md to avoid storing txid in cache as key AND value
        get_transaction_metadata.cache[txid.hex()] = copy.copy(md.__dict__)
        # write cache to file
        with open(cache_folder+"txsmd.cache", "w") as f:
            f.write(json.dumps(get_transaction_metadata.cache))

    md.txid = txid
    return md
get_transaction_metadata.cache = None

def go_get_transaction(txid, testnet):
    print("explorer go_get_transaction", txid.hex())

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid.hex()+"/hex")
    if page.status_code != 200:
        return None, None
    t = transactions.Transaction.from_hex(page.text)
    t.metadata = get_transaction_metadata(txid, testnet)
    return t, page.text

def get_transaction(txid, testnet):
    if get_transaction.cache is None:
        get_transaction.cache = {}
        get_transaction.bincache = {}
        # load cache from file
        if os.path.isfile(cache_folder+"txs.cache"):
            with open(cache_folder+"txs.cache", "r") as f:
                get_transaction.cache = json.loads(f.read())
                for k,v in get_transaction.cache.items():
                    get_transaction.bincache[k] = v
                    get_transaction.cache[k] = transactions.Transaction.from_hex(v)
                    get_transaction.cache[k].metadata = get_transaction_metadata(binascii.unhexlify(k), testnet)

    if txid.hex() not in get_transaction.cache:
        tx, bintx = go_get_transaction(txid, testnet)
        if tx is None:
            return None
        get_transaction.cache[txid.hex()] = tx
        get_transaction.bincache[txid.hex()] = bintx
        # write cache to file
        with open(cache_folder+"txs.cache", "w") as f:
            f.write(json.dumps(get_transaction.bincache))

    return get_transaction.cache[txid.hex()]
get_transaction.cache    = None
get_transaction.bincache = None


def is_output_spent(txid, vout, testnet):
    print("explorer is_output_spent", txid.hex(), vout)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid.hex()+"/outspend/"+str(vout))
    if page.status_code != 200:
        print("page.status_code", page.status_code)
        return False
    return json.loads(page.text)["spent"]

def get_utxo(txid_hex, vout, testnet):
    txid = binascii.unhexlify(txid_hex)
    transaction = get_transaction(txid, testnet)
    if transaction is None:
        txid_hex = txid_hex[::-1]
        txid = binascii.unhexlify(txid_hex)
        transaction = get_transaction(txid, testnet)
    if transaction is None:
        return None

    txout = transaction.outputs[vout]
    txout.parent_tx = transaction
    txout.metadata             = transactions.TxOutput.Metadata()
    txout.metadata.wallet_name = None
    txout.metadata.address     = None
    txout.metadata.derivation  = None
    txout.metadata.spent       = is_output_spent(txid, vout, testnet)
    txout.metadata.txid        = txid
    txout.metadata.vout        = vout
    return txout

def get_utxos(wallet_name, address, derivation, testnet):
    print("explorer get_utxos", address, derivation)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/address/"+address+"/utxo")
    if page.status_code != 200:
        print("page.status_code", page.status_code)
        return []
    utxos = json.loads(page.text)
    result = []
    for u in utxos:
        txid = binascii.unhexlify(u["txid"])
        tx = get_transaction(txid, testnet)
        txout = tx.outputs[u["vout"]]
        txout.parent_tx = tx
        txout.metadata             = transactions.TxOutput.Metadata()
        txout.metadata.wallet_name = wallet_name
        txout.metadata.address     = address
        txout.metadata.derivation  = derivation
        txout.metadata.spent       = is_output_spent(txid, u["vout"], testnet)
        txout.metadata.txid        = txid
        txout.metadata.vout        = u["vout"]
        result.append(txout)
    return result

    # blockcypher

def get_output_scriptpubkey(txid, vout, testnet):
    print("explorer get_output_scriptpubkey", txid.hex() + ":" + vout)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"tx/"+txid)
    if page.status_code != 200:
        print("page.status_code", page.status_code)
        return None
    return binascii.unhexlify(json.loads(page.text)["vout"][vout]["scriptpubkey"])

def get_current_height(testnet):
    epoch = time.time()
    if get_current_height.epoch is not None and epoch < get_current_height.epoch+60:
        return get_current_height.height

    print("explorer get_current_height")
    get_current_height.epoch = epoch

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"/api/blocks/tip/height")
    if page.status_code != 200:
        print("page.status_code", page.status_code)
        return None
    get_current_height.height = int(page.text)
    return get_current_height.height
get_current_height.height = None
get_current_height.epoch  = None

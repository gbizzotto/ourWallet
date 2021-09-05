import sys
import requests
import json
import time
import os.path

import transactions
import util


def get_transaction_metadata(txid, testnet):
    if get_transaction_metadata.cache is None:
        get_transaction_metadata.cache = {}
        # load cache from file
        if os.path.isfile("txsmd.cache"):
            with open("txsmd.cache", "r") as f:
                get_transaction_metadata.cache = json.loads(f.read())

    if txid in get_transaction_metadata.cache:
        md = transactions.Transaction.Metadata()
        md.__dict__ = get_transaction_metadata.cache[txid]
        md.txid = txid
        return md

    print("explorer get_transaction_metadata", txid, testnet)

    #blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid)
    contents = json.loads(page.text)
    metadata            = transactions.Transaction.Metadata()
    metadata.txid       = txid
    metadata.height     = contents["status"]["block_height"]
    metadata.block_hash = contents["status"]["block_hash"]

    get_transaction_metadata.cache[txid] = metadata.__dict__
    del get_transaction_metadata.cache[txid]["txid"]

    # write cache to file
    with open("txsmd.cache", "w") as f:
        f.write(json.dumps(get_transaction_metadata.cache))

    return metadata
get_transaction_metadata.cache = None

def get_transaction(txid, testnet):
    if get_transaction.cache is None:
        get_transaction.cache = {}
        get_transaction.bincache = {}
        # load cache from file
        if os.path.isfile("txs.cache"):
            with open("txs.cache", "r") as f:
                get_transaction.cache = json.loads(f.read())
                for k,v in get_transaction.cache.items():
                    get_transaction.bincache[k] = v
                    get_transaction.cache[k] = transactions.Transaction.from_hex(v)
                    get_transaction.cache[k].metadata = get_transaction_metadata(txid, testnet)

    if txid in get_transaction.cache:
        return get_transaction.cache[txid]

    print("explorer get_transaction", txid)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid+"/hex")
    t = transactions.Transaction.from_hex(page.text)

    get_transaction.bincache[txid] = page.text

    t.metadata = get_transaction_metadata(txid, testnet)

    get_transaction.cache[txid] = t

    # write cache to file
    with open("txs.cache", "w") as f:
        f.write(json.dumps(get_transaction.bincache))

    return t
get_transaction.cache    = None
get_transaction.bincache = None


def is_output_spent(txid, vout, testnet):
    print("explorer is_output_spent", txid, vout)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid+"/outspend/"+str(vout))
    return json.loads(page.text)["spent"]


def get_utxos(address, derivation, testnet):
    print("explorer get_utxos", address, derivation)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/address/"+address+"/utxo")
    utxos = json.loads(page.text)
    result = []
    for u in utxos:
        tx = get_transaction(u["txid"], testnet)
        txout = tx.outputs[u["vout"]]
        txout.parent_tx = tx
        txout.metadata            = transactions.TxOutput.Metadata()
        txout.metadata.address    = address
        txout.metadata.derivation = derivation
        txout.metadata.spent      = is_output_spent(u["txid"], u["vout"], testnet)
        txout.metadata.txid       = u["txid"]
        txout.metadata.vout       = u["vout"]
        result.append(txout)
    return result

    # blockcypher

def get_output_scriptpubkey(txid, vout, testnet):
    print("explorer get_output_scriptpubkey", txid, vout)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"tx/"+txid)
    return json.loads(page.text)["vout"][vout]["scriptpubkey"]

def get_current_height(testnet):
    epoch = time.time()
    print(epoch)
    if get_current_height.epoch is not None and epoch < get_current_height.epoch+60:
        return get_current_height.height

    print("explorer get_current_height")
    get_current_height.epoch = epoch

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"/api/blocks/tip/height")
    get_current_height.height = int(page.text)
    return get_current_height.height
get_current_height.height = None
get_current_height.epoch  = None

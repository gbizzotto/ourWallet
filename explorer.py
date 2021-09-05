import sys
import requests
import json

import transactions


def get_transaction(txid, testnet):
    #if txid in transactions:
    #    return transactions[txid]

    print("explorer get_transaction", txid)

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid+"/hex")
    t = transactions.Transaction.from_hex(page.text)
    #transactions[txid] = t

    page = requests.get("https://blockstream.info/"+network+"api/tx/"+txid)
    contents = json.loads(page.text)
    t.metadata            = transactions.Transaction.Metadata()
    t.metadata.txid       = txid
    t.metadata.height     = contents["status"]["block_height"]
    t.metadata.block_hash = contents["status"]["block_hash"]
    return t


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
    print("explorer get_current_height")

    # blockstream
    network = "testnet/" if testnet else ""
    page = requests.get("https://blockstream.info/"+network+"/api/blocks/tip/height")
    return int(page.text)

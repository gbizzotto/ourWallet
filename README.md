# ourWallet
Full-control BTC wallet

## How to make it work

- install python3 and pip
- run `pip install -r requirements.txt` to download the dependencies
- run `python main.py`

## Goals:

- :heavy_check_mark: Manually choose UTXOs in new TXs
- :heavy_check_mark: Manually set fee
- :heavy_check_mark: Sign individual UTXOs
- :heavy_check_mark: Set nLockTime
- :heavy_check_mark: Manage BIP32 wallets
- :white_check_mark: Allow Dbl spend for better control over RBF
- :white_check_mark: Choose SigHash
- Manage wallets that are a lose collection of private keys
- Export/Import (un)signed TXs
- Write custom Script (as in scriptpubkey and scriptsig)

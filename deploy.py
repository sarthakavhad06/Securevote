"""Compile Voting.sol and deploy it to the configured local Ganache node."""
import json
import os
from pathlib import Path

import solcx
from web3 import Web3

ROOT = Path(__file__).resolve().parent
SOLC_VERSION = "0.8.20"
RPC_URL = os.environ.get("GANACHE_RPC_URL", "http://127.0.0.1:7545")
CANDIDATES = ["Olivia Chen", "Ethan Patel", "Maya Sharma"]


def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    if not w3.is_connected():
        raise SystemExit(f"Cannot connect to Ganache at {RPC_URL}. Start the local chain first.")
    if SOLC_VERSION not in [str(v) for v in solcx.get_installed_solc_versions()]:
        print(f"Downloading Solidity compiler {SOLC_VERSION} (first deployment only)…")
        solcx.install_solc(SOLC_VERSION)
    source = (ROOT / "contracts" / "Voting.sol").read_text(encoding="utf-8")
    compiled = solcx.compile_source(source, output_values=["abi", "bin"], solc_version=SOLC_VERSION)
    _, interface = next(iter(compiled.items()))
    account = w3.eth.accounts[0]
    factory = w3.eth.contract(abi=interface["abi"], bytecode=interface["bin"])
    tx_hash = factory.constructor(CANDIDATES).transact({"from": account})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    if receipt.status != 1 or not receipt.contractAddress:
        raise SystemExit("Contract deployment failed.")
    config = {"address": receipt.contractAddress, "abi": interface["abi"], "chain_id": w3.eth.chain_id, "deployment_tx": tx_hash.hex(), "candidates": CANDIDATES}
    (ROOT / "deployment.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Voting contract deployed: {receipt.contractAddress}")
    print(f"Deployment transaction: {tx_hash.hex()}")
    print(f"Chain ID: {w3.eth.chain_id} | Block: {receipt.blockNumber}")


if __name__ == "__main__":
    main()

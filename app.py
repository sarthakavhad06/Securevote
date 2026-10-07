"""Flask UI for the report's Ethereum/Ganache blockchain voting project."""
import json
import os
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from web3 import Web3

ROOT = Path(__file__).resolve().parent
RPC_URL = os.environ.get("GANACHE_RPC_URL", "http://127.0.0.1:7545")
DEPLOYMENT_FILE = Path(os.environ.get("VOTING_DEPLOYMENT", ROOT / "deployment.json"))
CANDIDATE_NAMES = ["Olivia Chen", "Ethan Patel", "Maya Sharma"]
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-college-demo-change-me")


@app.template_filter("datetime")
def format_timestamp(value):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(value, timezone.utc).strftime("%d %b %Y · %H:%M UTC")


def load_chain():
    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 4}))
    if not w3.is_connected():
        return w3, None, "Ganache is not running. Start Ganache on " + RPC_URL
    if not DEPLOYMENT_FILE.exists():
        return w3, None, "Smart contract not deployed. Run `python deploy.py` first."
    try:
        cfg = json.loads(DEPLOYMENT_FILE.read_text(encoding="utf-8"))
        contract = w3.eth.contract(address=Web3.to_checksum_address(cfg["address"]), abi=cfg["abi"])
        return w3, contract, "Connected to Ganache"
    except Exception as exc:
        return w3, None, f"Deployment configuration error: {exc}"


def dashboard_data(w3, contract):
    accounts = w3.eth.accounts if w3.is_connected() else []
    results = {}
    candidates = []
    if contract:
        for index in range(contract.functions.candidateCount().call()):
            name, _vote_count = contract.functions.candidates(index).call()
            candidates.append(name)
            results[name] = contract.functions.getVotes(index).call()
    latest = w3.eth.get_block("latest") if w3.is_connected() else None
    events = []
    if contract:
        try:
            logs = contract.events.VoteCast().get_logs(from_block=0, to_block="latest")
            for log in logs:
                args = log["args"]
                events.append({"voter": args["voter"], "candidate": candidates[args["candidateId"]], "block": log["blockNumber"], "tx": log["transactionHash"].hex(), "timestamp": w3.eth.get_block(log["blockNumber"])["timestamp"]})
        except Exception:
            events = []
    return accounts, candidates, results, latest, events


@app.get("/")
def index():
    w3, contract, status = load_chain()
    accounts, candidates, results, latest, events = dashboard_data(w3, contract)
    return render_template("index.html", accounts=accounts, candidates=candidates, results=results, latest=latest, events=events, connected=w3.is_connected(), deployed=contract is not None, status=status, chain_id=w3.eth.chain_id if w3.is_connected() else None, contract_address=contract.address if contract else None)


@app.post("/vote")
def cast_vote():
    account = request.form.get("account", "")
    try:
        candidate_id = int(request.form.get("candidate_id", "-1"))
        w3, contract, status = load_chain()
        if not contract:
            raise ValueError(status)
        accounts = [Web3.to_checksum_address(a) for a in w3.eth.accounts]
        account = Web3.to_checksum_address(account)
        if account not in accounts:
            raise ValueError("Choose an unlocked Ganache account.")
        count = contract.functions.candidateCount().call()
        if candidate_id < 0 or candidate_id >= count:
            raise ValueError("Choose a valid candidate.")
        if contract.functions.hasVoted(account).call():
            raise ValueError("This Ganache account has already voted in this election.")
        tx_hash = contract.functions.vote(candidate_id).transact({"from": account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        if receipt.status != 1:
            raise ValueError("The blockchain rejected the transaction.")
        flash(f"Vote recorded on Ethereum block #{receipt.blockNumber}. Transaction: {tx_hash.hex()[:18]}…", "success")
    except Exception as exc:
        flash(str(exc), "error")
    return redirect(url_for("index"))


@app.get("/results")
def results_api():
    w3, contract, status = load_chain()
    if not contract:
        return jsonify({"connected": w3.is_connected(), "deployed": False, "message": status}), 503
    _, candidates, results, _, _ = dashboard_data(w3, contract)
    return jsonify({"connected": True, "deployed": True, "votes": results, "candidates": candidates})


@app.get("/chain_info")
def chain_info():
    w3, contract, status = load_chain()
    connected = w3.is_connected()
    if not connected:
        return jsonify({"connected": False, "message": status}), 503
    latest = w3.eth.get_block("latest")
    return jsonify({"connected": True, "deployed": contract is not None, "chain_id": w3.eth.chain_id, "latest_block": latest.number, "miner": latest.miner, "rpc_url": RPC_URL, "contract_address": contract.address if contract else None, "network": status})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)

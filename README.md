# SecureVote — Blockchain-Based Voting System

A college mini-project implementation based on the supplied report and its UI screenshots. The stack follows the report: **Flask + Python, Solidity, Web3.py, and Ganache**. The Flask app submits votes to an Ethereum-compatible smart contract; vote totals and transaction history are read from the local chain.

## Requirements

- Python 3.10+
- Node.js and npm (for Ganache CLI), or Ganache Desktop
- Internet access for the first install of Python packages and the Solidity compiler

## Windows setup

Open PowerShell in this project folder.

1. Create and activate a virtual environment, then install the Python dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Start a local Ganache chain in a second PowerShell window:

   ```powershell
   npx ganache --server.host 127.0.0.1 --server.port 7545 --chain.chainId 1337
   ```

   For Ganache Desktop, create/start a workspace with RPC server `http://127.0.0.1:7545`. If your RPC URL differs, set `$env:GANACHE_RPC_URL` in both terminals before running the following commands.

3. In the first PowerShell window, deploy the Solidity contract:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python deploy.py
   ```

   On first run, `py-solc-x` downloads Solidity compiler 0.8.20. The deployment script compiles `contracts/Voting.sol`, deploys the contract from Ganache account 0, and writes its address and ABI to `deployment.json`.

4. Start Flask:

   ```powershell
   python app.py
   ```

5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Choose an unlocked Ganache account and candidate, then submit the vote. Ganache mines the contract transaction and the interface shows its transaction hash and block number.

## Features

- Ganache accounts displayed as voter wallet choices.
- Solidity contract validates candidate selection and allows one vote per wallet address.
- Vote counts are stored and incremented on-chain; the Flask server does not maintain a separate tally database.
- Contract `VoteCast` events provide the confirmed vote history.
- Live vote totals and a network panel showing chain ID, latest block, account count, and deployed contract address.
- `GET /results` returns candidate totals as JSON; `GET /chain_info` returns network and contract status.
- Responsive dark interface based on the supplied SecureVote screenshots.

## Demo walkthrough

1. Verify the page reports a connection to Ganache and an open election.
2. Select a Ganache wallet and a candidate, then submit.
3. Confirm the success message displays the mined block and transaction hash.
4. Vote again from the same wallet; the contract rejects the duplicate.
5. Vote from a different wallet and candidate; live totals and confirmed votes update.
6. Open `/chain_info` and `/results` to show the Ethereum network details and contract-derived tally.

## Configuration

The defaults expect Ganache at `http://127.0.0.1:7545`. Set `GANACHE_RPC_URL` to use another local RPC endpoint. Set `PORT` to change the Flask port. Keep `deployment.json` for the current Ganache workspace; restarting Ganache with a reset chain requires running `python deploy.py` again.

## Scope and security

This is a local test-network college prototype, not an election system. Ganache's local node allows the Flask backend to submit transactions from unlocked accounts; voter eligibility is not verified, votes and voter wallet addresses are publicly visible on-chain, and the local chain is not independently decentralized. Real elections require ballot secrecy, strong eligibility controls, coercion resistance, hardened key custody, independent validators, accessibility and legal review, and security audits. Do not use real voter data or wallets.

import json
import os
import time
from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_source, install_solc

# **1️⃣ Install Solidity Compiler**
install_solc("0.8.26")  # Install Solidity compiler version 0.8.26

# **2️⃣ Load Environment Variables**
load_dotenv()

# Web3 connection
web3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
print(f"Connected to blockchain: {web3.is_connected()}")

# Wallet details
private_key = os.getenv("PRIVATE_KEY")
account = web3.eth.account.from_key(private_key)
owner_address = account.address
print(f"Owner Wallet Address: {owner_address}")

# **3️⃣ Smart Contract Source Code**
contract_source_code = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract FitnessReward {
    address public owner;
    mapping(address => bool) public rewardedUsers;  // This mapping keeps track of rewarded addresses
    uint256 public rewardAmount = 0.0001 ether;  
    bool public isTesting = true;  // Toggle this flag for testing (true) vs production (false)

    constructor() {
        owner = msg.sender;
    }

    function completeQuiz() public {
        // Only enforce one-time reward check when not testing
        if (!isTesting) {
            require(!rewardedUsers[msg.sender], "You have already claimed your reward.");
            rewardedUsers[msg.sender] = true;
        }
        require(address(this).balance >= rewardAmount, "Not enough balance in contract.");
        payable(msg.sender).transfer(rewardAmount);
    }

    // Function to deposit funds into the contract
    function deposit() public payable {}

    // Allow the contract to receive Ether directly
    receive() external payable {}
    fallback() external payable {}

    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
}

'''

# **4️⃣ Compile the Solidity Contract**
print("Compiling contract...")
compiled_sol = compile_source(contract_source_code, solc_version="0.8.26")
contract_interface = compiled_sol['<stdin>:FitnessReward']

# Extract ABI and Bytecode
abi = contract_interface['abi']
bytecode = contract_interface['bin']

# **5️⃣ Create the Contract Instance in Web3**
FitnessReward = web3.eth.contract(abi=abi, bytecode=bytecode)

# **6️⃣ Build and Sign the Deployment Transaction**
transaction = FitnessReward.constructor().build_transaction({
    'from': owner_address,
    'nonce': web3.eth.get_transaction_count(owner_address),
    'gas': 2000000,  # Gas limit
    'gasPrice': web3.to_wei('20', 'gwei'),  # Gas price
})
print("Signing transaction...")
signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

# **7️⃣ Send the Transaction**
print("Deploying contract...")
tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction hash: {tx_hash.hex()}")

# **8️⃣ Wait for the Transaction Receipt**
print("Waiting for transaction receipt...")
try:
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=2)
    print(f"Transaction receipt: {tx_receipt}")
    contract_address = tx_receipt.contractAddress
    print(f"Contract successfully deployed at address: {contract_address}")
except Exception as e:
    print(f"Error waiting for transaction receipt: {e}")
    exit(1)

# **9️⃣ Add Funds to the Smart Contract**

# Create a contract instance
fitness_reward_contract = web3.eth.contract(address=contract_address, abi=abi)

# Amount of Ether to send (in Ether)
amount_to_send = web3.to_wei(0.01, 'ether')  # Adjust the amount as needed

# Build the transaction for the deposit function
deposit_transaction = fitness_reward_contract.functions.deposit().build_transaction({
    'from': owner_address,
    'value': amount_to_send,  # Amount of Ether to send
    'nonce': web3.eth.get_transaction_count(owner_address),
    'gas': 2000000,  # Gas limit
    'gasPrice': web3.to_wei('20', 'gwei'),  # Gas price
})

# Sign the transaction
signed_deposit_txn = web3.eth.account.sign_transaction(deposit_transaction, private_key)

# Send the transaction
print("Sending deposit transaction...")
try:
    deposit_tx_hash = web3.eth.send_raw_transaction(signed_deposit_txn.raw_transaction)
    print(f"Deposit transaction hash: {deposit_tx_hash.hex()}")

    # Wait for the transaction receipt
    print("Waiting for deposit transaction receipt...")
    deposit_tx_receipt = web3.eth.wait_for_transaction_receipt(deposit_tx_hash, timeout=120, poll_latency=2)
    print(f"Deposit transaction receipt: {deposit_tx_receipt}")

    # Check the contract balance after depositing
    contract_balance = fitness_reward_contract.functions.getContractBalance().call()
    print(f"Contract balance after deposit: {web3.from_wei(contract_balance, 'ether')} ETH")
except Exception as e:
    print(f"Error sending deposit transaction: {e}")
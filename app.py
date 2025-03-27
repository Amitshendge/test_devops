import streamlit as st
from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
METAMASK_ADDRESS = os.getenv("METAMASK_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Connect to blockchain
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# App Title and Styling
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            color: #4CAF50;
            font-size: 36px;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 20px;
        }
        .quiz {
            margin: 20px 0;
        }
        .reward-button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 12px 20px;
            font-size: 20px;
            width: 100%;
        }
        .success {
            color: green;
            font-size: 18px;
        }
        .error {
            color: red;
            font-size: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and Subtitle
st.markdown('<div class="title">Fitness Reward DApp</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete the quiz and claim your ETH reward!</div>', unsafe_allow_html=True)

# Blockchain connection status
if web3.is_connected():
    st.success("✅ Connected to Ethereum Network")
else:
    st.error("❌ Failed to connect to blockchain")

# Contract ABI
CONTRACT_ABI = [
    {
        "inputs": [],
        "name": "completeQuiz",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getContractBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

contract_balance = contract.functions.getContractBalance().call()
st.info(f"💰 Contract Balance: {web3.from_wei(contract_balance, 'ether')} ETH")

st.markdown("### Enter your Ethereum Wallet Address")
user_wallet = st.text_input("Wallet Address")

if user_wallet and not web3.is_address(user_wallet):
    st.error("❌ Invalid Ethereum address. Please check and try again.")

st.markdown("### Complete the Quiz")
q1 = st.radio("Do you exercise at least 3 times a week?", ["Yes", "No"], index=1, key="q1")
q2 = st.radio("Do you drink at least 2 liters of water daily?", ["Yes", "No"], index=1, key="q2")
q3 = st.radio("Do you get at least 7 hours of sleep every night?", ["Yes", "No"], index=1, key="q3")
q4 = st.radio("Do you avoid junk food regularly?", ["Yes", "No"], index=1, key="q4")

if st.button("🎁 Claim Your Reward", key="claim_reward"):
    if user_wallet and web3.is_address(user_wallet):
        try:
            with st.spinner("Processing your reward... Please wait!"):
                tx = contract.functions.completeQuiz().build_transaction({
                    'from': METAMASK_ADDRESS,
                    'nonce': web3.eth.get_transaction_count(METAMASK_ADDRESS),
                    'gas': 700000,
                    'gasPrice': web3.to_wei('50', 'gwei')  # Increased gas price
                })
                signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                etherscan_link = f"https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}"
                st.success(f"✅ Transaction Sent Successfully!")
                st.write(f"📝 Transaction Hash: `{tx_hash.hex()}`")
                st.markdown(f"[🔗 View on Etherscan]({etherscan_link})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Transaction failed: {str(e)}")
    else:
        st.error("❌ Please enter a valid Ethereum address.")

import hashlib
import time
from web3 import Web3

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)

        # Connect to local Ganache Ethereum network
        self.web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Ganache local Ethereum network
        self.account = self.web3.eth.accounts[0]  # Using the first account from Ganache
        print(f"Connected to Ethereum network: {self.web3.isConnected()}")
        print(f"Using account: {self.account}")

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1 if self.chain else 1

    def hash(self, block):
        block_string = str(block).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def display_chain(self):
        return self.chain

    def display_transactions(self):
        return self.current_transactions

    def deploy_contract(self, contract_source_code, abi, bytecode):
        # Simulating deploying a contract to Ganache
        contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = contract.constructor().transact({'from': self.account})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Contract deployed at address: {tx_receipt.contractAddress}")
        return tx_receipt.contractAddress

    def interact_with_contract(self, contract_address, abi):
        # Interacting with an already deployed contract
        contract = self.web3.eth.contract(address=contract_address, abi=abi)
        candidates = contract.functions.getCandidates().call()
        print(f"Candidates: {candidates}")
        return candidates

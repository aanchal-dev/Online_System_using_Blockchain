import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)
    
    def new_block(self, proof, previous_hash=None):
        # Create a new block and calculate its hash
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }
        
        # Calculate the hash of the current block and add it to the block
        block['hash'] = self.hash(block)
        
        # Reset the current list of transactions
        self.current_transactions = []
        
        # Add the new block to the chain
        self.chain.append(block)
        return block
    
    def new_transaction(self, voter, party):
        # Add a new transaction to the list of transactions
        self.current_transactions.append({
            'voter': voter,
            'party': party,
        })
        # Return the index of the block that will hold this transaction
        return self.last_block['index'] + 1
    
    def hash(self, block):
        # Return the hash of a block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def add_transaction(self, transaction):
        # Add a custom transaction to the blockchain
        self.current_transactions.append(transaction)
    
    def mine_block(self):
        # Mine a new block by finding a valid proof
        last_block = self.last_block
        proof = self.proof_of_work(last_block)
        previous_hash = self.hash(last_block)
        
        # Create the new block and return it
        return self.new_block(proof, previous_hash)
    
    def proof_of_work(self, last_block):
        # Find a valid proof of work (simple algorithm)
        last_proof = last_block['proof']
        increment = last_proof + 1
        
        # Keep incrementing until a valid proof is found
        while not self.valid_proof(last_proof, increment):
            increment += 1
        
        return increment
    
    def valid_proof(self, last_proof, proof):
        # Check if the proof is valid (by checking the hash pattern)
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        # Valid proof has a hash that starts with "0000"
        return guess_hash[:4] == "0000"
    
    @property
    def last_block(self):
        # Return the last block in the chain
        return self.chain[-1]

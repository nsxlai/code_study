# source: https://medium.com/better-programming/understand-blockchains-by-building-your-own-in-python-676dc38816fa
from time import time
from uuid import uuid4
from flask import Flask, jsonify
import requests
import json
import hashlib


class Blockchain:

    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self, proof, previous_hash=None):
        '''
        Proof of Work is a protocol with the main purpose of countering cyberattacks, such as a DDoS attack.
        This protocol is a requirement for the intensive form of calculations (also call mining) that must be
        performed to create a new group of "trustless" transactions on the blockchain. The verify these
        transactions, miners must have to solve a mathematical puzzle and the first miner to solve this problem
        gets the reward. Verified transactions are stored in the public blockchain. This puzzle is a bit more
        difficult with each new block.
        :param proof:
        :param previous_hash:
        :return:
        '''
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1,
    )
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block created",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    # return jsonify(response), 200
    return response


@app.route('/transactions/new', methods=['POST'])
def newTransaction():
    values = requests.get('0.0.0.0').json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(*values)
    response = {'message': f'Transaction will be added to Block {index}'}
    # return jsonify(response), 201
    return response


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    # return jsonify(response), 200
    return response


# if __name__ == '__main__':
#     # app.run(host='127.0.0.1', port=5000)
#     node_identifier = str(uuid4()).replace('-', '')
#     blockchain = Blockchain()
#     print(full_chain())

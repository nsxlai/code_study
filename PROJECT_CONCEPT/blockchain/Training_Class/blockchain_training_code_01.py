import hashlib
import time


class Block:
    """ In this exercise - create a class called Block and a constructor
        with the following variables: index,timestamp,data,priorHash.
        Set local variables - i.e.: this.index=index; for all inputs.
        Add a local empty string variable named hash
    """
    def __init__(self, index: int, timestamp: str, data: str, priorHash: str = ''):
        self.index = index  # where does the block sit on the chain
        self.timestamp = timestamp  # when was the block created
        self.data = data  # your actual transactions
        self.priorHash = priorHash  # string of prior hash
        self.nonce = 0
        self.hash = self.createHash()

    def createHash(self):
        hash_str = str(self.index) + self.priorHash + self.timestamp + self.data + str(self.nonce)
        hash_str = hash_str.encode()
        return hashlib.sha256(hash_str).hexdigest()

    def mineBlock(self, difficulty):
        # while self.hash[:difficulty] != '0'*difficulty:
        while not self.hash.startswith('0' * difficulty):
            self.nonce += 1
            self.hash = self.createHash()
            # time.sleep(0.2)
            # print(f'Block Hash: {self.hash}')
            # print(f'{self.nonce = }')


class ErnestoBlockChain:
    def __init__(self):
        self.chain = [self._createGenesisBlock()]
        self.difficulty = 2

    def _createGenesisBlock(self):
        return Block(0, '04/17/1973', 'BlockchainTrainingAlliance.com', 'BTA')

    def getLastBlock(self):
        return self.chain[-1]

    def addBlock(self, newBlock):
        """
        When add a new block to the chain, need to add last block Hash to current block's priorHash
        """
        newBlock.priorHash = self.getLastBlock().hash
        newBlock.hash = newBlock.createHash()
        newBlock.mineBlock(self.difficulty)
        self.chain.append(newBlock)
        # obviously it wouldn't be this easy. There are many checks and balances

    def isBCValid(self):
        block_chain_index = range(len(self.chain))
        for i in block_chain_index[:0:-1]:  # reverse the chain verification until hitting the first block
            existingBlock = self.chain[i]
            priorBlock = self.chain[i - 1]
            print(f'{priorBlock.data = }, {existingBlock.data = }')
            isExistHashNotEqual = existingBlock.hash != existingBlock.createHash()
            isPriorHashNotEqual = existingBlock.priorHash != priorBlock.createHash()
            if any([isExistHashNotEqual, isPriorHashNotEqual]):
                return False
        return True


if __name__ == '__main__':
    ErnestoCoin = ErnestoBlockChain()
    ErnestoCoin.addBlock(Block(1, '04/03/1977', 'amount = 7'))
    ErnestoCoin.addBlock(Block(2, '04/05/1977', 'amount = 17'))
    ErnestoCoin.addBlock(Block(3, '04/24/1977', 'amount = 77'))
    print(f'ErnestoCoin: {ErnestoCoin.chain[0].__dict__}')
    print(f'ErnestoCoin: {ErnestoCoin.chain[1].__dict__}')
    print(f'ErnestoCoin: {ErnestoCoin.chain[2].__dict__}')
    print(f'ErnestoCoin: {ErnestoCoin.chain[3].__dict__}')
    print(f'Is ErnestoChain Valid? {ErnestoCoin.isBCValid()}')

    ErnestoCoin.chain[1].data = 'amount: 1000'
    print(f'ErnestoCoin: {ErnestoCoin.chain[1].__dict__}')  # change any value in the block will alter the hash value
    print(f'Is ErnestoChain Valid? After change: {ErnestoCoin.isBCValid()}')  # the chain will be invalid

import hashlib
import json
from time import time
from datetime import datetime as dt


class Tx:
    """ Transaction class """
    def __init__(self, fromAddr: str, toAddr: str, amount: int):
        self.fromAddr = fromAddr
        self.toAddr = toAddr
        self.amount = amount


class Block:
    """
    In this exercise - create a class called Block and a constructor
    with the following variables: index, timestamp, data, priorHash.
    Set local variables - i.e.: this.index=index; for all inputs.
    Add a local empty string variable named hash
    """

    def __init__(self, timestamp: str, txs: list, priorHash: str = ''):
        # self.index = index  # where does the block sit on the chain
        self.timestamp = timestamp  # when was the block created
        self.txs = txs  # your actual transactions
        self.priorHash = priorHash  # string of prior hash
        self.nonce = 0
        self.hash = self.createHash()

    def createHash(self):
        tx = json.dumps(self.txs)  # serialize the transaction list
        ts = str(int(self.timestamp))  # timestamp is a float; turn it to int first and then str object
        # hash_str = str(self.index) + self.priorHash + self.timestamp + txs + str(self.nonce)
        hash_str = self.priorHash + ts + tx + str(self.nonce)
        hash_str = hash_str.encode()
        return hashlib.sha256(hash_str).hexdigest()

    def mineBlock(self, difficulty: int):
        while not self.hash.startswith('0' * difficulty):
          self.nonce += 1
          self.hash = self.createHash()


class ErnestoBlockChain:
    def __init__(self):
        self.chain = [self._createGenesisBlock()]
        self.difficulty = 2
        self.pendingTxs = []
        self.miningReward = 10

    def _createGenesisBlock(self) -> Block:
        t0 = dt(year=2020, month=1, day=15, hour=0, minute=0, second=0)
        tx = Tx(fromAddr='', toAddr='', amount=0).__dict__
        return Block(dt_to_str(t0), [tx])

    def getLastBlock(self) -> Block:
        return self.chain[-1]

    def addBlock(self, newBlock: Block):
        """
        When add a new block to the chain, need to add last block Hash to current block's priorHash
        """
        newBlock.priorHash = self.getLastBlock().hash
        newBlock.hash = newBlock.createHash()
        newBlock.mineBlock(self.difficulty)
        self.chain.append(newBlock)

    def minePendingTxs(self, miningRewardAddr):
        print(f'{self.pendingTxs = }')
        block = Block(str(int(time())), self.pendingTxs)
        block.mineBlock(self.difficulty)

        print('Block has been mined')
        self.chain.append(block)
        self.pendingTxs = [Tx('', miningRewardAddr, self.miningReward).__dict__]

    def createTx(self, tx: Tx):
        self.pendingTxs.append(tx.__dict__)

    def getBalanceOfAddress(self, addr: str):
        balance = 0
        for block in self.chain:
            for tx in block.txs:
                # breakpoint()
                try:
                    if tx.fromAddr == addr or tx.toAddr == addr:
                        balance = tx.amount
                except AttributeError as e:
                    print('No attribute available')
        return balance

    def isBCValid(self):
        block_chain_index = range(len(self.chain))
        for i in block_chain_index[:0:-1]:  # reverse the chain verification until hitting the first block
            existingBlock = self.chain[i]
            priorBlock = self.chain[i - 1]
            # print(f'{priorBlock.data = }, {existingBlock.data = }')
            isExistHashNotEqual = existingBlock.hash != existingBlock.createHash()
            isPriorHashNotEqual = existingBlock.priorHash != priorBlock.createHash()
            if any([isExistHashNotEqual, isPriorHashNotEqual]):
                return False
        return True


def dt_to_str(datetime: dt) -> str:
    return str(int(datetime.timestamp()))


if __name__ == '__main__':
    ErnestoCoin = ErnestoBlockChain()

    t1 = dt(year=2020, month=6, day=15, hour=0, minute=0, second=0)
    t2 = dt(year=2020, month=9, day=15, hour=0, minute=0, second=0)
    t3 = dt(year=2021, month=1, day=15, hour=0, minute=0, second=0)

    # ErnestoCoin.addBlock(Block(dt_to_str(t1), ['amount = 7']))
    # ErnestoCoin.addBlock(Block(dt_to_str(t2), ['amount = 17']))
    # ErnestoCoin.addBlock(Block(dt_to_str(t3), ['amount = 77']))
    # print(f'ErnestoCoin: {ErnestoCoin.chain[0].__dict__}')
    # print(f'ErnestoCoin: {ErnestoCoin.chain[1].__dict__}')
    # print(f'ErnestoCoin: {ErnestoCoin.chain[2].__dict__}')
    # print(f'ErnestoCoin: {ErnestoCoin.chain[3].__dict__}')
    # print(f'Is ErnestoChain Valid? {ErnestoCoin.isBCValid()}')

    # in reality address 1 and 2 would be public keys
    ErnestoCoin.createTx(Tx(fromAddr='address1', toAddr='address2', amount=75))
    ErnestoCoin.createTx(Tx(fromAddr='address2', toAddr='address1', amount=25))
    print(f'{ErnestoCoin.pendingTxs[0] = }')
    print(f'{ErnestoCoin.pendingTxs[1] = }')
    print()
    print(' Start miner '.center(40, '='))
    ErnestoCoin.minePendingTxs('Joes-address')
    print(f'Balance of Joes wallet is: {ErnestoCoin.getBalanceOfAddress("Joes-address")}')
    print('Mine AGAIN because the reward happens in the next block...')
    ErnestoCoin.minePendingTxs('Joes-address')
    print(f'Balance of Joes wallet in the next bock is: {ErnestoCoin.getBalanceOfAddress("Joes-address")}')

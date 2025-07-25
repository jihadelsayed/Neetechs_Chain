import datetime as dt
import hashlib
import json
import plyvel

class Chain:
    def __init__(self):
        self.chain = list()
        self.current_transactions = list()
        self.fee_address = "fee_address"
        self.db = plyvel.DB('blockchain.db', create_if_missing=True)  # LevelDB database

        initial_block = self._create_block(
            data="genesis block", proof=1, previous_hash="0", index=1
        )
        self.chain.append(initial_block)
    
    def mine_transaction(self) -> dict:
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = len(self.chain) + 1
        proof = self._proof_of_work(
            previous_proof=previous_proof, index=index, transactions=self.current_transactions
        )
        previous_hash = self._hash(block=previous_block)
        block = self._create_block(
            transactions=self.current_transactions, proof=proof, previous_hash=previous_hash, index=index
        )
        self.chain.append(block)
        self.current_transactions = []
        self._store_block_in_db(block)  # Store the block in the LevelDB database
        return block

    def add_transaction(self, sender_address: str, recipient_address: str, amount: int) -> bool:
        """
        Add a new transaction to the current list of transactions
        """
        transaction = {
            "sender": sender_address,
            "recipient": recipient_address,
            "amount": amount
        }
        self.current_transactions.append(transaction)
        return True

    def mine_block(self, data: str) -> dict:
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = len(self.chain) + 1
        proof = self._proof_of_work(
            previous_proof=previous_proof, index=index, data=data
        )
        previous_hash = self._hash(block=previous_block)
        block = self._create_block(
            data=data, proof=proof, previous_hash=previous_hash, index=index
        )
        self.chain.append(block)
        self._store_block_in_db(block)  # Store the block in the LevelDB database
        return block

    def _create_block(
        self, data: str, proof: int, previous_hash: str, index: int
    ) -> dict:
        block = {
            "index": index,
            "timestamp": str(dt.datetime.now()),
            "data": data,
            "proof": proof,
            "previous_hash": previous_hash,
        }

        return block

    def get_previous_block(self) -> dict:
        return self.chain[-1]

    def _to_digest(
        self, new_proof: int, previous_proof: int, index: int, data: str
    ) -> bytes:
        to_digest = str(new_proof ** 2 - previous_proof ** 2 + index) + data
        # It returns a UTF-8 encoded version of the string
        return to_digest.encode()

    def _proof_of_work(self, previous_proof: str, index: int, data: str) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, index, data)
            hash_operation = hashlib.sha256(to_digest).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def _hash(self, block: dict) -> str:
        """
        Hash a block and return the cryptographic hash of the block
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            # Check if the previous hash of the current block is the same as the hash of its previous block
            if block["previous_hash"] != self._hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            index, data, proof = block["index"], block["data"], block["proof"]
            hash_operation = hashlib.sha256(
                self._to_digest(
                    new_proof=proof,
                    previous_proof=previous_proof,
                    index=index,
                    data=data,
                )
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block
            block_index += 1

        return True
    
    def get_balance(self, address: str) -> int:
        """
        Get the current balance of the given address
        """
        balance = 0
        for block in self.chain:
            for transaction in block["transactions"]:
                if transaction["sender"] == address:
                    balance -= transaction["amount"]
                elif transaction["recipient"] == address:
                    balance += transaction["amount"]
        return balance

    def send_money(self, sender_address: str, recipient_address: str, amount: int) -> bool:
        """
        Send a specified amount of money from the sender's address to the recipient's address,
        deducting the specified fee from the amount
        """
        # Check if the sender has sufficient funds (including the fee)
        sender_balance = self.get_balance(sender_address)
        random_fee = (amount * generate_random_fee() / 100)

        total_amount = amount + random_fee
        if sender_balance < total_amount:
            return False
        # Create a transaction and add it to the pending transactions list
        transaction = {
            "sender": sender_address,
            "recipient": recipient_address,
            "amount": amount
        }
        self.current_transactions.append(transaction)
        # Create a transaction for the fee and add it to the current transactions list
        fee_transaction = {
            "sender": sender_address,
            "recipient": self.fee_address,  
            "amount": random_fee
        }
        self.current_transactions.append(fee_transaction)
        return True
    
    def _store_block_in_db(self, block: dict) -> None:
        """
        Store a block in the LevelDB database
        """
        block_hash = self._hash(block)
        self.db.put(block_hash.encode(), json.dumps(block).encode())

    def load_chain_from_db(self) -> None:
        """
        Load the blockchain from the LevelDB database
        """
        for key, value in self.db:
            block = json.loads(value.decode())
            self.chain.append(block)


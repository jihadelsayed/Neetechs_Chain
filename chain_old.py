import datetime as _dt
import hashlib as _hashlib
import json as _json
# python -m uvicorn main:app --reload

from nas.insan import Insan
from mal.amal import Amal
from mal.fee import generate_random_fee

class Chain:
    def __init__(self):
        self.chain = list()
        self.current_transactions = list()
        self.family_tree = {}  # Dictionary to store the family tree
        self.fee_address = "fee_address"
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
        return block

    def _create_block(
        self, data: str, proof: int, previous_hash: str, index: int
    ) -> dict:
        block = {
            "index": index,
            "timestamp": str(_dt.datetime.now()),
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
        # It returns an utf-8 encoded version of the string
        return to_digest.encode()

    def _proof_of_work(self, previous_proof: str, index: int, data: str) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, index, data)
            hash_operation = _hashlib.sha256(to_digest).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def _hash(self, block: dict) -> str:
        """
        Hash a block and return the crytographic hash of the block
        """
        encoded_block = _json.dumps(block, sort_keys=True).encode()

        return _hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            # Check if the previous hash of the current block is the same as the hash of it's previous block
            if block["previous_hash"] != self._hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            index, data, proof = block["index"], block["data"], block["proof"]
            hash_operation = _hashlib.sha256(
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
        self.pending_transactions.append(transaction)
        # Create a transaction for the fee and add it to the current transactions list
        fee_transaction = {
            "sender": sender_address,
            "recipient": self.fee_address,  # Replace "fee_address" with the actual address where the fee will be collected
            "amount": random_fee
        }
        self.current_transactions.append(fee_transaction)
        return True
    
    def add_insan(self, insan: Insan) -> bool:
        """
        Add an insan to the family tree
        """
        if insan.id in self.family_tree:
            return False  # Insan already exists in the family tree

        self.family_tree[insan.id] = insan
        return True
    
    def add_relationship(self, parent_id: str, child_id: str) -> bool:
        """
        Add a parent-child relationship to the family tree
        """
        if parent_id not in self.family_tree or child_id not in self.family_tree:
            return False  # Parent or child does not exist in the family tree

        parent = self.family_tree[parent_id]
        child = self.family_tree[child_id]

        parent.add_child(child)
        child.add_parent(parent)

        return True

    def get_insan(self, id: str) -> Insan:
        """
        Get an insan from the family tree based on the ID
        """
        if id in self.family_tree:
            return self.family_tree[id]

        return None
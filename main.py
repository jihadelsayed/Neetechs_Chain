import fastapi
import chain
# 
chain = chain.Chain()
app = fastapi.FastAPI()


# endpoint to mine a block
@app.post("/mine_block/")
def mine_block(data: str):
    if not chain.is_chain_valid():
        return fastapi.HTTPException(status_code=400, detail="The chain is invalid")
    block = chain.mine_block(data=data)

    return block
@app.post("/mine_transaction/")
def mine_transaction(data: str):
    if not chain.is_chain_valid():
        return fastapi.HTTPException(status_code=400, detail="The chain is invalid")
    block = chain.mine_transaction(data=data)

    return block


# endpoint to return the chain
@app.get("/chain/")
def get_chain():
    if not chain.is_chain_valid():
        return fastapi.HTTPException(status_code=400, detail="The chain is invalid")
    return chain.chain

# endpoint to see if the chain is valid
@app.get("/validate/")
def is_chain_valid():
    if not chain.is_chain_valid():
        return fastapi.HTTPException(status_code=400, detail="The chain is invalid")

    return chain.is_chain_valid()


# endpoint to return the last block
@app.get("/chain/last/")
def previous_block():
    if not chain.is_chain_valid():
        return fastapi.HTTPException(status_code=400, detail="The chain is invalid")
        
    return chain.get_previous_block()
    
@app.post("/chain/send_money/")
def send_money(sender: str, recipient: str, amount: int):
    """
    Send a specified amount of money from the sender's address to the recipient's address
    """
    success = chain.send_money(sender_address=sender, recipient_address=recipient, amount=amount)
    if not success:
        return fastapi.HTTPException(status_code=400, detail="Transaction failed")

    return {"message": "Transaction successful"}

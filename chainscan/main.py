from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from pycoingecko import CoinGeckoAPI
import pandas as pd 
import json
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

##
# for the execution of the code after activating virtual enviroment: 
# source .venv/bin/activate 
# uvicorn main:app --reload
# include your API key in the URL or as an X-API-Key header when making 
# requests to Alchemy's production endpoints. The URL structure for a production endpoint 
# would look something like:https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY   . 
# Register a application after an account on alchemy and retrieve the api_key 
# #


@asynccontextmanager
async def lifespan(app: FastAPI):
    chain =  """
                                                                                     
      _____               _____    ____   ____        ____    ____  _____   ______   
 ___|\     \          ___|\    \  |    | |    |  ____|\   \  |    ||\    \ |\     \  
|    |\     \        /    /\    \ |    | |    | /    /\    \ |    | \\    \| \     \ 
|    | |     |      |    |  |    ||    |_|    ||    |  |    ||    |  \|    \  \     |
|    | /_ _ /   |   |    |  |____||    .-.    ||    |__|    ||    |   |     \  |    |
|    |\    \  --|-- |    |   ____ |    | |    ||    .--.    ||    |   |      \ |    |
|    | |    |   |   |    |  |    ||    | |    ||    |  |    ||    |   |    |\ \|    |
|____|/____/|       |\ ___\/    /||____| |____||____|  |____||____|   |____||\_____/|
|    /     ||       | |   /____/ ||    | |    ||    |  |    ||    |   |    |/ \|   ||
|____|_____|/        \|___|    | /|____| |____||____|  |____||____|   |____|   |___|/
  \(    )/             \( |____|/   \(     )/    \(      )/    \(       \(       )/  
   '    '               '   )/       '     '      '      '      '        '       '   
                            '                                                        
                                                                                     
     _____          ____   _________________       ____                              
 ___|\    \    ____|\   \ /                 \ ____|\   \                             
|    |\    \  /    /\    \\______     ______//    /\    \                            
|    | |    ||    |  |    |  \( /    /  )/  |    |  |    |                           
|    | |    ||    |__|    |   ' |   |   '   |    |__|    |                           
|    | |    ||    .--.    |     |   |       |    .--.    |                           
|    | |    ||    |  |    |    /   //       |    |  |    |                           
|____|/____/||____|  |____|   /___//        |____|  |____|                           
|    /    | ||    |  |    |  |`   |         |    |  |    |                           
|____|____|/ |____|  |____|  |____|         |____|  |____|                           
  \(    )/     \(      )/      \(             \(      )/                             
   '    '       '      '        '              '      '                              
    -Test For coins and blockchain data-
        Use curl to Pass Parameters: 
        Use the curl command in the
        terminal to call the API 
        endpoints and pass the required
        parameters. 
        For example:
        curl "http://127.0.0.1:8000/ohlc_price/?coin=bitcoin"
"""
    print(chain)
    yield

app = FastAPI(lifespan=lifespan)



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class InputString(BaseModel): 
    input_string:str

@app.post("/process_string/")
def process_string(input_data: InputString):
    processed_string = f"Processed: {input_data.input_string}"
    return {"result": processed_string}


@app.get("/btc_price/")
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
                "ids":"bitcoin", 
              "vs_currencies": "usd"
            }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {"bitcoin_price_usd": data["bitcoin"]["usd"]}
    else:
        return {"error": "Failed to fetch BTC price"}

""" The following method can be used for every specific coin """
@app.get("/ohlc_price/")
def get_ohlc_price(coin: str):
    cg = CoinGeckoAPI()
    ohlc = cg.get_coin_ohlc_by_id(id=coin, vs_currency="usd", days="30")
    
    #Each data point is represented as a dictionary. #
    #When you create a pandas DataFrame using 
    #pd.DataFrame(ohlc), pandas interprets each 
    #dictionary within the list as a row in the 
    #Dataframe, and extracts the key-value pairs as columns. 
    
    df_ohlc = pd.DataFrame(ohlc)
    df_ohlc.columns = ["date", "open", "high", "low", "close"]
    df_ohlc.set_index('date', inplace=True)
    return df_ohlc.to_dict()

"""

Use a tool like curl or a browser to call the /ohlc_price/ endpoint with the desired coin as a query parameter. For example:
curl "http://127.0.0.1:8000/ohlc_price/?coin=bitcoin"
View the Output: The response will return the OHLC data for the specified coin in JSON format.

"""
@app.get("/address_history/")
def get_address_history(fromAddress:str):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 0,
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "fromAddress": fromAddress,
            }
        ]
    })

    headers = {
        'Content-Type': 'application/json'
    }

    api_key = " Alchemy key "
    base_url = f"https://eth-mainnet.g.alchemy.com/v2/{api_key}"

    try:
        response = requests.post(base_url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



# Function returns a json of the transaction correposnding to the address specified 
# it traces the transaction acros the blockchain
@app.get("/trace_transaction/")
def trace_transaction(address:str): 
    url = "https://eth-mainnet.g.alchemy.com/v2/docs-demo"
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "trace_transaction",
        "params": [address]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return(response.text)


# It can be used to get a trace of all the transactions 
# in a given block. To use trace functions we must have a Growth or enterpize api profiles. 
@app.get("/trace_block/")
def trace_block(): 
    url = "https://eth-mainnet.g.alchemy.com/v2/docs-demo"

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "trace_block",
        "params": ["latest"] # this can be a string or a block number
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.text


@app.get("/block_info/")
def get_block_info(block_address: str):
    api_key = "Alchemy key"
    url = f"https://eth-mainnet.g.alchemy.com/v2/{api_key}"

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_getBlockByHash",
        "params": [block_address, True]  # True to include full transaction objects
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}


@app.get("/unified_ETH/")
def unified_ETH(item_id: int, q: Union[str, None] = None, fromAddress: str = None, address: str = None, block_address: str = None):
    result = {}

    # Include data from read_item
    result["item_data"] = read_item(item_id, q)

    # Include address history
    if fromAddress:
        result["address_history"] = json.loads(get_address_history(fromAddress))

    # Include transaction trace
    if address:
        result["transaction_trace"] = json.loads(trace_transaction(address))

    # Include block info
    if block_address:
        result["block_info"] = get_block_info(block_address)

    return result.json()

"""
Use curl to Pass Parameters: Use the curl command in the terminal to call the API endpoints and pass the required parameters. For example:
curl "http://127.0.0.1:8000/ohlc_price/?coin=bitcoin"
For /address_history/:
curl "http://127.0.0.1:8000/address_historyomAddress=0xYourAddressHere/?fr"
For /trace_transaction/:
curl "http://127.0.0.1:8000/trace_transaction/?address=0xYourTransactionHashHere"
For /block_info/:
curl "http://127.0.0.1:8000/block_info/?block_address=0xYourBlockHashHere"
For /unified_ETH/:
curl "http://127.0.0.1:8000/unified_ETH/?item_id=1&q=test&fromAddress=0xYourAddressHere&address=0xYourTransactionHashHere&block_address=0xYourBlockHashHere"

The response will be displayed in the terminal as JSON data.

"""
# The Transfers API allows you to easily fetch historical transactions for any address across Ethereum and supported L2s including Polygon, Arbitrum, and Optimism.
@app.get("/asset_transfers/")
def get_asset_transfers(address: str):
    url = "https://eth-mainnet.g.alchemy.com/v2/docs-demo"

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "toAddress": address,
                "category": ["external"],
                "order": "asc",
                "withMetadata": True,
                "excludeZeroValue": True,
                "maxCount": "0x3e8"
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}
    
# Method that calls to retrieve transaction receipts for a specific block, Extracting data for analysis, Building a blockchain explorer,
@app.get("/transaction_recipt")
def transaction_recipt(blocknumber: str): 
                
    url = "https://eth-mainnet.g.alchemy.com/v2/API-KEY"

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getTransactionReceipts",
        "params": [{ "blockNumber": blocknumber }]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

@app.get("/aggregate_data/")
def aggregate_data(
    fromAddress: str = None,
    address: str = None,
    block_address: str = None,
    blocknumber: str = None
):
    result = {}

    # Include address history
    if fromAddress:
        result["address_history"] = json.loads(get_address_history(fromAddress))

    # Include transaction trace
    if address:
        result["transaction_trace"] = json.loads(trace_transaction(address))
        result["asset_transfer"] = json.loads(get_asset_transfers(address))

    # Include block info
    if block_address:
        result["block_info"] = get_block_info(block_address)

    # Include transaction receipt
    if blocknumber:
        result["transaction_receipt"] = transaction_recipt(blocknumber)
    
    return result


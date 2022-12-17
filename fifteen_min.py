from finshoonya import shoonya
import datetime
import time
import json
from pytz import timezone
import pandas as pd
import sys

#sys.stdout = open("/content/drive/MyDrive/algo/algolog.txt", "w")

tze = timezone("Asia/Kolkata")

#replace with your api and credentials.
client = shoonya("user_id", "password", "onetimeotp",
           "your_api_key")
client.login()

#program variable
positions = []
exit_time = datetime.time(15, 10)
no_of_lot = 1
lot_size = 25
symbol = "BANKNIFTY"
typ_of_symbol = "C"
expiry = "28JUL22"
strike = 36300
TSYM = symbol + expiry + typ_of_symbol + str(strike)
scpd = client.get_scripcode(TSYM, "NFO")["values"][0]
qty = 25
trail_sl = 2

def get_order_executed_price_single(oid):
    count = 5
    while count != 0:
        _ord = client.order_detail(oid)[0]
        if _ord and _ord["status"] == "COMPLETE":
           return float(_ord["avgprc"])
        if _ord and _ord["status"] == "REJECTED":
           print("Order rejected.")
           break
        count -= 1

HDATA, candles = {}, {}
LTP={}

def on_message(ws, message, data_type = None, continue_flag = None):
    global LTP, HDATA#global ltp object
    msg = json.loads(message)
    #print(msg)
    if "tk" in msg and "lp" in msg:
        #print(msg,type(msg))
        if msg['tk'] not in HDATA:
            HDATA.update({str(msg['tk']): []})
        LTP[str(msg['tk'])] = float(msg['lp'])
        HDATA[str(msg['tk'])].append({"ltt":datetime.datetime.now(tze), "ltp":float(msg['lp'])})

def get_ref_price_and_flags():
    ordb = client.orderbook()
    ordb = [o for o in ordb if "remarks" in o and o["status"] == "COMPLETE"]
    BOUGHT = True if ordb[0]["trantype"] == "B" else False
    SOLD = True if ordb[0]["trantype"] == "S" else False
    refPrice = float(ordb[0]["avgprc"])
    return BOUGHT, SOLD, refPrice

def create_candlestick(data, timeframe = 20):
    _df = pd.DataFrame(data)
    _df.set_index(pd.DatetimeIndex(_df["ltt"]), inplace = True)
    _df = _df["ltp"].resample(f'{timeframe}S').ohlc()
    return _df

#starts websocket and subscribe token..
#client.start_websocket(on_message)
time.sleep(5)
#client.subscribe(f'NFO|{scpd["token"]}', "t")
time.sleep(5)
#refPrice = LTP[scpd["token"]]
positions = []#[i for i in client.position() if i['tsym'] == TSYM and int(i['netqty']) != 0]

BOUGHT = False
SOLD = False
LONG_PRICE = None
SHORT_PRICE = None
if positions:
    BOUGHT, SOLD, refPrice = get_ref_price_and_flags()

while datetime.datetime.now(tze).time() < datetime.time(23, 10):
    if BOUGHT and LTP[scpd["token"]] >= refPrice + 10:
        print(f"B|{datetime.datetime.now(tze)}|old refPrice:",refPrice)
        refPrice += trail_sl
        print(f"B|{datetime.datetime.now(tze)}|new refPrice:",refPrice)

    if SOLD and LTP[scpd["token"]] <= refPrice - 10:
        print(f"S|{datetime.datetime.now(tze)}|old refPrice:",refPrice)
        refPrice -= trail_sl
        print(f"S|{datetime.datetime.now(tze)}|new refPrice:",refPrice)
    if 1.5 >datetime.datetime.now(tze).time().second % 15 >= 0 and LTP[scpd["token"]] > refPrice and not BOUGHT:
        order = client.order(price=0, qty = qty *2 if SOLD else qty, tradingsymbol = TSYM, ord_tp = "MKT", sl = 0, buysell = "B", exch = "NFO",
                     prdct = "M", amo="NO", remarks = "STRATEGY")
        _PRICE = get_order_executed_price_single(order["norenordno"])
        print(f'{datetime.datetime.now(tze).time().isoformat()}|{TSYM} BOUGHT AT: {_PRICE}')
        SOLD = False
        BOUGHT = True
        time.sleep(1.5)

    if 1.5 >datetime.datetime.now(tze).time().second % 15 >= 0 and LTP[scpd["token"]] < refPrice and not SOLD:
        order = client.order(price=0, qty = qty *2 if BOUGHT else qty, tradingsymbol = TSYM, ord_tp = "MKT", sl = 0, buysell = "S", exch = "NFO",
                     prdct = "M", amo="NO", remarks = "STRATEGY")
        _PRICE = get_order_executed_price_single(order["norenordno"])
        print(f'{datetime.datetime.now(tze).time().isoformat()}|{TSYM} SOLD   AT: {_PRICE}')
        SOLD = True
        BOUGHT = False
        
        time.sleep(1.5)
print(f"ALGO STOPPED DUE TO TRADING HOUR IS OVER.")

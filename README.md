# finshoonya
unofficial library to trade in finvasia.

# Installation
  using git.
  ```
  pip install git+https://github.com/Rahulghuge94/finshoonya.git
  ```
# Login
To login provide ur account id,password and pan and create shoonya object.
```
  from finshoonya import shoonya
  client=shoonya(userid="xyzk56",password="utyh675",pan="THG56214P",api_key="gdkmbloonvkmsdf")
  client.login()
```
# orderbook
```
  print(client.orderbook())
```
# position
```
  print(client.position())
```
# tradebook
```
  print(client.tradebook())
```
# place order
to place intraday market order..
banknifty option
```
  order=client.order(price=0,qty=25,tradingsymbol="BANKNIFTY16DEC21P35700",ord_tp="MKT",sl=0,buysell="B",exch="NFO",prdct="M",disc_qty=0,amo="NO",trigger_price=None,
                    retention='DAY', remarks=None, bkpft = 0.0, trail_price = 0.0)
  print(order)
```
to place intraday limit order..
wipro
```
  order=client.order(price=400,qty=25,tradingsymbol="WIPRO-EQ",ord_tp="LMT",sl=0,buysell="B",exch="NFO",prdct="I",disc_qty=0,amo="NO",trigger_price=None,
                    retention='DAY', remarks=None, bkpft = 0.0, trail_price = 0.0)
  print(order)
```
to place delivery market order..
banknifty option
```
  order=client.order(price=0,qty=25,tradingsymbol="BANKNIFTY16DEC21P35700",ord_tp="MKT",sl=0,buysell="B",exch="NFO",prdct="M",disc_qty=0,amo="NO",trigger_price=None,
                    retention='DAY', remarks=None, bkpft = 0.0, trail_price = 0.0)
  print(order)
```
to place delivery limit order..
wipro
```
  order=client.order(price=400,qty=25,tradingsymbol="WIPRO-EQ",ord_tp="LMT",sl=0,buysell="B",exch="NFO",prdct="D",disc_qty=0,amo="NO",trigger_price=None,
                    retention='DAY', remarks=None, bkpft = 0.0, trail_price = 0.0)
  print(order)
```
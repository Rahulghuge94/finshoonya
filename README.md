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
  client=shoonya(email="xyzk56",password="utyh675",pan="THG56214P")
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
wipro
```
  order=client.order(price=0,qty=1,secid=3787,sl=0,buysell="B",exch="NSE",prdct="I",inst_tp='EQUITY',disc_qty=0)
  print(order)
```

"""
@auther:Rahul Ghuge
unofficial api to trade with finvasia.
"""
import requests
import json,os
import time,datetime
from time import sleep
import pandas as pd
import hashlib
from pytz import timezone
import websocket
import threading
tze=timezone('Asia/Kolkata')#timezone to work with cloud instances.


class shoonya(object):
      
      _root={"login": "/QuickAuth", "fund": "/Limits", "position": "/PositionBook", "orderbook": "/OrderBook", "tradebook": "/TradeBook", "holding": "/Holdings", 
             "order": '/PlaceOrder', "modifyorder": '/ModifyOrder', "cancelorder": '/CancelOrder', "exitorder": '/ExitSNOOrder', "singleorderhistory": '/SingleOrdHist',
             "searchscrip": '/SearchScrip', "scripinfo": '/GetSecurityInfo', "getquote": '/GetQuotes', "hist_data": "/TPSeries", "option": "/GetOptionChain"}

      def __init__(self, userid: str = None, password: str = None, twofa: str = None, app_key: str = None, source = "WEB"):
          self.userid = userid
          self.password = hashlib.sha256(password.encode('utf-8')).hexdigest() if password else password
          self.twofa = twofa
          self.imei = "dbbf5adf877739404c9220a28002b5d3"
          self.app_key = app_key
          self.session = requests.session()
          self.url = "https://shoonya.finvasia.com/NorenWClientWeb"
          self.wss_url = "wss://shoonya.finvasia.com/NorenWSWeb/"
          self.access_token = None
          #self.wss = None
          self.__wss = None
          self.wss_connected = False
          self.__ws_mutex = threading.Lock()
          self.subscribed = []
          self.LTP = {}
          self.ordsource = source

      def login(self):
          values = {"uid": self.userid, "pwd": self.password, "factor2": self.twofa,
            "apkversion": "1.2.0", "imei": self.imei, "vc": "NOREN_WEB",
            "appkey": self.app_key, "source": "WEB", "addldivinf": "Chrome-96.0.4664.45"}
          data = "jData="+json.dumps(values)
          #print(data, self.url + self._root["login"])
          res = self.session.post(self.url + self._root["login"], data = data)
          if res.status_code != 200:
             print(f"Unable to Login. Reason:{res.text}")
             return
          else:
             res = res.json()
             self.access_token = res["susertoken"]
             self.write_cred()
          print("Logged In.")
        
      def log_using_api(self):
          #Convert to SHA 256 for password and app key
          self.url = "https://shoonyatrade.finvasia.com/NorenWClientTP/"
          pwd = self.password
          u_app_key = '{0}|{1}'.format(self.userid, self.app_key)
          app_key = hashlib.sha256(u_app_key.encode('utf-8')).hexdigest()
          #prepare the data
          values = { "source": "API" , "apkversion": "1.0.0"}
          values["uid"] = self.userid
          values["pwd"] = self.password
          values["factor2"] = self.twofa
          values["vc"] = f"{self.userid}_U"
          values["appkey"] = app_key
          values["imei"] = "abc1234"

          payload = 'jData=' + json.dumps(values)
          res = requests.post(self.url+self._root["login"], data = payload)
          #print(res)
          resDict = json.loads(res.text)
          print(resDict,payload)
          if resDict['stat'] != 'Ok':            
             return None
          self.access_token = resDict['susertoken']
          self.write_cred()
          print("Logged In.")
            
      def check_if_source_is_api_and_add_source(self, data):
          if self.url == "https://shoonyatrade.finvasia.com/NorenWClientTP/":
             data.update({'ordersource':'API'})
          return data
    
      def api_helper(self, url, data = None, req_typ: str = "POST"):
          if data and req_typ == "POST":
             self.load_cred()
             data = 'jData=' + json.dumps(data) + f'&jKey={self.access_token}'
             res = self.session.post(url, data = data)
             if res.status_code !=200 and "Session Expired :  Invalid Session Key" in res.text:
                print(f"Unable to Login. Reason:{res.text}")
                if self.ordsource == "WEB":
                    self.login()
                else:
                    self.log_using_api()
                    self.write_cred()
                return self.session.post(url, data = data)
             else:
                res = res.json()
                return res
          if not data and req_type == "GET":
             res = self.session.get(url)
             if res.status_code != 200 and "Session Expired :  Invalid Session Key" in res.text:
                print(f"Unable to Login. Reason:{res.text}")
                return
             else:
                return res
        
      def load_cred(self):
          sessn = None
          data = None
          if os.path.isfile("cred.json"):
             sessn = open("cred.json", "r")
             data = json.load(sessn)
          else:
             self.login()
          self.userid = data["userid"]
          self.password = data["password"]
          self.twofa = data["twofa"]
          self.access_token = data["access_token"]
          self.app_key = data["app_key"]
          
      def write_cred(self):
          sessn = open("cred.json","w")
          dic = {"userid": self.userid, "password": self.password, "twofa": self.twofa,
               "access_token": self.access_token, "app_key": self.app_key}
          json.dump(dic, sessn)
     
      def fund(self):
          url = self.url + self._root["fund"]
          data={"uid": self.userid, "actid": self.userid}
          return self.api_helper(url, data = data, req_typ = "POST")
    
      def orderbook(self):
          url = self.url + self._root["orderbook"]
          data = {"uid": self.userid,"ordersource": self.ordsource}
          res = self.api_helper(url, data = data, req_typ = "POST")
          return res
        
      def position(self):
          url = self.url + self._root["position"]
          data = {"uid": self.userid, "actid": self.userid}
          res = self.api_helper(url, data = data, req_typ = "POST")
          return res
    
      def tradebook(self):
          url = self.url + self._root["tradebook"]
          data = {"uid": self.userid, "actid": self.userid, "ordersource": self.ordsource}
          res = self.api_helper(url, data = data, req_typ = "POST")
          return res
        
      def holdings(self):
          url = self.url + self._root["holding"]
          data = {"uid": self.userid,"actid": self.userid}
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"]=="Not_Ok":
             return []
          else:
             return res
            
      #order status "COMPLETE",REJECTED,"CANCELED" "OPEN" "PENDING"
      def order(self, price, qty, tradingsymbol, ord_tp, sl = 0, buysell = "B", exch = "NSE", prdct = "I", disc_qty = 0, amo = "NO", trigger_price = None,
                    retention = 'DAY', remarks = "Orderleg1", bkpft = 0.0, trail_price = 0.0):
          """
          place order
          """
          data= {"uid": self.userid, "actid": self.userid, "trantype": buysell, "prd": prdct, "exch": exch,
                 "tsym": tradingsymbol, "qty": str(qty),"dscqty": str(disc_qty), "prctyp": ord_tp, "prc": str(price),
                 "trgprc": str(trigger_price), "ret": retention, "remarks": remarks, "amo": amo, 'ordersource': self.ordsource}
          #print(data)
          url = self.url + self._root["order"]
          #cover order
          if prdct == 'H':            
            data["blprc"] = str(sl)
            #trailing price
            if trail_price != 0.0:
                data["trailprc"] = str(trail_price)
          #bracket order
          if prdct == 'B':            
             data["blprc"] = str(sl)
             data["bpprc"] = str(bkpft)
             #trailing price
             if trail_price != 0.0:
                data["trailprc"] = str(trail_price)
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"] == "Not_Ok":
             return None
          else:
             return res
        
      def modify_order(self, orderno, exch, tradingsymbol, qty, ord_tp, price = 0.0, trigger_price = None, sl = 0.0, bkpft = 0.0, trail_price = 0.0):
          url = self.url + self._root["modifyorder"]
          data = {"uid": self.userid, "actid": self.userid, "norenordno": orderno, "exch": exch, "tsym": tradingsymbol, "qty": str(qty), "prctyp": ord_tp, 
                 "prc": str(price), "ordersource": self.ordsource}
          if (ord_tp == 'SL-LMT') or (ord_tp == 'SL-MKT'):
             if (trigger_price != None):
                data["trgprc"] = trigger_price
             else:
                return None
          #if cover order or high leverage order
          if product_type == 'H':            
             data["blprc"] = str(bkpft)
             #trailing price
             if trail_price != 0.0:
                values["trailprc"] = str(trail_price)
          #bracket order
          if product_type == 'B':            
             data["blprc"] = str(sl)
             data["bpprc"] = str(bkpft)
             #trailing price
             if trail_price != 0.0:
                data["trailprc"] = str(trail_price)
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"] == "Not_Ok":
             return None
          else:
             return res
        
      def cancel_order(self, order_no: str):
          url = self.url + self._root["cancelorder"]
          data = {"uid": self.userid, "norenordno": str(order_no), "ordersource": self.ordsource}
          res = self.api_helper(url, data = data, req_typ = "POST")
          return res
            
      def order_detail(self, order_no: str):
          url = self.url + self._root["singleorderhistory"]
          data = {"uid": self.userid, "norenordno": str(order_no), "ordersource": self.ordsource}
          res = self.api_helper(url, data = data, req_typ = "POST")
          return res
            
      def getdata(self,secid:str, fdt:str, tdt:str, exch:str="NSE", interval="1"):
          """
          :param
            tdt:to date in timestamp i.e.1650864392
            fdt: from date in timestamp i.e.1650764392
            secid: security name i.e. TTTAN-EQ, NIFTY31MAR22P36000,BANKNIFTY31MAR22C36000
            interval possible values 1, 3, 5 , 10, 15, 30, 60, 120, 240
            #symbol format option SYMEXPCorPSTRIKE fut SYMEXPF expiry format ddmmyy equity sym-EQ
          """
          url = "https://shoonyatrade.finvasia.com//NorenWClientWeb/TPSeries"
          data = {"uid": self.userid, "exch": exch, "token": secid, "st": fdt, "et": tdt, "intrv": interval}
          res = self.api_helper(url, data = data, req_typ = "POST")
          #print(res)
          res.sort(key = lambda x: x["ssboe"])
          res = pd.DataFrame(res)
          res.rename(columns = {'into': 'Open','inth': 'High','intl': 'Low','intc': 'Close','intvwap': 'vwap','intv': 'Volume','intoi': 'OI',
                                'v': 'TVolume','oi': 'TOI'}, inplace = True)
          cng_typ = {"Open": float, "High": float, "Low": float, "Close": float, "Volume": int, "OI": int, "vwap": float, "TVolume": float, "TOI": int}
          res = res.astype(cng_typ)
          res.drop("stat", axis = 1, inplace = True)
          return res
            
      def get_quote(self, secid, exch = "NSE"):
          url = self.url+self._root["getquote"]
          data = {"uid": self.userid, "exch": exch, "token": secid}
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"] == "Not_Ok":
             return None
          else:
             return res
            
      def get_scripcode(self, searchstring, exch = "NSE"):
          url = self.url + '/SearchScrip'
          data = {"uid": self.userid, "exch": exch, "stext": str(searchstring)}
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"]=="Not_Ok":
             return None
          else:
             return res
      
      def get_scripinfo(self, token, exch = "NSE"):
          url = self.url+'/GetSecurityInfo'
          data = {"uid": self.userid, "exch": exch, "token": str(token)}
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"] == "Not_Ok":
             return None
          else:
             return res
        
      def close_all(self):
          posns = self.position()
          if not posns:
             return "No open Positions."
          for i in posns:
              if i["netqty"] < 0:
                 ord = self.order(price = 0, qty = i["netqty"], tradingsymbol = i["tsym"], ord_tp = "MKT", sl = 0, buysell = "B", exch = i["exch"], prdct = i["prd"])
                 print(ord)
          for i in posns:
              if i["netqty"] > 0:
                 self.order(price = 0, qty = i["netqty"], tradingsymbol = i["tsym"], ord_tp = "MKT", sl = 0, buysell = "S", exch = i["exch"], prdct = i["prd"])
                 print(ord)

      def get_open_position(self):
          posns = self.position()
          pos = []
          if not posns:
             return "No open Positions."
          for i in posns:
              if i["netqty"] != 0:
                 pos.append("i")
          return pos

      def is_position_open(self, tsym):
          posns = self.position()
          pos = []
          if not posns:
             return False
          for i in posns:
              if i["tsym"] == tsym:
                 return True
          return False

      def __ws_run_forever(self):
          while True:
              try:
                  self.__wss.run_forever( ping_interval = 3,  ping_payload = '{"t": "h"}')
              except Exception as e:
                  "Error"
              sleep(0.1) # Sleep for 100ms between reconnection.

      def __ws_send(self, *args, **kwargs):
          while self.wss_connected == False:
              sleep(0.05)  # sleep for 50ms if websocket is not connected, wait for reconnection
          with self.__ws_mutex:
              ret = self.__wss.send(*args, **kwargs)
          return ret

      def __on_close(self, wsapp, close_status_code, close_msg):
          self.wss_connected = False
          print("WEBSOCKET closed.", close_msg)

      def __on_open(self, ws = None):
          print("Im in open callback.")
          self.wss_connected = True
          values = { "t": "c" }
          values["uid"] = self.userid
          values["pwd"] = self.password
          values["actid"] = self.userid
          values["susertoken"] = self.access_token
          values["source"] = self.ordsource             
          payload = json.dumps(values)
          #print(payload)
          self.__ws_send(payload)

      def __on_error(self, ws = None, error = None):
          print(error)

      def __on_data_callback(self, ws=None, message=None, data_type=None, continue_flag=None):
          res = json.loads(message)
          if res["tk"] not in self.LTP:
             self.LTP.update({str(msg['tk']): msg['lp']})

      def start_websocket(self,data_and_ord_callback=None):        
          """ Start a websocket connection for getting live data """
          url=self.wss_url
          #print(url)
          if not data_and_ord_callback:
             data_and_ord_callback=self.__on_data_callback
          self.__wss = websocket.WebSocketApp(url,
                                                on_data=data_and_ord_callback,
                                                on_error=self.__on_error,
                                                on_close=self.__on_close,
                                                on_open=self.__on_open)
          self.__ws_thread = threading.Thread(target=self.__ws_run_forever)
          self.__ws_thread.daemon = True
          self.__ws_thread.start()

      def subscribe(self, instrument, feed_type = "t"): #t:touchline d:
          values = {"t": feed_type}
          if type(instrument) == list:
             values['k'] = '#'.join(instrument)
          else :
             values['k'] = instrument
          data = json.dumps(values)
          self.__ws_send(data)
          self.subscribed.append(instrument.split("|")[1])

      def subscribe_orders(self):
          values = {'t': 'o'}
          values['actid'] = self.userid        
          data = json.dumps(values)
          reportmsg(data)
          self.__ws_send(data)
            
      def get_option_chain(self, exch, tradingsymbol, strikeprice, count = 50):
          """
          client.get_option_chain("NFO","BANKNIFTY30DEC21","37000",50)
          """
          url = self.url+self._root["option"]
          data = {"uid": self.userid, "exch": exch, "tsym": tradingsymbol,"strprc": str(strikeprice), "cnt": str(count)}
          res = self.api_helper(url, data = data, req_typ = "POST")
          if res["stat"] == "Not_Ok":
             return res
          else:
             return res

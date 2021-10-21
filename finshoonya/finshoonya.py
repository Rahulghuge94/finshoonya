import requests
import json,os
import time,datetime
import pandas as pd
#from retry import retry
from pytz import timezone

tze=timezone('Asia/Kolkata')#timezone to work with cloud instances.

class shoonya(object):
      _root={"jwt":"/jwt/token","login":"/trade/login",
              "fund":"/trade/getLimits","orderbook":"/trade/getOrderbook",
              "tradebook":"/trade/getTradebook","position":"/trade/getNetposition",
              "order":"/trade/placeorder","boco":"/trade/bracketorder",
              "cancel_order":"/trade/cancelorder"}
      
      headers={'Accept':'application/json, text/plain, */*','Accept-Encoding':'gzip, deflate, br','Accept-Language':'en-US,en;q=0.5',
                'Connection':'keep-alive','Content-Type':'application/x-www-form-urlencoded','Host':'shoonya.finvasia.com','Origin':'https://shoonya.finvasia.com',
                'Referer':'https://shoonya.finvasia.com/','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
      
      def __init__(self,email:str=None,password:str=None,pan:str=None):
          self.email=email.upper()
          self.password=password
          self.pan=pan.upper()
          self.username=self.email
          self.url="https://shoonya.finvasia.com"
          self.enctoken=None
          self.cookie=None
          self.key=None
          self.tokenid=None
          self.usercode=None
          self.session=requests.session()
    
      def login(self):
          self.session.get(self.url)
          temp={"userName":self.email,"pan":self.pan,"role":"admin","pass": self.password}
          data={str(temp):""}
          header=self.headers
          resp=self.session.post(self.url+self._root["jwt"],headers=header,data=data)
          self.enctoken=resp.text
          header.update({'Authorisation':'Token '+self.enctoken})
          resp=self.session.post(self.url+self._root["login"],headers=header,data=data)
          self.cookie=resp.headers['Set-Cookie'].replace("; Path=/; HttpOnly","")
          self.usercode=resp.json()["userdata"]['USERID']
          self.tokenid=resp.json()["userdata"]["TOKENID"]
          self.key=resp.json()["key"]
          self.headers.update({'Authorisation':'Token '+self.enctoken,"Cookie": self.cookie})
          self.write_cred()
          print('Logged In.')

      def fund(self):
          """
           returns funds in account.
           response structure
           {'LIMIT_TYPE': 'CAPITAL', 'LIMIT_SOD': '54208.47', 'ADHOC_LIMIT': '0.0', 'RECEIVABLES': 0.0, 'BANK_HOLDING': 0.0, 'COLLATERALS': 0.0, 'REALISED_PROFITS': 0.0,
           'AMOUNT_UTILIZED': '0.0', 'CLEAR_BALANCE': 54208.47, 'SUM_OF_ALL': '54208.47', 'AVAILABLE_BALANCE': '54208.47', 'SEG': 'A', 'PAY_OUT_AMT': '0.0', 'MTM_COMBINED': 0.0,
           'UNCLEAR_BALANCE': 0.0, 'MTF_AVAILABLE_BALANCE': '54208.47', 'MTF_UTILIZE': '0.0', 'MTF_COLLATERAL': '0.0', 'MF_COLLATERAL': '0.0'}
          """
          self.load_cred()
          temp={"token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}
          data={str(temp):""}
          resp=self.session.post(self.url+self._root["fund"],headers=self.headers,data=data).json()
          return resp[0]
        
      def update_header(self,temp:dict):
          temp.update({"token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C",
                "usercode":self.usercode,"pan_no":self.pan})
          return {str(temp):""}
        
      def orderbook(self):
          self.load_cred()
          temp={"row_1":"","row_2":"","exch":"","seg":"","product":"","status":"","inst":"","symbol":"","str_price":"","place_by":"",
                "opt_type":"","exp_dt":"","token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C",
                "usercode":self.usercode,"pan_no":self.pan}
          data={str(temp):""}
          resp=self.session.post(self.url+self._root["orderbook"],headers=self.headers,data=data).json()
          try:
              if resp["message"]=="Session Invalidate":
                 self.login()
                 data=self.update_header(temp)
                 resp=self.session.post(self.url+self._root["orderbook"],headers=self.header,data=data).json()
          except:
              pass
          return resp
        
      def position(self):
          self.load_cred()
          temp={"row_1":"","row_2":"","exch":"","seg":"","product":"","v_mode":"","status":"","Inst":"","symbol":"","str_price":"","place_by":"",
                "opt_type":"","exp_dt":"","token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}
          data={str(temp):""}
          print(data,self.__dict__)
          resp=self.session.post(self.url+self._root["position"],headers=self.headers,data=data).json()
          try:
              if resp["message"]=="Session Invalidate":
                 self.login()
                 data=self.update_header(temp)
                 resp=self.session.post(self.url+self._root["position"],headers=self.headers,data=data).json()
          except:
              pass
          return resp

      def tradebook(self):
          self.load_cred()
          temp={"row_1":"","row_2":"","exch":"","seg":"","product":"","status":"","symbol":"","cl_id":"","place_by":"",
                "str_price":"","token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}
          data={str(temp):""}
          resp=self.session.post(self.url+self._root["tradebook"],headers=self.headers,data=data).json()
          try:
              if resp["message"]=="Session Invalidate":
                 self.login()
                 data=self.update_header(temp)
                 resp=self.session.post(self.url+self._root["tradebook"],headers=self.headers,data=data).json()
                 return resp
          except:
              pass
          return resp

      def order(self,price,qty,secid,sl=0,buysell="B",exch="NSE",prdct="I",inst_tp='OPTIDX',disc_qty=0):
          """
          param:
             price: price at which you want to buy.
             qty: quantity
             sl: stop loss price in case of sl order.
             secid: security id or scrip id i.e. 3787 for wipro.
             buysell: "B" for buy and "S" for sell.
             exch: exchange "NSE","CDS","BSE" or "MCX"
             prdct: product of your order. "I"(intraday),"C"(cnc),"B"(bracket order),"V"(cover order),"M"(margin) for fno product
             Note: to take overnight position in derivative use product "M".
             ordtp: type of order "MKT"(market),"LMT"(limit), for stop loss just pass sl
             inst_tp: instrument type. 'OPTIDX' for index option,'OPTSTK' for stock option,'EQUITY' for equity,'FUTSTK' for stock future ,'FUTIDX' for index future.

             to place sl-m order just enter sl of your choice.
             to place normal order sl is zero. so bydefault it is zero dont have to touch it.
             enter required parameter only.
          """
          self.load_cred()
          temp=None
          ordtp="MKT"
          if price==0:
             price='MKT'
          elif price!=0:
             ordtp="LMT"
          elif sl!=0:
              price="MKT"
          temp={"qty":qty,"price":price,"odr_type":ordtp,"product_typ":prdct,"trg_prc":sl,"validity":"DAY","disc_qty":disc_qty,"amo":False,
                  "sec_id":secid,"inst_type":inst_tp,"exch":exch,"buysell":buysell,"gtdDate":"0000-00-00","mktProtectionFlag":"N","mktProtectionVal":0,
                  "settler":"000000000000","token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}       
          data={str(temp):""}
          order=self.session.post(self.url+self._root["order"],headers=self.headers,data=data).json()
          #print(order)
          #print(data)
          try:
              if order["message"]=="Session Invalidate":
                 self.login()
                 data=self.update_header(temp)
                 order=self.session.post(self.url+self._root["order"],headers=self.headers,data=data).json()
                 return order
          except:
              pass
          return order

      def order_bo_co(self,price:float,qty:int,secid:int,sl:float=0,bkpft:float=0,buysell:str="B",exch:str="NSE",prdct:str="I",inst_tp:str='OPTIDX'):
          """
          parameter:
             price: price at which you would like to buy or sell.
             qty: quantity
             secid: security id or scrip id i.e. 3787 for wipro.
             buysell: "B" for buy and "S" for sell.
             exch: exchange "NSE","CDS","BSE" or "MCX"
             prdct: product of your order. "I"(intraday),"C",(cnc),"B"(bracket order),"V"(cover order)
             ordtp: type of order "MKT"(market),"LMT"(limit), for stop loss just pass sl
             sl: stop loss
             bkpft: value at which you would like to book profit in case of bracket order.
             inst_tp: instrument type 'OPTIDX','OPTSTK','EQUITY','FUTSTK','FUTIDX'.
             
            to place order at market keep price 0.
          """
          self.load_cred()
          temp=None
          ordtp="MKT"
          if price==0:
             price='MKT'
             ordtp="MKT"
          else:
             ordtp="LMT"
          #bracket order.
          if bkpft!=0 and sl!=0:
             temp={"amo":False,"disclosequantity":0,"securityid":secid,"productlist":"B","inst_type":inst_tp,"iNoOfLeg":"3","qty":qty,"price":price,
                   "odr_type":ordtp,"buysell":buysell,"order_validity":"DAY","exch":exch,"sec_id":secid,"fPBTikAbsValue":bkpft,"fSLTikAbsValue":sl,
                   "fTrailingSLValue":0,"mktProtectionFlag":"N","trg_prc":0,"settler":"000000000000","token_id":self.tokenid,"keyid":self.key,"userid":self.username,
                   "clienttype":"C","usercode":self.usercode,"pan_no":self.pan} 
          if bkpft==0 and sl!=0: 
             temp={"amo":False,"disclosequantity":0,"securityid":secid,"product_typ":"V","inst_type":inst_tp,"qty":qty,"price":price,"odr_type":ordtp,
                   "buysell":buysell,"order_validity":"DAY","exch":exch,"sec_id":secid,"fSLTikAbsValue":sl,"mktProtectionFlag":"N","settler":"000000000000",
                   "token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}
          data={str(temp):""}
          order=self.session.post(self.url+self._root["boco"],headers=self.headers,data=data).json()
          try:
              if order["message"]=="Session Invalidate":
                 self.login()
                 data=self.update_header(temp)
                 order=self.session.post(self.url+self._root["boco"],headers=self.headers,data=data).json()
                 return order
          except:
              pass
          return order
        
      def getdata(self,secid:str,fdt:int=1,tdt:int=1,exch:str="NSE",seg:str="E"):
          """
           param:
              secid:scripcode or security id
              fdt: from date. required numbe like 2 for 2 days back data.
              tdt: to date
              seg: segment "E" for equity and "D" for derivative.
          """
          self.load_cred()
          headers={'Host': 'shoonyabrd.finvasia.com',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
                  "Accept": "*/*","Accept-Encoding": "utf-8","Accept-Language": "en-USen;q=0.5",
                  "Content-Length": "197","Origin": "https://shoonyabrd.finvasia.com","Connection": "keep-alive",
                  "Referer": "https://shoonyabrd.finvasia.com/Charts/chartw.html"}
          temp={"Exch":exch,"Seg":seg,"ScripId":str(secid),"FromDate":fdt,"ToDate":tdt,"Time":1}
          data={"Count": 10,"Data": str(temp),"DoCompress": False,
                "RequestCode": 800,"Reserved": "","Source": "W","UserId": self.username}
          return pd.DataFrame(self.session.post("https://shoonyabrd.finvasia.com/TickPub/api/Tick/LiveFeed",headers=self.headers,data=data).json())
        
      def get_last_candle(self,secid:str,exch:str="N",seg:str="D"):
          """
            return last candle of chart.
            param:
              seg "D" for derivative "E" for equity
              exch: exchange "N" for nse ,"B" for bse and "M" for mcx.
              secid:security id or scripcode
          """
          EXCH={"N":1,"B":2,"M":3}
          SEG={"E":1,"D":2}
          seg,exch=SEG[seg],EXCH[exch]
          headers={"Content-Type": "application/json","Connection": "Keep-Alive","Accept": "application/json"}
          temp={"SecIdxCode":secid,"Exch":exch,"ScripIdLst":[],"Seg":seg}
          data={"Count": 10,"Data": str(temp),"DoCompress": False,"RequestCode": 129,"Reserved": "","Source": "W","UserId": ""}
          return self.session.post("https://shoonyabrd.finvasia.com/TickPub/api/Tick/LiveFeed",headers=headers,json=data).json()

      def get_quote(self,secid:str,exch="N",seg="D"):
          """
            return QUOTE.
            param:
              seg "D" for derivative "E" for equity
              exch: exchange "N" for nse ,"B" for bse and "M" for mcx.
              secid:security id or scripcode
          """
          EXCH={"N":1,"B":2}
          SEG={"E":1,"D":2}
          seg,exch=SEG[seg],EXCH[exch]
          temp={"Seg": seg, "ScripIdLst": [f"{secid}"], "Exch": exch, "SecIdxCode": "-1"}
          data={"Count": "50","Data": str(temp),"DoCompress": False,"RequestCode": 131,"Reserved": "", "Source": "W","UserId": "","UserType": "C"}
          headers={"Content-Type": "application/json","Connection": "Keep-Alive","Accept": "application/json"}
          return self.session.post("https://shoonyabrd.finvasia.com/DataPub/api/SData/LiveFeed",headers=headers,json=data).json()
        
      def timestamp():
          tmstm=str(datetime.datetime.now(tz=tze).timestamp())
          tmstm=tmstm.replace(".","")
          ciqrand=tmstm[:13]
          return ciqrand

      #not useful.
      def getwatchlist(self,wname):
          temp={"wlname":wname,"token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}
          data={str(temp):''}
          return s.post("https://shoonya.finvasia.com/trade/getWatchlistDetail",headers=self.headers,data=data).json()

      #not useful.
      def addtowatchlist(self,scrip: list,wname: str,seg="D",exch="NSE"):
          for sc in scrip:
              data={str({"exch":exch,"secId":sc,"seg":seg,"wlName":wname,"token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}): ""}
              self.session.post('https://shoonya.finvasia.com/trade/addWatchlist',headers=self.headers,data=data).json()['status']

      def get_scripcode(self,srchstring:str):
          """
            return scripcode.
          """
          temp=[]
          headers={'Host': 'data.rupeetracker.in','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0','Accept': 'application/json, text/plain, */*',
                   'Accept-Language': 'en-US,en;q=0.5','Accept-Encoding': 'gzip, deflate, br','Referer': 'https://shoonya.finvasia.com/','Origin': 'https://shoonya.finvasia.com','Connection': 'keep-alive'}
          resp=self.session.get('https://data.rupeetracker.in/solr/scrip/select?wt=json&indent=true&q=((_Exch_s:xxx AND Seg_s:x)OR(_Exch_s:NSE AND Seg_s:E)OR(_Exch_s:NSE AND Seg_s:D)OR(_Exch_s:NSE AND Seg_s:C)OR(_Exch_s:BSE AND Seg_s:E)OR(_Exch_s:BSE AND Seg_s:C)OR(_Exch_s:MCX AND Inst_s:FUTCOM)OR(_Exch_s:MCX AND Inst_s:OPTCOM)OR(_Exch_s:MCX AND Inst_s:OPTFUT)OR(_Exch_s:NCDEX AND Inst_s:FUTCOM)OR(_Exch_s:NCDEX AND Inst_s:FUTCOM)OR(_Exch_s:NCDEX AND Inst_s:COM))& fq={!lucene q.op=AND df=SearcTerm_s}'+srchstring+'*&rows=150&sort=Inst_s asc,volume_i desc',headers=headers).json()
          if resp['response']['docs']:
             temp=[]
          for i in resp['response']['docs']:
              temp.append([i['Sid_s'],i['TradeSym_t']])
          return temp

      def get_open_position(self):
          pos=[]
          positions=self.position()
          if not positions:
             return pos
          for i in range(0,len(positions)):
              if positions[i]['NET_QTY']!=0:
                 pos.append([positions[i]['SECURITY_ID'],positions[i]['NET_QTY']])
          return pos

      def is_position_open(self,secid:int):
          open_pos=self.get_open_position()
          if not open_pos:
             return False
          else:
             for i in open_pos:
                 if int(i[0])==secid:
                    return True
      def load_cred(self):
          sessn=None
          data=None
          if os.path.isfile("cred.json"):
             sessn=open("cred.json","r")
             data=json.load(sessn)
          else:
             self.login()
          self.email=data["email"]
          self.password=data["password"]
          self.pan=data["pan"]
          self.username=data["username"]
          self.enctoken=data["enctoken"]
          self.cookie=data["cookie"]
          self.key=data["key"]
          self.tokenid=data["tokenid"]
          self.usercode=data["usercode"]
          self.headers.update({'Authorisation':'Token '+self.enctoken,"Cookie": self.cookie})
          
      def write_cred(self):
          sessn=open("cred.json","w")
          dic={"email":self.email,"password":self.password,"pan":self.pan,"username":self.username,
               "enctoken":self.enctoken,"cookie":self.cookie,"key":self.key,"tokenid":self.tokenid,"usercode":self.usercode}
          json.dump(dic,sessn)
      def order_detail(self,order_no:int):
          ordbk=self.orderbook()
          for i in ordbk:
              if i["ORDER_NUMBER"]==order_no:
                 return i
      def cancel_order(self,order_no):
          _ord=self.order_detail(order_no)
          {"exch":_ord["EXCHANGE"],"orderno":order_no,"scripname":_ord["SYMBOL"],"buysell":"B" if _ord["BUY_SELL"]=="Buy" else "S",
            "qty_type":_ord["ORDER_TYPE"],"qty":_ord["QUANTITY"],"prc":_ord["PRICE"],"trg_prc":_ord["TRG_PRICE"],"disc_qty":0,"productlist":"I",
            "order_typ":"DAY","sec_id":"3351","qty_rem":1,"inst_type":"E","offline_flag":False,
           
          temp={"qty":qty,"price":price,"odr_type":ordtp,"product_typ":prdct,"trg_prc":sl,"validity":"DAY","disc_qty":disc_qty,"amo":False,
                  "sec_id":secid,"inst_type":inst_tp,"exch":exch,"buysell":buysell,"gtdDate":"0000-00-00",
                  "settler":"000000000000","token_id":self.tokenid,"keyid":self.key,"userid":self.username,"clienttype":"C","usercode":self.usercode,"pan_no":self.pan}       
          data={str(temp):""}
          
      

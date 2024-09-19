from bs4 import BeautifulSoup
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import json
from functions import functions
from pydantic import BaseModel
import fake_useragent
from urllib3.util import create_urllib3_context
from urllib3 import PoolManager
from requests.adapters import HTTPAdapter
from requests import Session
import requests
import ssl

app=FastAPI()

# CORSを回避するために追加（今回の肝）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

#ラウンドワンサイトでrequestsを使うための設定
class AddedCipherAdapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    ctx = create_urllib3_context(ciphers=":HIGH:!DH:!aNULL")
    self.poolmanager = PoolManager(
      num_pools=connections,
      maxsize=maxsize,
      block=block,
      ssl_context=ctx
    )
#証明書認証が通らないため、その対策
class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)
    

@app.get("/")
async def read_root():
    return {"Hello":"Wod"}

@app.get("/{name}")
async def read_item(name:str):
    return {"Hello":name}
class Login(BaseModel):
    id1:int
    id2:int
    id3:int
    password:str

class Shop(BaseModel):
    shop_id:str

#待ち時間の取得
@app.post("/waitTime")
def get_wait_time(shop:Shop):
  shop_id=shop.shop_id
  url=f"https://www.round1.co.jp/yoyaku/queue/bowling/index.php?service_department_id=1&store_id={shop_id}"
  response=requests.get(url)
  soup=BeautifulSoup(response.content,"html.parser")

  info=soup.find("div",{"class","form_append"})

  nowTime=info.find("div",{"class","update-time"}).text.split("現")[0]
  groups=info.find_all("dd")[0].text.replace("\u2002","").split("組")[0]
  waitTime=info.find_all("dd")[1].text.replace("\u2002","").split("分")[0].split("約")[1]

  return [nowTime,groups,waitTime]

#以下、スコアの取得
@app.post("/login")
async def get_score_data(login:Login):
    id1=login.id1
    id2=login.id2
    id3=login.id3
    password=login.password

    # カスタムSSLコンテキストの作成
    context = ssl.create_default_context()
    context.check_hostname = False  # ホスト名の検証を無効化
    context.verify_mode = ssl.CERT_NONE  # SSL証明書の検証を無効化

    # カスタムSSLコンテキストの作成
    context.set_ciphers('DEFAULT:@SECLEVEL=1')  # セキュリティレベルを下げる

    session = Session()
    # session.mount("https://rmc.round1.co.jp/user_web/", AddedCipherAdapter())
    ua=fake_useragent.UserAgent()
    header={"user-agent":ua.chrome}
    data={
    'login_user_id':f"{id1}{id2}{id3}",
    'login_password':password,
    }
    # session.post(url, headers=header,data=data)

    adapter = SSLAdapter(ssl_context=context)
    session.mount('https://rmc.round1.co.jp/user_web/', adapter)

    url='https://rmc.round1.co.jp/user_web/etc/ajax_login.php'

    session.post(url,data=data,headers=header)

    #以下、ログイン後

    #スコアデータ取得
    score_data_res=session.get("https://rmc.round1.co.jp/user_web/my_score/index.php",headers=header)
    score_data_soup = BeautifulSoup(score_data_res.content, "html.parser")

    #日付の取得
    when_score_data=score_data_soup.find("span",{"class","f12"}).text
    today_score_data=functions.get_day(when_score_data)

    for score_data in score_data_soup.find_all("tr"):
        item=score_data.find("th").text
        score=score_data.find("td").text
        today_score_data.append([item,score])
    
    #データをjsonファイルに保存（一応過去のデータがないと後々）
    save_data(today_score_data)
    return today_score_data

def save_data(data):
    with open("data.json","w") as f:
        json.dump(data,f,indent=4,ensure_ascii=False)

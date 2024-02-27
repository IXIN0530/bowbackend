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
@app.post("/login")
async def get_score_data(login:Login):
    id1=login.id1
    id2=login.id2
    id3=login.id3
    password=login.password

    url='https://rmc.round1.co.jp/user_web/etc/ajax_login.php'
    session = Session()
    session.mount("https://rmc.round1.co.jp/user_web/", AddedCipherAdapter())
    ua=fake_useragent.UserAgent()
    header={"user-agent":ua.chrome}
    data={
    'login_user_id':f"{id1}{id2}{id3}",
    'login_password':password,
    }
    session.post(url, headers=header,data=data)

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

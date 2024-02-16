from bs4 import BeautifulSoup
from starlette.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fastapi import FastAPI
import json
from functions import functions
import os
app=FastAPI()

# CORSを回避するために追加（今回の肝）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

@app.get("/")
async def read_root():
    return {"Hello":"World"}

@app.get("/login/{id1}/{id2}/{id3}/{password}")
async def get_score_data(id1:int,id2:int,id3:int,password:str):
    
    #ヘッドレスモードでの実行
    options=Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
    driver=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=options)

    driver_path="./chrome/chromedriver"

    url="https://www.round1.co.jp/mypage/"
    # service=Service(executable_path=driver_path)
    # driver=webdriver.Chrome(service=service,options=options)
    driver.get(url)

    #フレーマーがある場合、そこに移動してから要素を取得する
    frame=driver.find_element(By.XPATH,"//iframe")
    driver.switch_to.frame(frame)

    id1_input=driver.find_element(By.XPATH,"//input[@name='login_user_id_1']")
    id2_input=driver.find_element(By.XPATH,"//input[@name='login_user_id_2']")
    id3_input=driver.find_element(By.XPATH,"//input[@name='login_user_id_3']")
    password_input=driver.find_element(By.XPATH,"//input[@name='login_password']")
    submit_button=driver.find_element(By.XPATH,"//input[@type='submit']")
    id1_input.send_keys(id1)
    id2_input.send_keys(id2)
    id3_input.send_keys(id3)
    password_input.send_keys(password)
    submit_button.click()

    try:
        element=WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div/nav/a[2]"))
        )
    finally:
        #mydataへアクセス
        myData_link=driver.find_element(By.XPATH,"/html/body/div/div[1]/div/nav/a[2]")
        myData_link.click()

    scoredatas=driver.find_elements(By.XPATH,"//tr")
    when_score_data=driver.find_element(By.XPATH,'/html/body/div/div[2]/section/p/span[2]')

    #データの日付を配列にして格納
    today_score_data=functions.get_day(when_score_data.text)
    for data in scoredatas:
        soup=BeautifulSoup(data.get_attribute("innerHTML"),"html.parser")
        today_score_data.append([soup.find("th").text,soup.find("td").text])
    
    #データをjsonファイルに保存（一応過去のデータがないと後々）
    save_data(today_score_data)
    return today_score_data

def save_data(data):
    with open("data.json","w") as f:
        json.dump(data,f,indent=4,ensure_ascii=False)
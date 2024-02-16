# from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#ヘッドレスモードでの実行
options=Options()
options.add_argument('--headless')

driver_path="/Users/yamaguchimasahiro/bowling/app/backend/chrome/chromedriver"

url="https://www.round1.co.jp/mypage/"
url1="https://www.google.com/"
service=Service(executable_path=driver_path)
driver=webdriver.Chrome(service=service,options=options)
driver.get(url)

#フレーマーがある場合、そこに移動してから要素を取得する
frame=driver.find_element(By.XPATH,"//iframe")
driver.switch_to.frame(frame)

class Info:
    def __init__(self):
        self.Id1=1182
        self.Id2=524
        self.Id3=797
        self.password=""
Me=Info()
Me.password=input("パスワードを入力してください")
id1_input=driver.find_element(By.XPATH,"//input[@name='login_user_id_1']")
id2_input=driver.find_element(By.XPATH,"//input[@name='login_user_id_2']")
id3_input=driver.find_element(By.XPATH,"//input[@name='login_user_id_3']")
password_input=driver.find_element(By.XPATH,"//input[@name='login_password']")
submit_button=driver.find_element(By.XPATH,"//input[@type='submit']")

id1_input.send_keys(Me.Id1)
id2_input.send_keys(Me.Id2)
id3_input.send_keys(Me.Id3)
password_input.send_keys(Me.password)
submit_button.click()


#ログイン完了後の動き
try:
    element=WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,"/html/body/div/div[1]/div/nav/a[3]"))
    )
finally:
    print("ログイン完了")
score_link=driver.find_element(By.XPATH,"/html/body/div/div[1]/div/nav/a[3]")
score_link.click()

#スコアシートの取得
try:
    element=WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,"//li[@class='sheet_list']/a"))
    )
finally:
    print("スコアシート存在確認")

scores=driver.find_elements(By.XPATH,"//li[@class='sheet_list']/a")
# print(len(scores))
for i in range(len(scores)):
    time.sleep(2)
    if i==0: 
        re_score=driver.find_elements(By.XPATH,f"/html/body/div/div[2]/ul/li[{1}]/a")
        if len(re_score)==0:
            print("スコアシートが見つかりませんでした")
        else:
            print(f"iは{i},{len(re_score)}この要素が発見されました")
            re_score[0].click()
    try:
        element=WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"//*[@id='download_button']/a"))
        )
    finally:
        print(f"{6*i+1}~{6*(i+1)}のスコア取得完了")
        #.back()で戻らないことに注意
        if i==0:
            back_butotn=driver.find_element(By.XPATH,"//*[@id='download_wrap']/div[1]/nav/ul/li[2]/a")
            download_button=driver.find_element(By.XPATH,"//a[@class='button download-button']")
            download_button.click()
            back_butotn.click()
        elif i!=len(scores)-1:
            back_butotn=driver.find_element(By.XPATH,"//*[@id='download_wrap']/div[1]/nav/ul/li[3]/a")
            download_button=driver.find_element(By.XPATH,"//a[@class='button download-button']")
            download_button.click()
            back_butotn.click()
        else:
            download_button=driver.find_element(By.XPATH,"//a[@class='button download-button']")
            download_button.click()
time.sleep(100)
driver.quit()


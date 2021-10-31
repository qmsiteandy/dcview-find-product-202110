import requests
import time 
from bs4 import BeautifulSoup
import schedule  

#已通知過的商品ID紀錄，避免重複通知
usedID = []

#抓取DCview資料，搜尋對應商品，傳送訊息
def FindInDCview():
    print("FindInDCview:", time.ctime(time.time()))

    #----------Grab----------
    # 步驟一：
    result = requests.get("http://market.dcview.com/") #get 該網址的 HTML

    # 步驟二：
    soup = BeautifulSoup(result.text,"html.parser") #將網頁資料以 html.parser 解析器來解析
    #print(soup) #印出至畫面

    # 步驟三：
    datas = soup.find('table', 'table').tbody.find_all(class_="data-list-xs visible-xs")
    #print(datas)
    
    items = []

    for data in datas:
        #商品連結&ID0
        s_href = data.find('a').get('href')
        splitHref = s_href.split('/')
        s_id = splitHref[len(splitHref)-1]
        #徵或售
        s_mode = data.find(class_='btn-xs').text
        #縣市&品項名稱
        s_topic = data.find(class_='h5').text.strip()
        s_location = s_topic.split(']')[0].replace("[", "")
        s_name = s_topic.split(']')[1].strip()
        #價格
        s_price = data.find(class_='price').text.split()[0].replace(",", "")
        i_price = int(s_price)


        items.append({'id':s_id, 'mode':s_mode, 'location':s_location, 'name':s_name, 'price':i_price, 'href':s_href})
        
    #----------Compare----------    
    mode = '售'
    target_names = ['A73','A7iii','A7m4']
    budget = 38000
    locations = ['台北市','新北市']

    import re

    for item in items:

        #確認是否為出售
        if item['mode'] != mode: continue

        #搜尋名稱中是否有符合關鍵字
        for target_name in target_names:
            name_match = False
            if re.search(target_name, item['name'], re.IGNORECASE):
                name_match = True
                print(item['mode'], item['location'], item['name'], item['price'])
                msg = (item['mode'] +' ['+ item['location'] +']'+ item['name'] +' '+ str(item['price']) +'元 \n\n')
                break

        #此商品含所需關鍵字        
        if name_match:
            #確認此商品是否已通知過，避免重複通知
            b_used = False
            for used_id in usedID:
                if used_id == item['id']:
                    b_used = True
                    break
            if b_used == True: print('已通知過')
            else:    
                usedID.append(item['id'])
                #確認符合預算
                if(item['price'] <= budget): 
                    print('O符合預算/' + str(budget), end = ' ')
                    msg += 'O符合預算/'
                else: 
                    print('X超過預算/' + str(budget), end = ' ')
                    msg+= 'X超過預算/'
                #確認地區
                for location in locations:
                    location_match = False
                    if item['location'] == location: 
                        location_match = True
                        break
                if location_match: 
                    print('O地區符合')
                    msg+= 'O地區符合'
                else:
                    print('X地區不符合')
                    msg+= 'X地區不符合'
                #加上超連結
                msg += '\n-----------\n' + item['href']


                #傳送此商品資訊到LINE   
                SendLineMsg (msg)    
                
def SendLineMsg (msg):     
    token = 'eXcB8Q9b6OT7fggGcOAE2UZzDwis3WSEBd7QOxCEXgF'   
    headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded"
        }    
    params = {"message": msg}

    r = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, params=params)



schedule.every(5).minutes.at(":00").do(FindInDCview)  
while True:  
    schedule.run_pending()  
    time.sleep(10)  
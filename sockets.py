from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import json,httplib
from datetime import datetime

import time
chrome_options = Options()
chrome_options.add_argument("--headless")
cd_driver = webdriver.Chrome(chrome_options=chrome_options)
cd_driver.get('https://coindelta.com/market?active=XRP-INR')

def processCurrency(cd,kx,currency):
        lowest_buy_price = float(kx[currency]['lowest_ask'])
        highest_sell_price_min = float(cd[currency]['highest_bid'])
        highest_sell_price_max = float(cd[currency]['lowest_ask'])
        return lowest_buy_price,highest_sell_price_min,round((highest_sell_price_min/lowest_buy_price * 100)-100,2),round((highest_sell_price_max/lowest_buy_price * 100)-100,2)


def sendNotification(message):
    connection = httplib.HTTPSConnection('api.pushed.co', 443)
    connection.connect()
    connection.request('POST', '/1/push', json.dumps({
      "app_key": "zJXwOVU4QPkJz8maAcwj",
      "app_secret": "8dm245WwJurFASQJ7VI6HjRHKAcKp60a5wI7uJLVxAvPBZncv89eimWIrpSg9lFT",
      "target_type": "app",
      "content": message}),
      {
    	"Content-Type": "application/json"
      }
    )
    result = json.loads(connection.getresponse().read())

def extractKoinexData():
    url = 'https://koinex.in/api/ticker'
    data = requests.get(url).json()['stats']
    return data

def extractCoinDeltaData():
    if 'complete' in cd_driver.execute_script('return document.readyState'):
        table = cd_driver.find_element_by_xpath('/html/body/div[1]/div[2]/section/div/div[2]/div[1]/div/div/div[2]/table/tbody')
        cd_dict = {}
        table_data = processTable(table)
        for row in table_data:
            a = {}
            currency = row[0]
            a['last_traded_price'] = row[1]
            a['lowest_ask'] = row[3]
            a['highest_bid'] = row[2]
            cd_dict[currency] = a
            if '--' in str(a):
                return {}
        return cd_dict
    else:
        return {}

def processTable(table):
    rows = table.find_elements_by_tag_name('tr')
    table_data = []
    for row in rows:
        row_data = processRow(row)
        table_data.append(row_data)
    return table_data


def processRow(row):
    cells = row.find_elements_by_tag_name('td')
    row_data = []
    for cell in cells:
        cell_data = "".join(str(cell.get_attribute('innerText')).split()).upper().replace(',','')
        row_data.append(cell_data)
    return row_data

currency_list = ['LTC', 'ETH', 'BCH', 'XRP', 'BTC']
threshold = 0

while (True):
    cd = extractCoinDeltaData()
    if 'BTC' in cd.keys():
        kx = extractKoinexData()
        result = ""
        for currency in currency_list:
            curr = processCurrency(cd,kx,currency)
            if (float(curr[2]) > threshold or float(curr[3]) > threshold):
                if result == "":
                    result = currency + " (" + str(curr[2]) + "," + str(curr[3]) + ")"
                else:
                    result = result + "  " + currency + " (" + str(curr[2]) + "," + str(curr[3]) + ")"
        #sendNotification(result)
        myfile = open("Log.txt", "a")
        myfile.write(str(datetime.now()) + "\t" + result + "\n")
        print result
        break

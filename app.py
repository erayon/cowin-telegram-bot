from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests, os, geocoder
import datetime, telegram
import schedule, os
import time, json

class MyCowinSelenium:

    def __init__(self):
        self.driver = None
        self.waiting = 5

    def get_latlng(self):
        g = geocoder.ip('me')
        val = g.latlng
        lat, lng = val[0], val[1]
        return lat, lng
    
    def web_driver_quit(self):
        if self.driver!= None: self.driver.quit()

    def web_driver_load(self):
        lat, lng = self.get_latlng()
        geo = webdriver.FirefoxOptions()
        geo.add_argument("--headless")
        geo.set_preference("geo.enabled", True)
        geo.set_preference('geo.prompt.testing', True)
        geo.set_preference('geo.prompt.testing.allow', True)
        location = 'data:application/json,{"location": {"lat": %s, "lng": %s}, "accuracy": 100.0}'
        location = (location)%(lat,lng)
        geo.set_preference('geo.provider.network.url', location)
        geo.set_preference('devtools.jsonview.enabled', False)
        self.driver = webdriver.Firefox(options=geo)
    
    def get_response(self,url):
        try:
            self.web_driver_load()
            self.driver.get(url)
            # rawdata_tab = '//*[@id="rawdata-tab"]'
            # self.driver.find_element_by_xpath(rawdata_tab).click()
            # time.sleep(5)
            val = self.driver.find_element_by_tag_name('pre').text
            data = json.loads(val)
            return data
        except NoSuchElementException:
            return "NoSuchElementException"
        except Exception as e:
            return "Error in code"
        finally:
            self.web_driver_quit

class MyCowin():

    def __init__(self):
        self.locations = os.environ.get("LOCATION").split(",")
        self.district_id = int(os.environ.get("DISTRICT_ID"))
        self.telegram_token = os.environ.get("TELEGRAM_TOKEN_ID")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    def calender_res(self):
        date_ = datetime.datetime.strftime(datetime.datetime.now(),'%d-%m-%Y')
        self.url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(self.district_id,date_)
        payload={}
        headers = {}
        response = requests.request("GET", self.url, headers=headers, data=payload)
        return response

    def formatter(self,res):
        tmp = []
        for i in res['centers']:
            for x in self.locations:
                if x in i['name'].lower():
                    for each in i['sessions']:
                        if int(each['available_capacity']) > 0:
                            tmp.append([i['name'], each['date'], each['available_capacity']]) 
        return tmp   

    def watcher(self):
        res = self.calender_res()
        if res.status_code==200:
            tmp = self.formatter(res.json())
        elif res.status_code == 403:
            cowin_sel = MyCowinSelenium()
            res = cowin_sel.get_response(self.url)
            if type(res) == dict:
                tmp = self.formatter(res)
            else:
                return res
        else:
            tmp = []
        return tmp

    def send_msg(self):
        res = self.watcher()
        if res and (type(res)==list):
            tp = []
            for e in res:
                st = ' , '.join(str(v) for v in e)
                tp.append(st)
            bot = telegram.Bot(token=self.telegram_token)
            bot.sendMessage(chat_id = self.telegram_chat_id, text = "\n".join(tp))
        elif res and (type(res)==str):
            bot = telegram.Bot(token=self.telegram_token)
            bot.sendMessage(chat_id = self.telegram_chat_id, text = res)
        else:
            pass


cowin = MyCowin()

start_time  = "07:00"
end_time    = "23:45"  

def job():
    on_time       = datetime.datetime.now().time()
    checkin_time  = datetime.datetime.strptime(start_time, '%H:%M').time()
    checkout_time = datetime.datetime.strptime(end_time, '%H:%M').time()
    if ( on_time > checkin_time ) and ( on_time < checkout_time ):
        print("Working............")
        cowin.send_msg()

if __name__ == "__main__":
    schedule.every(5).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
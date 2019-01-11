#imports

from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from datetime import datetime
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import sys

#settings
url = "https://pure360.pure-yoga.com/en/TW?location_id=24"
classes = [{"date":"Wed Jan 9","time":"17:00"}]

#classes = [{"date":"Mon Jan 7","time":"06:30"},{"date":"Mon Jan 7","time":"09:00"},{"date":"Mon Jan 7","time":"11:00"},{"date":"Mon Jan 7","time":"14:00"}]


book_datetime = datetime(2019, 1, 7, 9, 0, 0)
#book_datetime = datetime(2019, 1, 6, 21, 8, 50)
is_running = True

# create a new Chrome session
browser = webdriver.Chrome()
browser.implicitly_wait(30)
browser.get(url)

sign_in_button = browser.find_element_by_id('sign-in-btn')
time.sleep(1)
sign_in_button.click()
time.sleep(2)
username = browser.find_element_by_id("username")
username.clear()
username.send_keys("huohsien@gmail.com")
time.sleep(1)
password = browser.find_element_by_id("password")
password.clear()
password.send_keys("jj121632")
time.sleep(1)
login_button = browser.find_element_by_name('login')
login_button.click()
time.sleep(1)
data_soup = BeautifulSoup(browser.page_source,'lxml')

def reserve_class(browser, classes):
    for c in classes:
       # class to be booked, specify date and time
        td = browser.find_element_by_xpath("//td[@data-date='" + c['date'] + "'][@data-time='" + c['time'] + "']")
        button = td.find_element_by_xpath(".//button")
        button.click()
        time.sleep(4)
    
    global is_running
    time.sleep(3)
    is_running = False
    browser.quit()


# Start the scheduleruler
scheduler = BackgroundScheduler()
job = scheduler.add_job(reserve_class, 'date', run_date= book_datetime, args=[browser, classes])
scheduler.start()

while is_running:
    time.sleep(60)
    sys.stdout.write('.'); sys.stdout.flush()


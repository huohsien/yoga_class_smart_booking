from lxml import html

from bs4 import BeautifulSoup
import time
from datetime import datetime
import threading
from apscheduler.schedulers.background import BackgroundScheduler

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import json
import os
import sys

course_schedule = []
is_running = True

def sync_get_element_by_xpath(xpath):
    wait.until(ec.visibility_of_element_located((By.XPATH, xpath)))
    return driver.find_element_by_xpath(xpath)
def teacher_norm(teacher):
    if not teacher.startswith('-'):
        return teacher
    tmp = teacher.split('\n')[0].split('- ')[1]
    return tmp[:-2]

def search_courses_by_date(date_str, courses):
    results = []
    
    date_str = date_str.strip()
    
    for item in courses:
        if date_str in item['date']:
            results.append(item)
    return results

def search_courses_by_teacher(teacher_str, courses=course_schedule):
    results = []
    
    teacher_str = teacher_str.strip()
    
    for item in courses:
        if teacher_str in item['teacher']:
            results.append(item)
    return results
def search_courses_by_name(name_str, courses=course_schedule):
    results = []
    
    name_str = name_str.strip()
    
    for item in courses:
        if name_str in item['name']:
            results.append(item)
    return results

def search_courses_by_time(time_str, courses=course_schedule):
    results = []
    
    time_str = time_str.strip()
    
    for item in courses:
        if time_str in item['time']:
            results.append(item)
    return results

def click_book_this_class_now():
    btn = driver.find_element_by_xpath("//a[contains(text(), 'BOOK THIS CLASS NOW')]")
    btn_click()
def list_courses_to_be_booked(courses_to_be_booked):
    if len(courses_to_be_booked) <= 0:
        return
    print("Date: {}".format(courses_to_be_booked[0]['date']))
    print("-----------------------\n")
    for course in courses_to_be_booked:
        print("Name: {}".format(course['name']))
        print("Teacher: {}".format(course['teacher']))
        print("Time: {}".format(course['time']))
        print("\n")
    print("-----------------------")
    
#setup option for chrome profile
chrome_options = Options()
# chrome_options.add_argument("user-data-dir=/Users/huohsien/Library/Application Support/Google/Chrome/Default/")

#start web driver
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.implicitly_wait(60)

wait = WebDriverWait(driver, 30)

def sign_in():
    username = driver.find_element_by_id('ctl00_cphContents_txtUsername')
    password = driver.find_element_by_id('ctl00_cphContents_txtPassword')
    username.send_keys("DN20092360")
    password.send_keys("jj1216")

    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "submit-button")))
    sign_in_btn = driver.find_element_by_class_name("submit-button") 
    sign_in_btn.click()

def click_book_for_class():
    click_btn = sync_get_element_by_xpath("//a[contains(text(), 'Book for Class')]")
#     print("click_btn: ", click_btn)
    click_btn.click()
    
#launch url
base_url = "https://www.trueclassbooking.com.tw/member/search-class.aspx"
driver.get(base_url)
sign_in()
click_book_for_class()

with open(r"07 September - 13 September 2020.json", "r") as read_file:
    course_schedule = json.load(read_file)

book_datetime = datetime(2020, 9, 8, 22, 0, 0)
courses_to_be_booked = []
c = search_courses_by_date('Sat', course_schedule)
c = search_courses_by_name('Iyengar', c)
c = search_courses_by_teacher('Ani', c)
courses_to_be_booked.extend(c)

c = search_courses_by_date('Sat', course_schedule)
c = search_courses_by_teacher('CoCo', c)
courses_to_be_booked.extend(c)

list_courses_to_be_booked(courses_to_be_booked)

def reserve_class():
    
    start = time.time()
    for course_to_be_booked in courses_to_be_booked:
        book_url = course_to_be_booked['href']
        driver.get(book_url)
        btn = driver.find_element_by_xpath("//a[contains(text(), 'BOOK THIS CLASS NOW')]")
        btn.click()
    print("Time Elapsed: {:.4g\f}".format(time.time() - start))
    click_book_for_class()
    global is_running
    time.sleep(3)
    is_running = False
    browser.quit()
        
   
# Start the scheduleruler
scheduler = BackgroundScheduler()
job = scheduler.add_job(reserve_class, 'date', run_date= book_datetime)
scheduler.start()

while is_running:
    time.sleep(60)
    sys.stdout.write('.'); sys.stdout.flush()
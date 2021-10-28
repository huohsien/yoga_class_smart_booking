from selenium.common.exceptions import NoSuchElementException        
from selenium.common.exceptions import TimeoutException

from lxml import html

# from bs4 import BeautifulSoup
from bs4 import BeautifulSoup, NavigableString
import time
import datetime
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

def check_exists_by_xpath(driver, xpath):
    
    driver.implicitly_wait(1)
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        driver.implicitly_wait(30)
        return False
    driver.implicitly_wait(30)
    return True

def sync_get_element_by_xpath(driver, xpath):
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(ec.visibility_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
#         print("Get element from xpath:{} Timeout".format(xpath))
        return None
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

def search_courses_by_teacher(teacher_str, courses):
    results = []
    
    teacher_str = teacher_str.strip()
    
    for item in courses:
        if teacher_str in item['teacher']:
            results.append(item)
    return results

def search_courses_by_name(name_str, courses):
    results = []
    
    name_str = name_str.strip()
    
    for item in courses:
        if name_str in item['name']:
            results.append(item)
    return results

def search_courses_by_time(time_str, courses):
    results = []
    
    time_str = time_str.strip()
    
    for item in courses:
        if time_str in item['time']:
            results.append(item)
    return results

def click_book_this_class_now(driver):
    btn = driver.find_element_by_xpath("//a[contains(text(), 'BOOK THIS CLASS NOW')]")
    btn_click()
    
def list_courses_to_be_booked(courses_to_be_booked):
    
    if len(courses_to_be_booked) <= 0:
        return
    
    cur_date = ''
    print("-----------------------")
    for idx, course in enumerate(courses_to_be_booked):  

        if cur_date != course['date']:
            if cur_date != '':
                print("-----------------------")
            print("Date: {}".format(course['date']))
            print("-----------------------\n")
            cur_date = course['date']
        print("Name: {}".format(course['name']))
        print("Teacher: {}".format(course['teacher']))
        print("Time: {}".format(course['time']))
        if idx < len(courses_to_be_booked) - 1:
            print("")
    print("-----------------------")
        
def scheduled_sign_in(driver, wait):
    #     print("scheduled_sign_in({},{})".format(driver, wait))
    driver.get(base_url)
    sign_in(driver, wait)


def reserve_class(driver, wait, course_to_be_booked):
    print("reserve_class: ({})\n".format(course_to_be_booked['time']))
    book_url = course_to_be_booked['href']
    driver.get(book_url)
    click_book_this_class_now(driver, wait)

def create_new_driver():
    # setup option for chrome profile
    # chrome_options = Options()
    # chrome_options.add_argument("user-data-dir=/Users/huohsien/Library/Application Support/Google/Chrome/Default/")
    options = Options()

    if NO_WINDOW:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')

    # start web driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)

    wait = WebDriverWait(driver, EXPLICIT_WAIT_TIME)
    return driver, wait

def sign_in(driver, wait):
    username = driver.find_element_by_id('ctl00_cphContents_txtUsername')
    password = driver.find_element_by_id('ctl00_cphContents_txtPassword')
    username.send_keys("DN20092360")
    password.send_keys("jj1216")

    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "submit-button")))

    sign_in_btn = driver.find_element_by_class_name("submit-button")
    sign_in_btn.click()


def log_out(driver, wait):
    click_btn = helper.sync_get_element_by_xpath(driver, "//a[contains(text(), 'Logout')]")
    #     print("click_btn: ", click_btn)
    if click_btn:
        click_btn.click()


def click_book_for_class(driver, wait):
    click_btn = helper.sync_get_element_by_xpath(driver, "//a[contains(text(), 'Book for Class')]")
    #     print("click_btn: ", click_btn)
    if click_btn:
        click_btn.click()


def click_book_this_class_now(driver, wait):
    click_btn = helper.sync_get_element_by_xpath(driver, "//a[contains(text(), 'BOOK THIS CLASS NOW')]")
    click_btn.click()
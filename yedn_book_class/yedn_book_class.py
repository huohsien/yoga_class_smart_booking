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

import yedn

##################################
## Need to change every time
#
YEAR = 2020
MONTH = 10
Day = 1
#
##################################
num_book_classes = 0
course_schedule = []
# NO_WINDOW = False
IMPLICIT_WAIT_TIME = 20
EXPLICIT_WAIT_TIME = 20
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 920

is_running = True

#launch url
base_url = "https://www.trueclassbooking.com.tw/member/search-class.aspx"
with open(r'/Users/huohsien/workspace/python/yoga_class_smart_booking/class_schedules/28 September - 04 October 2020.json', "r") as read_file:
    course_schedule = json.load(read_file)

book_datetime = datetime.datetime(YEAR, MONTH, Day, 22, 0, 0)
temp = []

##################################
## Need to change every time
#

# book_datetime = datetime.datetime(YEAR, MONTH, Day, 22, 0, 0)
# temp = []
#
# c = yedn.search_courses_by_date('1', course_schedule)
# c = yedn.search_courses_by_name('Tone', c)
# c = yedn.search_courses_by_teacher('Una', c)
# c = yedn.search_courses_by_time('PM', c)
# # c = helper.search_courses_by_name('Hatha', c)
# temp.extend(c)
#
#
#
# courses_to_be_booked = []
# courses_to_be_booked.append(temp[0])
# # courses_to_be_booked.append(temp[2])
# # courses_to_be_booked.append(temp[1])
#
# # Set Sign In time 10 minutes before the open for booking time
# signin_datetime = book_datetime - datetime.timedelta(seconds=600)
# # set time shift for booking
# book_datetime = book_datetime + datetime.timedelta(seconds=0.0)

#
##################################

##################################
## TEST CODE
#

NUM_CLASSES = 1
DELAY_BETWEEN_CLASSSES = 3
BASE_DELAY = 4
TEST_SIGNIN_SECONDS_DELAY_FROM_NOW = BASE_DELAY
TEST_BOOK_CLASSES_SECONDS_DELAY_FROM_NOW =  (NUM_CLASSES-1) * DELAY_BETWEEN_CLASSSES + BASE_DELAY*2

signin_datetime = datetime.datetime.now() + datetime.timedelta(seconds=TEST_SIGNIN_SECONDS_DELAY_FROM_NOW)
book_datetime = datetime.datetime.now() + datetime.timedelta(seconds=TEST_BOOK_CLASSES_SECONDS_DELAY_FROM_NOW)

print("Now: {}".format(datetime.datetime.now()))
courses_to_be_booked = []

c = yedn.search_courses_by_date('29', course_schedule)
c = yedn.search_courses_by_name('Mysore', c)
# c = helper.search_courses_by_teacher('Una', c)

courses_to_be_booked.extend(c)

#
##################################

yedn.list_courses_to_be_booked(courses_to_be_booked)

def scheduled_sign_in(driver, wait):
    #     print("scheduled_sign_in({},{})".format(driver, wait))
    global base_url
    driver.get(base_url)
    yedn.sign_in(driver, wait)
    print("driver {}\nSigned in. Now is {}".format(driver, datetime.datetime.now()))


def reserve_class(driver, wait, course_to_be_booked):
    print("reserve_class: ({})\n".format(course_to_be_booked['time']))
    book_url = course_to_be_booked['href']
    driver.get(book_url)
    yedn.click_book_this_class_now(driver, wait)
    global num_book_classes
    global is_running
    num_book_classes = num_book_classes - 1
    print("driver {}\n'BOOK THIS CLASS NOW' button was clicked'. Now is {}".format(driver, datetime.datetime.now()))
    if num_book_classes == 0:
        is_running = False
        driver.quit()

drivers = []
waits = []
scheduler = BackgroundScheduler()
# start = time.time()
for idx, course_to_be_booked in enumerate(courses_to_be_booked):

    driver, wait = yedn.create_new_driver(NO_WINDOW=True)
    driver.set_window_position(WINDOW_WIDTH * idx, 0);
    driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    signin_datetime_var = signin_datetime + datetime.timedelta(seconds=(idx+1)*1)
    print("idx: ", idx, " signin datetime: ", signin_datetime_var)
    print("idx: ", idx, " book datetime: ", book_datetime)
    scheduler.add_job(scheduled_sign_in, 'date', run_date=signin_datetime_var, args=[driver, wait])
    scheduler.add_job(reserve_class, 'date', run_date= book_datetime, args=[driver, wait, course_to_be_booked])
    num_book_classes = num_book_classes + 1
# print("Time Elapsed: {:.2f}".format(time.time() - start))
scheduler.start()

while is_running:
    time.sleep(60)
    if is_running == False:
        break
    sys.stdout.write('.'); sys.stdout.flush()
print("Done!")




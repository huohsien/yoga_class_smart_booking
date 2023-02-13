from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import json
import os

import time

from PyQt5 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)

Form = QtWidgets.QWidget()
Form.setWindowTitle('VHHC Studio')
Form.resize(600, 400)

#launch url
base_url = "https://www.trueclassbooking.com.tw/member/search-class.aspx"

class_schedules_folder_path = './class_schedules'

course_schedule = []

#setup option for chrome profile
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
#start web driver
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.implicitly_wait(30)

wait = WebDriverWait(driver, 30)

from selenium.common.exceptions import NoSuchElementException
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def sync_get_element_by_xpath(xpath):
    wait.until(ec.visibility_of_element_located((By.XPATH, xpath)))
    return driver.find_element_by_xpath(xpath)
def send_keys(elm, string):
    for c in string:
        elm.send_keys(c)


def sign_in():
    username = driver.find_element_by_id('ctl00_cphContents_txtUsername')
    password = driver.find_element_by_id('ctl00_cphContents_txtPassword')
    #     username.send_keys("DN20092360")
    #     password.send_keys("jj1216")
    send_keys(username, "DN20092360")
    send_keys(password, "jj1216")
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "submit-button")))
    sign_in_btn = driver.find_element_by_class_name("submit-button")
    sign_in_btn.click()


def click_book_for_class():
    click_btn = sync_get_element_by_xpath("//a[contains(text(), 'Book for Class')]")
    #     print("click_btn: ", click_btn)
    click_btn.click()


def teacher_norm(teacher):
    if not teacher.startswith('-'):
        return teacher
    tmp = teacher.split('\n')[0].split('- ')[1]
    return tmp[:-2]


def search_courses_by_date(date_str, courses=course_schedule):
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


def get_course_schedule_table_title():
    return driver.find_element_by_xpath("//div[@class='tbl-header']").get_attribute('innerText')


def click_next_week_btn():
    print("#0")
    if check_exists_by_xpath("//*[@class='btnCircleRight']"):
        print("%1")
        btns = driver.find_elements_by_class_name('btnCircleRight')
    else:
        print("@1")
        return False

    print("#1")
    if btns is not None:

        if not len(btns) == 1:
            return False

        print("#2")
        btns[0].click()

        return True
    else:
        print("#3")
        return False


def click_previous_week_btn():
    if check_exists_by_xpath("//*[@class='btnCircleLeft']"):
        btns = driver.find_elements_by_class_name('btnCircleLeft')
    else:
        print("@2")
        return False

    if btns is not None:

        assert len(btns) == 1

        btns[0].click()
        return True
    else:
        return False

def scrape_a_week():
    course_schedule = []
    header_titles = []

    room_td_elms = driver.find_elements_by_xpath("//div[@class='studios']/table/tbody/tr[1]/td")

    for room_idx in range(len(room_td_elms)):
        room_select_btn = room_td_elms[room_idx].find_element_by_xpath("./span")
        room_label = room_select_btn.find_element_by_xpath("./label")
        room_name = room_label.get_attribute('innerText')

        if room_name == 'DN 6 PT Room':
            continue

        print("waiting...")
        room_select_btn.click()
        room_td_elms = driver.find_elements_by_xpath("//div[@class='studios']/table/tbody/tr[1]/td")

        th_elms = driver.find_elements_by_xpath("//div[@class='tbl-container']/table/tbody/tr[1]/th")
        for idx, th_elm in enumerate(th_elms):
            header_title = th_elm.get_attribute("innerText")
            header_titles.append(header_title)

        td_elms = driver.find_elements_by_xpath("//div[@class='tbl-container']/table/tbody/tr[2]/td")

        for idx, td_elm in enumerate(td_elms):
            # skip useless Column data of 'TIME'
            if idx == 0:
                continue
            a_elms = td_elm.find_elements_by_xpath("./a")

            for a_elm in a_elms:
                course = {}
                course['room'] = room_td_elms[room_idx].get_attribute("innerText")
                course['date'] = header_titles[idx]
                course['href'] = a_elm.get_attribute('href')
                span_1 = a_elm.find_element_by_xpath("./span[1]")
                course['name'] = span_1.get_attribute('innerText')
                span_2 = a_elm.find_element_by_xpath("./span[2]")
                tmp_str = span_2.get_attribute('innerText')

                teacher_str = tmp_str.split('\n')[0]
                time_str = tmp_str.split('\n')[1]

                course['teacher'] = teacher_norm(teacher_str)
                course['time'] = time_str

                course_schedule.append(course)

                title_name = get_course_schedule_table_title()
                filename = os.path.join(class_schedules_folder_path, title_name + '.json')
                with open(filename, 'w', encoding='utf-8') as fp:
                    json.dump(course_schedule, fp)
    return course_schedule

def get_class_schedule():
    driver.get(base_url)
    sign_in()
    click_book_for_class()

    os.makedirs(class_schedules_folder_path, exist_ok=True)

    # click_next_week_btn()
    course_schedule = scrape_a_week()
    time.sleep(3)
    driver.quit()
    print("Finish getting class schedule of this week")



btn1 = QtWidgets.QPushButton(Form)
btn1.setText('Get Class Schedule of this week')
btn1.setGeometry(50,60,250,30)
btn1.clicked.connect(get_class_schedule)

Form.show()
sys.exit(app.exec_())
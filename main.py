import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def make_authors_list(filepath):
    authors = set()
    with open(filepath, newline='') as csvfile:
        author_reader = csv.reader(csvfile, delimiter=';')
        for row in author_reader:
            if row[0] == "":
                continue
            else:
                authors.add(row[0])
    return authors


def make_lots_by_artist_name_dict(driver, authors):
    dict_with_lots_links = {}
    driver.maximize_window()
    for author in authors:
        for name in author.split('--'):
            dict_with_lots_links[name] = []
            get_page_lots_by_artist(driver, name)
            if wait_until_lots_loaded(driver):
                continue
            number_lots = get_number_of_lots(driver)
            if number_lots == 0:
                continue
            else:
                add_links_to_dict_by_artist(driver, name, dict_with_lots_links, (number_lots + 119) // 120)
    return dict_with_lots_links


def get_page_lots_by_artist(driver, name):
    driver.get(f"https://www.phillips.com/Search?Search={name.replace(' ', '+')}")


def wait_until_lots_loaded(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                    "//div/div/div/div"
                                                                    "[@class = 'item-count-display']")))
        return False
    except TimeoutException:
        return True


def get_number_of_lots(driver):
    return int(re.findall(r"\d+", driver.find_element_by_xpath("//div/div/div/div"
                                                               "[@class = 'item-count-display']").text)[0])


def add_links_to_dict_by_artist(driver, name, dict_with_lots_links, number_pages):
    for i in range(1, number_pages + 1):
        scroll_page_down(driver)
        add_links_for_lot_dict(driver, name, dict_with_lots_links)
        get_next_page(driver, name, i, number_pages)



def get_next_page(driver, name, i, number_pages):
    if (i != number_pages) and (number_pages != 1):
        driver.get(f'https://www.phillips.com/search/{i + 1}?search={"%20".join(name.lower().split())}')


def scroll_page_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def add_links_for_lot_dict(driver, name, dict_with_lots_links):
    for now in range(len(driver.find_elements_by_xpath("//body/div/div/div/ul/li"))):
        cur_lot = get_current_lot(driver, now)
        title_cur_lot = get_title_current_lot(driver, cur_lot)
        if name.upper() in title_cur_lot:
            add_link_to_dict(dict_with_lots_links, name, cur_lot)


def get_current_lot(driver, now):
    return driver.find_element_by_xpath(f"//body/div/div/div/ul/li[{now + 1}]")


def get_title_current_lot(driver, cur_lot):
    try:
        wait_until_find_class_maker(driver)
    except TimeoutException:
        refresh_current_page(driver)
        try:
            wait_until_find_class_maker(driver)
        except TimeoutException:
            return "NoSuchElements"
    try:
        return cur_lot.find_element_by_class_name('maker').text
    except NoSuchElementException:
        refresh_current_page(driver)
        try:
            return cur_lot.find_element_by_class_name('maker').text
        except NoSuchElementException:
            return "NoSuchElements"


def wait_until_find_class_maker(driver):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "maker")))


def refresh_current_page(driver):
    driver.find_element_by_tag_name("body").send_keys(Keys.F5)


def add_link_to_dict(dict_with_lots_links, name, cur_lot):
    dict_with_lots_links[name].append(get_link_for_lot(cur_lot))


def get_link_for_lot(cur_lot):
    return cur_lot.find_element_by_class_name("image-link").get_attribute("href")


dict_with_lots_links = make_lots_by_artist_name_dict(webdriver.Chrome(),
                                                     make_authors_list("arts2.csv"))

f = open("dict_with_lots_links.txt", "w")
f.write(str(dict_with_lots_links))
f.close()
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import hashlib
import hmac
from checklib import *
from time import sleep

def quit_driver_wrapper(driver):
    def _quit_driver_internal(sig, frame):
        if driver:
            driver.quit()

    return _quit_driver_internal

def captcha(nonce):
    return hmac.new(b"d528291b1e8e61b84389760fce409faf9c4be2c3", nonce.encode(), hashlib.sha1).hexdigest()

def wait_id(driver, idx, where):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, idx))
        )
    except TimeoutException:
        cquit(Status.DOWN, f"Timeout on {where}")

def click(driver, idx, F, o=False):
    try:
        wait_id(driver, idx, F)
        elem = driver.find_element_by_id(idx)
        if o:
            elem = elem.find_element_by_xpath('./..')
        elem.click()
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find {idx} on {F}")

def fill(driver, idx, text, F):
    try:
        wait_id(driver, idx, F)
        driver.find_element_by_id(idx).send_keys(text)
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find {idx} on {F}")


def get_value(driver, idx, F):
    try:
        wait_id(driver, idx, F)
        while True:
            text = driver.find_element_by_id(idx).get_attribute('value')
            if text != '':
                break
            sleep(0.2)
        return text
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find {idx} on {F}")

def screen(driver, name):
    driver.save_screenshot(f'{name}.png')
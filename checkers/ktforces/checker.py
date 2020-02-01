#!/usr/bin/env python3

import os
import sys
from selenium import webdriver
from traceback import format_exc
import signal
import random
from selenium.common.exceptions import ElementClickInterceptedException
from auxiliary import *

import check_action
import put_action
import get_action
import requests

VULNS = "5"

driver = None

def get_driver():
    global driver

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'user-agent={rnd_useragent()}')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')


    while True:
        # noinspection PyBroadException
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(20)
        except:
            continue
        else:
            break

    signal.signal(signal.SIGINT, quit_driver_wrapper(driver))
    signal.signal(signal.SIGTERM, quit_driver_wrapper(driver))

    driver.set_window_size(1264, 1264)

def close_driver():
    global driver
    if driver != None:
        driver.quit()
        driver = None

if __name__ == '__main__':
    try:
        action = sys.argv[1]
        if action == 'info':
            cquit(Status.OK, f"vulns: {VULNS}")
        elif action == 'check':
            get_driver()
            check_action.run(driver, sys.argv[2])
        elif action == 'put':
            get_driver()
            put_action.run(driver, *sys.argv[2:])
        elif action == 'get':
            get_driver()
            get_action.run(driver, *sys.argv[2:])
        else:
            cquit(Status.ERROR, 'System error', 'Invalid action provided')
    except ElementClickInterceptedException:
        close_driver()
        cquit(Status.DOWN, "With love from stable checker <3", "Fking ClickInterceptedException")
    except SystemExit:
        close_driver()
        raise
    except Exception as e:
        tb = format_exc()
        close_driver()
        cquit(Status.ERROR, 'System error', f'Error: {e}\n{tb}')

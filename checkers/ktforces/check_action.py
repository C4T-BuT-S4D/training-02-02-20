import random
from selenium.common.exceptions import NoSuchElementException
from auxiliary import *
from ktforces_lib import *


def run(driver, ip):
    
    mch1 = CheckMachine(ip, driver)

    driver.get(mch1.url)

    mch1.register()
    mch1.login()

    mch1.check_profile()

    mch1.create_task()

    mch1.logout()

    mch2 = CheckMachine(ip, driver)

    try:
        wait_id(driver, "fl-close", "logout")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find close button after logout")
    driver.implicitly_wait(1.5)
    click(driver, "fl-close", "logout")

    mch2.register()
    mch2.login()

    try:
        wait_id(driver, "me-button", "login")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't login after task creation")

    mch2.open_task(mch1.task)

    mch2.logout()

    try:
        wait_id(driver, "fl-close", "logout")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find close button after logout")
    driver.implicitly_wait(1.5)
    click(driver, "fl-close", "logout")

    mch1.login()
    mch1.check_user_profile(mch2.n, mch2.u)

    cquit(Status.OK)

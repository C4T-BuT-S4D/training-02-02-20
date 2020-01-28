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
        wait_id(driver, "fl-close", "No close button after logout")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find close button after logout")
    sleep(0.5)
    click(driver, "fl-close", "logout")

    mch2.register()
    mch2.login()

    mch2.open_task(mch1.task)

    mch2.logout()

    driver.get(mch1.url)

    mch1.login()
    mch1.check_user_profile(mch2.n, mch2.u)

    cquit(Status.OK)

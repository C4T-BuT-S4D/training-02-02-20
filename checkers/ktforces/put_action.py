import random
from selenium.common.exceptions import NoSuchElementException
from auxiliary import *
from ktforces_lib import *


def run(driver, ip, flag_id, flag, vuln):
    
    mch1 = CheckMachine(ip, driver)

    driver.get(mch1.url)

    if vuln == "1":
        mch1.register(flag)
        mch1.login()
        try:
            wait_id(driver, "me-button", "login")
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"login")
    else:
        mch1.register()
        mch1.login()

        try:
            wait_id(driver, "me-button", "login")
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"login")

        mch1.create_task(flag, vuln, True)

    cquit(Status.OK, f"{mch1.u}:{mch1.p}:{mch1.task['id'] if vuln != '1' else ''}")

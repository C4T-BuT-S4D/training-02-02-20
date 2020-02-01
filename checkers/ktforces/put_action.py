import random
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
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

    driver.get(f"{mch1.url}tasks/")

    try:
        wait_id(driver, "t-list", "check_task")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't open task list")

    tasks = re.findall('.{8}-.{4}-.{4}-.{4}-.{12}', driver.page_source)

    for task in tasks:
        try:
            driver.get(f"{mch1.url}tasks/{task}/")
            try:
                wait_id(driver, "tv-data", 'check_task', 3)
            except NoSuchElementException:
                cquit(Status.MUMBLE, f"Can't find tv-data on task_view")
        except UnexpectedAlertPresentException:
            pass

    cquit(Status.OK, f"{mch1.u}:{mch1.p}:{mch1.task['id'] if vuln != '1' else ''}")

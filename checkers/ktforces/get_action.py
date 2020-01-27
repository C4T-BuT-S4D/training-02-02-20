import random
from selenium.common.exceptions import NoSuchElementException
from auxiliary import *
from ktforces_lib import *
import re


def run(driver, ip, flag_id, flag, vuln):
    
    mch1 = CheckMachine(ip, driver)

    driver.get(mch1.url)

    mch1.u, mch1.p, task_id = flag_id.split(':')

    mch1.login()

    if vuln == "1":
        mch1.check_profile(False)
    else:
        mch1.check_task(task_id, flag)

    driver.get(f"{mch1.url}tasks/")

    try:
        wait_id(driver, "t-list", "check_task")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't find task_id on task_list")

    tasks = re.findall('.{8}-.{4}-.{4}-.{4}-.{12}', driver.page_source)

    for task in tasks:
        driver.get(f"{mch1.url}tasks/{task}/")
        try:
            wait_id(driver, "tv-data", 'check_task')
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"Can't find tv-data on task_view")

    cquit(Status.OK)
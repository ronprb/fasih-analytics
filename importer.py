import json
import os
import time
import httpx
from selenium import webdriver

COOKIE_CACHE_PATH = "input/session_cache.json"
_TEST_URL = "https://fasih-sm.bps.go.id/survey/api/v1/surveys/datatable?surveyType=Pencacahan"
_TEST_PAYLOAD = {"pageNumber": 0, "pageSize": 1, "sortBy": "CREATED_AT", "sortDirection": "DESC", "keywordSearch": ""}


def _save_session(cookies_dict, csrf_token):
    os.makedirs("input", exist_ok=True)
    with open(COOKIE_CACHE_PATH, "w") as f:
        json.dump({"cookies": cookies_dict, "csrf_token": csrf_token}, f)


def _load_session():
    if os.path.exists(COOKIE_CACHE_PATH):
        with open(COOKIE_CACHE_PATH) as f:
            data = json.load(f)
        return data.get("cookies"), data.get("csrf_token")
    return None, None


def _session_valid(cookies_dict, csrf_token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://fasih-sm.bps.go.id",
        "Referer": "https://fasih-sm.bps.go.id/survey-collection/survey",
        "User-Agent": "Mozilla/5.0",
        "X-XSRF-TOKEN": csrf_token,
    }
    try:
        response = httpx.post(_TEST_URL, headers=headers, cookies=cookies_dict, json=_TEST_PAYLOAD, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def get_cookies_and_csrf():
    cookies, csrf_token = _load_session()
    if cookies and csrf_token:
        print("🔄 Checking cached session...")
        if _session_valid(cookies, csrf_token):
            print("✅ Cached session valid, skipping login.\n")
            return cookies, csrf_token
        print("⚠️  Cached session expired, re-logging in...\n")

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    print("🔐 Opening browser... please log in manually.")
    driver.get("https://fasih-sm.bps.go.id")
    input("✅ After logging in completely, press ENTER to continue...")

    driver.get("https://fasih-sm.bps.go.id/survey-collection/survey")
    time.sleep(1)

    selenium_cookies = driver.get_cookies()
    csrf_token = None
    for cookie in selenium_cookies:
        if cookie['name'].lower() in ['x-xsrf-token', 'xsrf-token']:
            csrf_token = cookie['value']
    driver.quit()

    cookies_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
    _save_session(cookies_dict, csrf_token)
    print("💾 Session cached for next run.\n")
    return cookies_dict, csrf_token


def get_payload(region1Id, surveyPeriodId):
    return {
        "filterTargetType":"TARGET_ONLY",
        "region1Id": region1Id,
        "region2Id": None,
        "region3Id": None,
        "region4Id": None,
        "region5Id": None,
        "region6Id": None,
        "region7Id": None,
        "region8Id": None,
        "region9Id": None,
        "region10Id": None,
        "surveyPeriodId": surveyPeriodId,
        "assignmentErrorStatusType": -1,
        "assignmentStatusAlias": None,
        "data1": None,
        "data2": None,
        "data3": None,
        "data4": None,
        "data5": None,
        "data6": None,
        "data7": None,
        "data8": None,
        "data9": None,
        "data10": None,
        "userIdResponsibility": None,
        "currentUserId": None,
        "regionId": None
        }

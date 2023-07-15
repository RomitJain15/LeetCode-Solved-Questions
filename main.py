from bs4 import BeautifulSoup  # For Web Scraping
import time  # For Adding Sleep Time
import pandas as pd  # Used for Data Manipulation
# --------------- Browser Automation Imports -------------
from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
# ---------------------------------------------
import gspread
import os

siteUrl = 'https://leetcode.com/problemset/all/'
solvedQuestionNameList = []
solvedQuestionUrlList = []
solvedQuestionDifficultyList = []
pageLocator = 0

def openBrowser(url):
    global pageLocator
    print("     -----------> Opening Browser")
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    if '--headless' in options.arguments:
        pageLocator = 5
    else:
        pageLocator = 8

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    
    driver.get(url)
    driver.maximize_window()
    WebDriverWait(driver, 10).until(EC.title_contains("Problems - LeetCode"))

    return driver

def sign_in(driver):
    sign_in_button = driver.find_element(By.LINK_TEXT, 'Sign in')
    sign_in_button.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'signin_btn')))
    email_input = driver.find_element(By.ID, 'id_login')
    email_input.send_keys('jainromit15@gmail.com')
    password_input = driver.find_element(By.ID, 'id_password')
    password_input.send_keys('Romit@1508')
    time.sleep(1)
    login_button = driver.find_element(By.ID, 'signin_btn')
    login_button.click()

def closeBrowser(driver):
    print("     -----------> Closing Browser")
    driver.close()

def fetchPageData(browser):
    time.sleep(2)
    pageSource = browser.page_source
    WebDriverWait(browser, 20).until(EC.title_contains("Problems - LeetCode"))
    
    soup = BeautifulSoup(pageSource, 'html.parser')
    if (browser.title == "Problems - LeetCode"):
        print("\n\n------------------- Parsing data -------------------\n\n")
        questionBlock = soup.find('div', role='rowgroup')
        questionList = questionBlock.find_all('div', role='row')    
        for question in questionList:
            row = question.find_all('div', role='cell')
            if row[0].find('svg', class_='chakra-icon css-1hwpjif') is not None:
                questionName = row[1].find('a').text
                questionUrl = row[1].find('a')['href']
                questionUrl = 'https://leetcode.com' + questionUrl
                questionDifficulty = row[4].find('span').text
                solvedQuestionNameList.append(questionName)
                solvedQuestionUrlList.append(questionUrl)
                solvedQuestionDifficultyList.append(questionDifficulty)
                print(questionName, questionUrl, questionDifficulty)
        print("\n\n-----------> Done")

    else:
        print("Page does not exist or connection failed, status code: ", soup.status_code)
    return

def gsheets():
    global solvedQuestionNameList, solvedQuestionDifficultyList, solvedQuestionUrlList

    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file_path = os.path.join(script_dir, 'key.json')
    gc = gspread.service_account(filename=key_file_path)

    worksheet = gc.open_by_key('1y0xREEYhm3s7Sa1c4uo_gw30OStr33pzKLgGl_NvU6I')
    current_sheet = worksheet.worksheet("Solved Questions")
    current_sheet.clear()
    current_sheet.update('A1', [['Question Name']])
    current_sheet.update('B1', [['Question Url']])
    current_sheet.update('C1', [['Question Difficulty']])
    
    for i in range(2, len(solvedQuestionNameList) + 2):
        current_sheet.update(f'A{i}:C{i}', [[solvedQuestionNameList[i-2], solvedQuestionUrlList[i-2], solvedQuestionDifficultyList[i-2]]])
        time.sleep(3)

def getData():
    try:
        browser = openBrowser(siteUrl)
        time.sleep(1.5)
        pageSource = browser.page_source
        WebDriverWait(browser, 10).until(EC.title_contains("Problems - LeetCode"))
        soup = BeautifulSoup(pageSource, 'html.parser')

        if (browser.title == "Problems - LeetCode"):
            totalPages = soup.find('nav', role='navigation').find_all('button')[pageLocator].text
            print(f"Total {totalPages} pages available")
            if "Sign out" not in soup.text:
                sign_in(browser)
                time.sleep(2)
                pageSource = browser.page_source
                time.sleep(3)
                soup = BeautifulSoup(pageSource, 'html.parser')

            for page in range(1, int(totalPages) + 1):
                print(f"\n\n------------------- Fetching Page {page} -------------------\n\n")
                fetchPageData(browser)
                if page == 56:
                    break
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='next']")))
                next_button = browser.find_element(By.XPATH, "//button[@aria-label='next']")
                next_button.click()
            # print(solvedQuestionNameList)
            # print(solvedQuestionDifficultyList)
            # print(solvedQuestionUrlList)
            print("-----------> Done all pages ")
            print(f"Total {len(solvedQuestionNameList)} questions fetched")
            closeBrowser(browser)

        else:
            print("Connection Failed")
            return

    except Exception as e:
        print("Some error occurred, error: ", e)
        return

if __name__ == "__main__":
    getData()

# --------- Insert values into Gsheet --------
gsheets()
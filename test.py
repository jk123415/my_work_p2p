import time
from selenium import webdriver
import selenium.webdriver.chrome.service as service

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Remote('http://localhost:9515',desired_capabilities=options.to_capabilities())
driver.get('https://wap.xiaogelicai.com/pro_det?borrowId=1508');
print(driver.page_source)
time.sleep(2) # Let the user actually see something!
driver.close()

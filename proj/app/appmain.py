from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.chrome.options import Options
import os, sys

baseprojectpath = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)) 
            )
baseprojectpathexists = False
for syspath in sys.path:
    if baseprojectpath == syspath :
        baseprojectpathexists = True
        break

if not baseprojectpathexists :
    sys.path.append(baseprojectpath)

from proj.app.crawl.categorycrawl import CategoryCrawl
from proj.common.database.dbmanager import DatabaseManager
from proj.common.config.configmanager import ConfigManager


def close(driver):
    if driver is not None:
        driver.close()


def main():
    configmanager = ConfigManager()
    databasemanager = DatabaseManager(configmanager.database_object_list)

    CHROMEDRIVER_PATH = 'D:/_1.project/WEBuilder/python_project/crawling/proj/resource/chromedriver.exe'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    chrome_options.add_argument( "--headless" )
    chrome_options.add_argument( "--no-sandbox" )
    chrome_options.add_argument( "--disable-gpu" )
    # chrome_options.add_argument( f"--window-size={ WINDOW_SIZE }" )
    
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
    
    categorycrawl = CategoryCrawl(driver)
    categorycrawl.parse(databasemanager.insert_many_mongo)

    close(driver)

if __name__ == '__main__': 
    main()
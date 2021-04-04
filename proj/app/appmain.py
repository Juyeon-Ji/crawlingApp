import os
import sys
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
from proj.app.crawl.productcrawl import ProductCrawl
from proj.common.database.dbmanager import DatabaseManager
from proj.common.config.configmanager import ConfigManager

def close(driver):
    if driver is not None:
        driver.close()

def main():
    logging.info('Crawl Test')
    configmanager = ConfigManager()
    databasemanager = DatabaseManager(configmanager.database_object_list)
    # proejct_path = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
    # print(proejct_path)


    # os.chdir(proejct_path)
    # D:\_1.project\WEBuilder\python_project\git_crawling\crawlingApp\proj\resource\application.json

    # CHROMEDRIVER_PATH = Path.joinpath(proejct_path, r'/resource/chromedriver.exe')
    CHROMEDRIVER_PATH = 'D:/_1.project/WEBuilder/python_project/git_crawling/crawlingApp/proj/resource/chromedriver.exe'

    print(CHROMEDRIVER_PATH)
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument( f"--window-size={ WINDOW_SIZE }" )
    
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)

    categorycrawl = CategoryCrawl(driver=driver,
                                  crawl_config=configmanager.crawl_config_object)

    categorycrawl.parse(databasemanager.insert_many_mongo)

    json_datas = databasemanager.find_all_mongo('category')

    category = ProductCrawl(driver=driver,
                            json_data=json_datas,
                            func=databasemanager.insert_many_mongo,
                            crawl_config=configmanager.crawl_config_object)

    logging.info('Crawl Test End')
    close(driver)

if __name__ == '__main__': 
    main()
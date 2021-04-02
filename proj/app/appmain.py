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

def close(driver):
    if driver is not None:
        driver.close()

def main():
    CHROMEDRIVER_PATH = 'proj/resource/chromedriver.exe'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    chrome_options.add_argument( "--headless" )
    chrome_options.add_argument( "--no-sandbox" )
    chrome_options.add_argument( "--disable-gpu" )
    # chrome_options.add_argument( f"--window-size={ WINDOW_SIZE }" )
    
    driver = webdriver.Chrome( executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options )
    
    categoryCrawl = CategoryCrawl(driver)
    categoryCrawl.parse()

    close(driver)

if __name__ == '__main__': 
    main()
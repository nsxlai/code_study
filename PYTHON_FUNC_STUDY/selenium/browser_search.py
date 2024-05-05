"""
https://realpython.com/modern-web-automation-with-python-and-selenium/

For Windows machine, need to down the ChromeDriver from this link:
https://chromedriver.chromium.org/downloads

"""
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from time import sleep


if __name__ == '__main__':
    # For FireFox
    # opts = Options()
    # opts.headless = True
    # assert opts.headless  # Operating in headless mode

    # For Chrome
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    chrome_path = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'

    browser = Chrome(chrome_path, options=chrome_options)
    browser.get('https://duckduckgo.com')
    sleep(2)
    search_form = browser.find_element_by_id('search_form_input_homepage')
    search_form.send_keys('real python')
    search_form.submit()
    results = browser.find_elements_by_class_name('result')
    print(results[0].text)
    browser.close()

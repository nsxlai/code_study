from selenium import webdriver

webdriver_path = '/usr/bin/chromedriver'


if __name__ == '__main__':
    browser = webdriver.Chrome(webdriver_path)
    browser.get('http://www.google.com')
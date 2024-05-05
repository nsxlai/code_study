"""
For Windows machine, need to down the ChromeDriver from this link:
https://chromedriver.chromium.org/downloads
"""
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from time import sleep


if __name__ == '__main__':
    # For Chrome
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    # chrome_path = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    chrome_path = '/Users/ray.lai/cruise/chromedriver'

    vehicle_dict = {'Zuppa': '5G21A6P05L4100115'}
    browser = Chrome(chrome_path, options=chrome_options)
    browser.get('https://starfleet.robot.car/fleet/vehicles')
    sleep(2)
    # search_form = browser.find_element_by_id('search_form_input_homepage')
    class_name = "MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"
    search_form = browser.find_elements_by_class_name(class_name)
    search_form = browser.find
    search_form.send_keys('poppy')
    search_form.submit()
    results = browser.find_elements_by_class_name('result')
    # print(results[0].text)
    print(results)
    browser.close()

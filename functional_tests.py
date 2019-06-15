from selenium import webdriver

browser = webdriver.Edge()
browser.get('http://localhost:5000')

assert 'DRAFT' in browser.title.upper()

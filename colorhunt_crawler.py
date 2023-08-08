from bs4 import BeautifulSoup
import requests
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# headless background execution
Options = Options()
Options.headless = True

print("start")
url = "https://colorhunt.co/palettes/popular"
browser = webdriver.Chrome()
print("hello1")
browser.get(url)
print("hello")
# request web page
html = BeautifulSoup(requests.get(url).content, 'lxml').text

# parse the HTML
soup = BeautifulSoup(html, "html.parser")
mydivs = soup.find_all("div", {"class": "item"})
print(mydivs)
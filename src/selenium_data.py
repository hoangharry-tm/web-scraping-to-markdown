from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

driver.get("https://www.elsevier.com/resources/anatomy?query=&page=473&sortBy=alphabeticalAsc")

# Find the h2 element using XPath
h2_element = driver.find_element(By.CSS_SELECTOR, "[data-heading-level='3']");

# Get the text from the h2 element
text = h2_element.text

# Print the text
print(text)

while True:
  pass

driver.close()

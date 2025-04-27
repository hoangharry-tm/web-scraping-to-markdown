from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome()

driver.get("https://www.elsevier.com/resources/anatomy?query=&page=579&sortBy=alphabeticalAsc")

with open("./cache-requests/selenium_test.txt", "w") as f:
    f.write(driver.page_source)

# example: find all input elements with type='text'
elements = driver.find_elements(By.CSS_SELECTOR, "h2[data-heading-level='3']")
print(elements)
# Print the text
for element in elements:
    print(element.text)
    print(element.get_attribute("outerHTML"))

driver.close()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service as ChromeService

# Setting up the Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.maximize_window()

try:
    # Navigate to the homepage
    driver.get("https://clear-sky-debt-settlement-2b44b15cca88.herokuapp.com/home")

    email= driver.find_element(By.ID, "email")
    email.send_keys("nimathing1995@gmail.com")

    password = driver.find_element(By.ID, "password")
    password.send_keys("Test@123")

    button_sub = driver.find_element(By.XPATH, "//button[@type='submit']")
    button_sub.click()

    # Wait for the "Add an Expense" button to be clickable and click it
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-link"))
    ).click()

    # Delay to allow page to load
    time.sleep(3)  # You can adjust the delay based on your network speed

    # Fill in the "Item Purchased" text field
    item_name_input = driver.find_element(By.ID, "item_name")
    item_name_input.send_keys("Shoes")

    # Enter the amount
    amount_input = driver.find_element(By.ID, "amount")
    amount_input.send_keys("100")

    # Select from the "Group ID" dropdown
    group_select = Select(driver.find_element(By.ID, "group_id"))
    group_select.select_by_value("1")

    # Select from the "Payer ID" dropdown
    payer_select = Select(driver.find_element(By.ID, "payer_id"))
    payer_select.select_by_value("1")

    # Select from the "Debtor ID" dropdown
    debtor_select = Select(driver.find_element(By.ID, "debtor_id"))
    debtor_select.select_by_value("2")

    # Click the submit button
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    # Delay to allow page to load
    time.sleep(3)

    # Check if the transaction was added successfully
    success_message = driver.find_element(By.TAG_NAME, "body").text
    assert "Transaction added successfully" in success_message
    print("Successful validation of Transaction")

finally:
    # Close the driver
    driver.quit()


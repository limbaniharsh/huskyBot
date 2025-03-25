import csv
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


def check_exists(driver, by, xpath):
    """ Checks if an element exists and is enabled on the page."""
    try:
        e = driver.find_element(by, xpath)
    except NoSuchElementException:
        return False
    return e.is_enabled()


def confirm_cookies_if_present(driver):
    """ Checks if a cookies consent banner is present and clicks the 'Accept All Cookies' button if found. """
    if check_exists(driver, By.XPATH, "//button[contains(@data-ui-id,'accept-all-cookies')]"):
        cookies_accept = driver.find_element(
            By.XPATH,
            "//button[contains(@data-ui-id,'accept-all-cookies')]"
        )
        cookies_accept.click()


def wait_until_page_is_fully_load(driver, timeout=10):
    """ Waits for the page to fully load by checking the document ready state."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_for_ajax(driver, timeout=10):
    """  Waits for all AJAX requests to complete by checking jQuery's active request count. """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return jQuery.active == 0")
    )


def scroll_down(driver):
    """ Scrolls smoothly to the footer of the page. """
    driver.execute_script(
        "document.getElementsByTagName('footer')[0].scrollIntoView({behavior: 'smooth', block: 'center'})")


def scroll_to_element(driver, element):
    """ Scrolls smoothly to bring the specified element into view. """
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", element)


def scroll_to_img_wait_until_load(driver, img_element, timeout=10):
    """ Scrolls to an image element and waits for it to load completely. """
    scroll_to_element(driver, img_element)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return arguments[0].complete", img_element)
    )


def wait_until_all_image_load(driver):
    """ Waits for all images on the page to be fully loaded. """
    images = driver.find_elements(By.TAG_NAME, "img")
    print(f"Found {len(images)}")

    for img in images:
        scroll_to_img_wait_until_load(driver, img)


def wait_until_knowledge_based_page_load(driver, timeout=20):
    """ Waits for a knowledge-based page to finish loading by checking for specific loading elements. """
    WebDriverWait(driver, timeout).until(
        lambda d: check_exists(driver, By.CLASS_NAME, "ext_loading"))

    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            r"return Array.from(document.getElementsByClassName('ext_loading')).every((e)=> e.style.display == 'none')"))


def write_into_csv(data, filename):
    """
        Appends data to a CSV file. If the file doesn't exist, it writes the header first.

        The data should be a list of dictionaries, where each dictionary has the keys
        corresponding to the CSV fieldnames ("file", "URL").
    """
    should_write_header = os.path.exists(filename)

    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["file", "URL"])
        if not should_write_header:
            writer.writeheader()
        writer.writerows(data)



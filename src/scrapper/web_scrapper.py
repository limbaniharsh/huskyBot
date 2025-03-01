import csv
import os
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.print_page_options import PrintOptions


def check_exists(driver, by, xpath):
    try:
        e = driver.find_element(by, xpath)
    except NoSuchElementException:
        return False
    return e.is_enabled()


def wait_until_page_is_fully_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_for_ajax(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return jQuery.active == 0")
    )


def scroll_down(driver):
    driver.execute_script("document.getElementsByTagName('footer')[0].scrollIntoView({behavior: 'smooth', block: 'center'})")


def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", element)


def scroll_to_img_wait_until_load(driver, img_element, timeout=3):
    scroll_to_element(driver, img_element)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return arguments[0].complete", img_element)
    )


def wait_until_all_image_load(driver):
    images = driver.find_elements(By.TAG_NAME, "img")
    print(f"Found {len(images)}")

    for img in images:
        scroll_to_img_wait_until_load(driver, img)


def wait_until_knowledge_based_page_load(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        lambda d: check_exists(driver, By.CLASS_NAME, "ext_loading"))

    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(r"return Array.from(document.getElementsByClassName('ext_loading')).every((e)=> e.style.display == 'none')"))


def write_into_csv(data, filename):
    should_write_header = os.path.exists(filename)

    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["file", "URL"])
        if not should_write_header:
            writer.writeheader()
        writer.writerows(data)


def create_save_pdf(driver, url, file_name):

    wait_until_all_image_load(driver)
    scroll_down(driver)

    print_options = PrintOptions()
    pdf = driver.print_page(print_options)

    with open(BASE_FOLDER + file_name + ".pdf", 'wb') as f:
        print(f"Writing -{url} - into {file_name}")
        f.write(base64.b64decode(pdf))

    completed_links_file.append({"file": file_name, "URL": url})


def scrapper(driver, base_url, data):
    for space in data:
        page_count = 0
        while len(data[space]) > 0:
            page_count += 1
            rel_url = data[space].pop()
            url = base_url + rel_url

            driver.get(url)
            print(f"Fetching - {url}")

            driver.implicitly_wait(2)

            if check_exists(driver, By.XPATH, "//button[contains(@data-ui-id,'accept-all-cookies')]"):
                print("cooki present")
                cookies_accept = driver.find_element(By.XPATH, "//button[contains(@data-ui-id,'accept-all-cookies')]")
                cookies_accept.click()

            wait_until_knowledge_based_page_load(driver)
            create_save_pdf(driver, url, f"{space}_{page_count}")

            printable_div = driver.find_element(By.ID, "printable_document")
            new_links = printable_div.find_elements(By.XPATH, ".//div[contains(@class,'children_container page_tree_container')]//a")

            print(f"{len(new_links)} - New link extracted from {url}")

            for link_elm in new_links:
                link = link_elm.get_attribute("href")
                if link.count(base_url):
                    relative_url = link.replace(base_url,"")
                    data[space].append(relative_url)


if __name__ == "__main__":

    csv_file = "FileURLMapper.csv"
    BASE_URL = "https://kb.uconn.edu"
    BASE_FOLDER = "Data\\"
    data_to_scrape = {
        "Parking": ["/space/PAR/10894836117"]
    }
    completed_links_file = []

    web_driver = webdriver.Chrome()
    web_driver.maximize_window()

    scrapper(web_driver, BASE_URL, data_to_scrape)
    write_into_csv(completed_links_file, csv_file)


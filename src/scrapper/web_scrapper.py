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
    driver.execute_script(
        "document.getElementsByTagName('footer')[0].scrollIntoView({behavior: 'smooth', block: 'center'})")


def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", element)


def scroll_to_img_wait_until_load(driver, img_element, timeout=10):
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
        lambda d: d.execute_script(
            r"return Array.from(document.getElementsByClassName('ext_loading')).every((e)=> e.style.display == 'none')"))


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
    already_visited_url.add(url)


def scrapper(driver, base_url):
    for space in data_to_scrape:

        if space not in visited_space_next_file_number:
            visited_space_next_file_number[space] = 0

        while len(data_to_scrape[space]) > 0:
            rel_url = data_to_scrape[space].pop()
            url = base_url + rel_url

            try:
                visited_space_next_file_number[space] += 1

                driver.get(url)
                print(f"Fetching - {url}")

                driver.implicitly_wait(2)

                if check_exists(driver, By.XPATH, "//button[contains(@data-ui-id,'accept-all-cookies')]"):
                    cookies_accept = driver.find_element(
                                            By.XPATH,
                                            "//button[contains(@data-ui-id,'accept-all-cookies')]"
                                            )
                    cookies_accept.click()

                wait_until_knowledge_based_page_load(driver)

                if url in already_visited_url:
                    print(f"Skipping Download Already visited URL - {url}")
                    visited_space_next_file_number[space] -= 1
                else:
                    create_save_pdf(driver, url, f"{space}_{visited_space_next_file_number[space]}")

                printable_div = driver.find_element(By.ID, "printable_document")
                new_links = printable_div.find_elements(
                                            By.XPATH,
                                            ".//div[contains(@class,'children_container page_tree_container')]//a"
                                            )

                print(f"{len(new_links)} - New link extracted from {url}")

                for link_elm in new_links:
                    link = link_elm.get_attribute("href")

                    if link.count(base_url) and link not in already_visited_url:
                        relative_url = link.replace(base_url, "")

                        if relative_url not in data_to_scrape[space]:
                            data_to_scrape[space].append(relative_url)

            except NoSuchElementException:
                print(f"NoSuchElementException for {url}")
                visited_space_next_file_number[space] -= 1


if __name__ == "__main__":
    csv_file = "FileURLMapper.csv"
    BASE_URL = "https://kb.uconn.edu"
    BASE_FOLDER = "Data\\"

    # Below dict is in format "Space": "Home URL for Space"
    data_to_scrape = {
        "StudentAdmin": ["/space/SAS/10758194553"],
        "Parking": ["/space/PAR/10894836117"],
        "HuskyCT": ["/space/TL/10726900389"],
        "HuskyCT-Ultra": ["/space/TL/26040828048", "/space/TL/26211713033", "/space/TL/26054328575",
                          "/space/TL/26043285770", "/space/TL/26043090046", "/space/TL/26044268884",
                          "/space/TL/26043678882", "/space/TL/26046857479", "/space/TL/26044432789",
                          "/space/TL/26045939985", "/space/TL/27366326319", "/space/TL/26054394050",
                          "/space/TL/26052199835", "/space/TL/26053706428", "/space/TL/26056720610",
                          "/space/TL/26546896910", "/space/TL/26724991067", "/space/TL/26844168198",
                          "/space/TL/27107983406"],
        "IT_Guides": ["/space/IKB/10769924612", "/space/IKB/10784508250", "/space/IKB/26279051510",
                      "/space/IKB/26016516022", "/space/IKB/26302447699", "/space/IKB/26302054492",
                      "/space/IKB/26303627270"],
        "IT-NetId": ["/space/IKB/10724476730", "/space/IKB/10744071296", "/space/IKB/10728767960"],
        "IT-Printing": ["/space/IKB/10899849280", "/space/IKB/26996441110", "/space/IKB/26928676873"],
        "IT-Network": ["/space/IKB/10724476737"],
        "IT-Support": ["/space/IKB/10759275649", "/space/IKB/26327319630", "/space/IKB/10914103701",
                       "/space/IKB/26055606857", "/space/IKB/27175059526", "/space/IKB/10845093938"],
        "IT-Devices": ["/space/IKB/10852500909"],
        "IT-Microsoft": ["/space/IKB/10770819474"]
    }

    already_visited_url = set()
    visited_space_next_file_number = {}

    if os.path.exists(csv_file):
        print("Found Existing file to URL mapper file")
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                space, number = row["file"].split('_')

                if space not in visited_space_next_file_number:
                    visited_space_next_file_number[space] = int(number)
                if visited_space_next_file_number.get(space) < int(number):
                    visited_space_next_file_number[space] = int(number)

                already_visited_url.add(row["URL"])
        print(visited_space_next_file_number)

    if os.path.exists("UnFetchedURL.csv"):
        print("Found Existing UnFetched URL file")
        with open('UnFetchedURL.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                space = row["space"]
                if space not in data_to_scrape:
                    data_to_scrape[space] = []
                data_to_scrape[space].append(row["URL"])

    completed_links_file = []

    web_driver = webdriver.Chrome()
    web_driver.maximize_window()

    try:
        scrapper(web_driver, BASE_URL)
    except Exception as e:
        print(e)
        unfetched_url = []

        for key in data_to_scrape:
            for u in data_to_scrape[key]:
                unfetched_url.append({"space": key, "URL": u})

        with open("UnFetchedURL.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["space", "URL"])
            writer.writeheader()
            writer.writerows(unfetched_url)
        print("Write unfetched URL to UnFetchedURL.csv.")

    write_into_csv(completed_links_file, csv_file)

    print("SUMMARY OF DOWNLOADED FILE")
    print(f"Total Download - {len(completed_links_file)}")

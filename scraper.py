import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chinese_converter
import re
import cProfile

regex_pc = r'^https://www.manhuagui.com/comic/'
regex_mobile = r'https://m.manhuagui.com/comic/'
regex_gen = r'https://'

NAME = 0
URL = 1

#future extension: search - with dict, where name is key and val is link
#TODO: 
# -add help to each command, 
# -add description to each function

def __runSoup(href):
    response = requests.get(href)

    attr_status = SoupStrainer(class_="status")

    soup = BeautifulSoup(response.content, 'html.parser', parse_only=attr_status)

    #status = soup.find('li', class_="status")
    return(soup.text)

#slightly faster
def __runLxml(href : str):
    """
    Slightly faster than beautifulSoup, scraping details using lxml and xpath.

    Parameter
    ---
    href : string
        The URL/href of target webpage.
    
    Return
    ---
    final_string : string
        A string of current status/detail of target work.
    """
    response = requests.get(href)
    tree = html.fromstring(response.content)

    status = tree.xpath('//li[@class="status"]/span/child::*/text()')

    final_string = ""
    for i in status:
        final_string += i
        final_string += " "
    
    return final_string

def __get_work_title(response_str : str):
    """
    Get the title of a work after GET request is completed.
    
    Parameter
    ---
    response_str : page source of html
        Page source of target work's webpage.

    Return
    ---
    title : string
        Title of target work.
    """
    tree = html.fromstring(response_str)
    title = tree.xpath('//div[@class="book-title"]/h1/text()')
    return chinese_converter.to_simplified(title[0])





def __add_to_scrape_list(f, title, new_URL):
    f.write(f'\n{title}|||{new_URL}')

"""def get_scrape_list():
    with open("list.txt", "r", encoding="utf-8") as f:
        lst = f.read().strip().splitlines()
        for i in lst:
            work = i.split(sep="|||")
            scrape_list_dict[work[0]] = work[1]
        f.close()"""

def __get_scrape_list(type : str = "dict"):
    """
    Returns all added works stored in list.txt.

    Parameter
    ---
    type : str, default = "dict"
        Entails the type of return required.
    
    Returns
    ---
    type = "all" : dictionary 
        {"title":"URL"}, URLs and titles of all works added, where each URL corresponds to each title.
    type = "name" : set-like object
        Titles of all works added.
    type = "URL" : set-like object
        URLs of all works added.
    """
    work_dict = {}
    with open("list.txt", "r", encoding="utf-8") as f:
        lst = f.read().strip().splitlines()
        for i in lst:
            work = i.split(sep="|||")
            work_dict[work[0]] = work[1]
    f.close()
    match type:
        case "name":
            return work_dict.keys()
        case "URL":
            return work_dict.values()
        case "dict":
            return work_dict
        
def __is_name_or_URL(name_or_URL):
    name_or_URL = name_or_URL.strip()
    if re.match(regex_gen, name_or_URL):
        return URL
    else:
        return NAME

def __return_full_work_name(work_name_list, name_substring) -> str:
    for name in work_name_list:
        if name_substring in name:
            return name
    return None

def __get_work_URL(work_dict, name_substring) -> str:
    work_name = __return_full_work_name(work_name_list=work_dict.keys(), name_substring=name_substring)
    if work_name:
        return work_dict[work_name]
    else:
        return None

def __is_URL_in_scrape_list(work_URL_list, url):
    for u in work_URL_list:
        if url == u:
            return True
    return False
        


def __add_name_to_scrape_list(new_name_substring):
    scrape_list = __get_scrape_list()
    if __return_full_work_name(scrape_list.keys(), new_name_substring):
        return "work already added."
    
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    utf8encoded = new_name_substring.encode("utf-8").hex("%")
    url = f"https://www.manhuagui.com/s/%{utf8encoded}.html"
    driver.get(url)
    try:
        driver.find_element(By.XPATH, '//a[@class="bcover"]').click()
        work_URL = driver.current_url
        work_name = __get_work_title(driver.page_source)
    except:
        return "no works found. work not added."

    if __is_URL_in_scrape_list(scrape_list.values(), work_URL):
        return "work already added."

    with open("list.txt", "a", encoding="utf-8") as f:
        __add_to_scrape_list(f, work_name, work_URL)
    return "added " + work_name

def __add_URL_to_scrape_list(new_URL):
    new_URL = new_URL.strip()

    if re.match(regex_mobile, new_URL):
        new_URL = new_URL.replace("https://m.manhuagui.com/comic/", "https://www.manhuagui.com/comic/")

    hrefs = __get_scrape_list(type="URL")
    if new_URL in hrefs:
        return "work already added."

    with open("list.txt", "a", encoding="utf-8") as f:
        
        if re.match(regex_pc, new_URL): # check if has correct format at the start of URL
            #check if work is valid
            response = requests.get(new_URL)
            if response:
                title = __get_work_title(response.content)
                __add_to_scrape_list(f, title, new_URL)
                f.close()
                return "added " + title
            else:
                return "invalid work number entered. try again"
            
        else:
            return "invalid URL entered. perhaps you missed 'https://' ?"



def scrape_n(name_or_URL : str) -> str:
    scrape_lst_dict = __get_scrape_list()
    if __is_name_or_URL(name_or_URL) == URL:
        return __runLxml(name_or_URL)
        #link database? - see notion for grid
    else:
        try:
            return __runLxml(__get_work_URL(__get_scrape_list(), name_or_URL))
        except:
            return "invlid argument entered."

def scrape_d() -> dict:
    info_dict = {}
    scrape_lst_dict = __get_scrape_list()
    try:
        for name in scrape_lst_dict:
            info_dict[name] = __runLxml(scrape_lst_dict[name])
        return info_dict
    except:
        return "no works added."
    
def add_to_scrape_list(name_or_URL):
    if __is_name_or_URL(name_or_URL) == URL:
        return __add_URL_to_scrape_list(name_or_URL)
    else:
        return __add_name_to_scrape_list(name_or_URL)

def remove_from_scrape_list(name_or_URL):
    scrape_list_dict = __get_scrape_list()
    if __is_name_or_URL(name_or_URL) == URL:
            in_list = False
            with open("list.txt", "w", encoding="utf-8") as f:
                for name in scrape_list_dict:
                    if scrape_list_dict[name] == name_or_URL:
                        in_list = True
                        continue
                    else:
                        __add_to_scrape_list(f, name, scrape_list_dict[name])
            f.close()
            if in_list == False:
                return "work not in list."
            else:
                return f"{name_or_URL} deleted successfully."
            
    else:
            in_list = False
            with open("list.txt", "w", encoding="utf-8") as f:
                for name1 in scrape_list_dict:
                    if name1.find(name_or_URL) != -1:
                        in_list = True
                        continue
                    else:
                        __add_to_scrape_list(f, name, scrape_list_dict[name])
            f.close()
            if in_list == False:
                return "work not in list."
            else:
                return f"{name_or_URL} deleted successfully."

def return_readable_scrape_list():
    msg = "added works:"
    names = __get_scrape_list("name")
    if len(names) == 0:
        return "no works added"
    for i in names:
        msg += "\n"
        msg += i
    return msg
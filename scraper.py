import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from lxml import html
import re
import cProfile

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

def __get_work_title(response : requests.Response):
    """
    Get the title of a work after GET request is completed.
    
    Parameter
    ---
    response : Response object
        Target work's webpage (returned after GET request fulfilled).

    Return
    ---
    title : string
        Title of target work.
    """
    tree = html.fromstring(response.content)
    title = tree.xpath('//div[@class="book-title"]/h1/text()')
    return title[0]





def __write_work_in_fomat(f, new_URL, title):
    f.write(f'\n{new_URL}|||{title}')

def __get_scrape_list(type : str = "dict"):
    """
    Returns all added works stored in list.txt.

    Parameter
    ---
    type : str, default = "dict"
        Entails the type of return required.
    
    Returns
    ---
    type = "dict" : dictionary 
        {"URL":"title"}, URLs and titles of all works added, where each URL corresponds to each title.
    type = "keys" : set-like object
        URLs of all works added.
    type = "values" : set-like object
        Titles of all works added.
    """
    work_dict = {}
    with open("list.txt", "r", encoding="utf-8") as f:
        lst = f.read().strip().splitlines()
        for i in lst:
            work = i.split(sep="|||")
            work_dict[work[0]] = work[1]
    f.close()
    match type:
        case "keys":
            return work_dict.keys()
        case "values":
            return work_dict.values()
        case "dict":
            return work_dict

def scrape(): #change getting list to get_list function
    info_lst = []
    with open("list.txt", "r") as f:
        href_lst = __get_scrape_list("keys")
        for href in href_lst:
            info_lst.append(__runLxml(href))
    f.close()
    return info_lst

def add_to_scrape_list(new_URL):
    new_URL = new_URL.strip()
    hrefs = __get_scrape_list(type="keys")
    if new_URL in hrefs:
        return "work already added."

    with open("list.txt", "a", encoding="utf-8") as f:
        regex = r'^https://www.manhuagui.com/comic/'
        if re.match(regex, new_URL): # check if has correct format at the start of URL
            #check if work is valid
            response = requests.get(new_URL) 
            if response:
                title = __get_work_title(response)
                __write_work_in_fomat(f, new_URL, title)
                f.close()
                return "added " + title
            else:
                return "invalid work number entered. try again"
            
        else:
            return "invalid URL entered. perhaps you missed 'https://' ?"

def remove_from_scrape_list(URL_to_del):
    URL_to_del = URL_to_del.strip()
    dic = __get_scrape_list()
    lst = dic.keys()
    if URL_to_del not in lst:
        return "work not in list."
    
    with open("list.txt", "w") as f:
        for i in lst:
            if i == URL_to_del:
                continue
            else:
                __write_work_in_fomat(f, URL_to_del, dic[URL_to_del])
        f.close()
        return "work deleted successfully."

def return_readable_scrape_list():
    msg = "added works:"
    lst = __get_scrape_list(type="values")
    if len(lst) == 0:
        return "no works added"
    for i in lst:
        msg += "\n"
        msg += i
    return msg



def __test(inp):
    with open("list.txt", "r") as f:
        print(f.read().find())

        if inp in f.read():
            print("yes")
        else:
            print("no")
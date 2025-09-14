import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from lxml import html
import chinese_converter
import re
import cProfile

regex_pc = r'^https://www.manhuagui.com/comic/'
regex_mobile = r'https://m.manhuagui.com/comic/'
regex_gen = r'https://'

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
        case "all":
            return work_dict

def __is_in_scrape_list(work_name_list, name_substring) -> str:
    for name in work_name_list:
        if name_substring in name:
            return name
        else:
            return None

"""def __get_work_URL(work_dict, name_substring) -> str:
    work_name = __is_in_scrape_list(work_name_list=work_dict.values(), name_substring=name_substring)
    if work_name:
        return work_dict[work_name]
    else:
        return None"""




def scrape(): #change getting list to get_list function
    info_lst = []
    href_lst = __get_scrape_list(type="URL")
    for href in href_lst:
        info_lst.append(__runLxml(href))
    return info_lst

def add_to_scrape_list(new_URL):
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
                title = __get_work_title(response)
                __add_to_scrape_list(f, title, new_URL)
                f.close()
                return "added " + title
            else:
                return "invalid work number entered. try again"
            
        else:
            return "invalid URL entered. perhaps you missed 'https://' ?"

def remove_from_scrape_list(name_or_URL):
    name_or_URL = name_or_URL.strip()
    scrape_list_dict = __get_scrape_list(type="all")
    match name_or_URL:
        case re.match(regex_gen, name_or_URL):
            URLs = scrape_list_dict.values()
            if name_or_URL in URLs:
                with open("list.txt", "w") as f:
                    for name in scrape_list_dict:
                        if scrape_list_dict[name] == name_or_URL:
                            continue
                        else:
                            __add_to_scrape_list(f, name, scrape_list_dict[name])
                    f.close()
                    return f"{name_or_URL} deleted successfully."
            else:
                return "work not in list."
        case _:
            if name in scrape_list_dict:
                with open("list.txt", "w") as f:
                    for name1 in scrape_list_dict:
                        if name1 == name:
                            continue
                        else:
                            __add_to_scrape_list(f, name, scrape_list_dict[name])
                    f.close()
                    return f"{name_or_URL} deleted successfully."
            else:
                return "work not in list."

def return_readable_scrape_list():
    msg = "added works:"
    names = __get_scrape_list("name")
    if len(names) == 0:
        return "no works added"
    for i in names:
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
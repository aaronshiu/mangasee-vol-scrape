from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from urllib.parse import quote
import subprocess
import time
import re
import shutil
import os

p = print

storage = Path("D:/Mangas") # path to main root directory to store/manage files in - make sure there is enough storage in directory to DL files
driver_location = Service(Path("D:/geckodriver.exe")) # path to Firefox geckodriver executable
kcc = Path("D:/kcc/kcc-c2e.py") # path to KindleComicConverter script

mangasee_base = "https://mangasee123.com" # main URL for MangaSee
engine = "https://duckduckgo.com/?q=" # default search engine is DuckDuckGo
mangasee_dir = mangasee_base + "/directory" # MangaSee directory for all listings
storage_subdirectory = storage / "mangasee" # subdirectory that Gallery-dl generates for the specific URL
options = Options()
options.headless = True # allows headless Firefox to reduce resource use

def search(): # searches for query in all links inside the URL directory
    matched_name = []
    matched_url = []
    query = input("\nEnter the content to search for: ")
    p("\nNavigating to URL... ")
    driver.get(mangasee_dir) # go to URL directory
    time.sleep(1)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML") # execute scripts on page to modify base DOM content
    p(f"\nSearching for {query}... ")
    soup = BeautifulSoup(html, "html.parser")
    links = [a for a in soup.find_all("a", href=True)]
    for link in links:
        if (query.casefold() in link.decode_contents().casefold()) or (query.casefold() in link["href"].casefold()):
            matched_name.append(link.decode_contents())
            matched_url.append(mangasee_base + link["href"])
    n = 1
    p("\nResults:\n")
    for match in matched_name:
        p(f"{str(n)}) {match}")
        n += 1
    # default recursive searching for query, or can use choice number or allow for later input
    confirm = input(f"\nDo you see what you're looking for? (Y/N/[1-{len(matched_name)}]) [N]: ").casefold() or "n"
    if ("y" in confirm):
        choice = int(input(f"\nNumber of choice [1-{len(matched_name)}]: "))
        return choice-1, matched_name, matched_url
    elif ("n" not in confirm) and (int(confirm) in range(1, len(matched_name)+1)):
        return int(confirm)-1, matched_name, matched_url
    else:
        search()

def selection(number, matched_name, matched_url): # find all <span> tags inside choice URL, find latest chapter for % completion and specific choice details
    latest_chapter = []
    name = matched_name[number]
    url = matched_url[number]
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for s in soup.find_all("span", class_="ng-binding"):
        latest_chapter.append(list(filter(None, re.split("\t|\n", s.decode_contents()))))
    try:
        latest_chapter = int(float(latest_chapter[0][1]))
    except IndexError as e:
        latest_chapter = int(float(latest_chapter[2][1]))
    p(f"\nSelection: {name} | Total number of chapters: {latest_chapter}")
    return url, latest_chapter, name

def gallery_dl(url, total, name): # passes url to Gallery-dl and gives an interactive output to user instead of default no response
    process = subprocess.Popen(f"gallery-dl {url} -d {storage}", stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    p()
    try:
        for line in iter(process.stdout.readline, ""):
            current = int(float(line.split(b"_")[-2].strip(b"c")))
            prcnt = round(100 * (current / total), 2)
            p(f"Percentage complete: {str(prcnt)}%", end="\r")
    except IndexError as e:
        pass
    p(f"\n\nDone downloading: {name}")

def vol_search(term): # searches for, title of content + "list of chapters", to find first Wikipedia page to volume/chapter information - WIP!
    hit_name = []
    hit_url = []
    p(f"\nLooking up {term} in search engine... ")
    search_query = engine + quote(term + " list of chapters")
    driver.get(search_query)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for a in soup.find_all("a", href=True):
        info_page = a["href"]
        if "wikipedia" in info_page:
            driver.get(info_page) 
            break
    
    number_of_volumes = 0
    chapters_per_volume = []
    soup_2 = BeautifulSoup(driver.page_source, "html.parser")
    for main_table in soup_2.find_all("table", class_="wikitable"):
        for info_table in main_table.find_all("table"):
            number_of_volumes += 1
            n = 0
            for ol in info_table.find_all("ol"):
                for li in ol.find_all("li"):
                    n += 1
            chapters_per_volume.append(n)
    return chapters_per_volume

# strips folders of non-useful characters and places chapters in volumes as well as side-chapters corresponding to main chapter number
def sorter(chapter, name):
    root = storage_subdirectory / name
    p("\nCleaning up chapter names into a usable format... ")
    for folder in root.iterdir():
        c_num = float(folder.name.strip("c").lstrip("0"))
        shutil.move(folder, folder.parent / f"{c_num}")
    
    current_chapter = 0
    chapter_list = [1]
    p("\nMoving chapters into their respective volumes... ")
    for v in range(1, len(chapter)+1):
        current_chapter += chapter[v-1]
        chapter_list.append(current_chapter)
    for i in range(1, len(chapter_list)):
        current_volume = root / f"Volume {i}"
        for j in range(chapter_list[i], chapter_list[i]+1):
            p(f"\nMoving chapters related to Volume {i}... ", end="\r")
            for k in range(chapter_list[i-1], j):
                if k == 1:
                    shutil.move(root / f"{float(k)}", current_volume / f"{int(float(k))}")
                shutil.move(root / f"{float(k+1)}", current_volume / f"{int(float(k+1))}")
    
    p("\n\nSorting side chapters (if any) into their respective volumes... ")
    for f in root.iterdir():
        if "." in f.name:
            deci_name = f.name.split(".")
            if deci_name[-1] != "0":
                chapter_stem = deci_name[0]
                for s in root.glob("*/*"):
                    if s.name[0].isdigit():
                        if chapter_stem == s.name:
                            shutil.move(f, s.parent / f.name)
    p("\nDeleting residual, non-volume-sorted chapters... ")
    for g in root.iterdir():
        if g.name[0].isdigit():
            shutil.rmtree(g)

def converter(name): # archives the sorted/cleaned directory into .CBZ, and uses KCC to convert -> .epub -> .MOBI files
    p("\nArchiving directory for KindleComicConverter... ")
    shutil.make_archive(name, "zip", storage_subdirectory / name)
    shutil.move(f"{name}.zip", storage / f"{name}.cbz")
    p("\nRunning KindleComicConverter... ")
    cmd = subprocess.Popen(["python", kcc, name + ".cbz", "-m", "-u", "-s", "-b", "2", "-o", storage]) # can edit flags to change kcc options
    cmd.communicate()
    
if __name__ == "__main__": # initialise program
    os.chdir(storage) # change directory to user-defined storage location
    p("\nOpening headless Firefox temporarily... ")
    driver = webdriver.Firefox(service=driver_location, options=options) # opens Firefox with Geckodriver path and Headless option
    manga_choice, name_list, url_list = search() # user-selected content of choice, names of matching query, URLs of matching query
    url, latest, name = selection(manga_choice, name_list, url_list) # specific content DL link, latest chapter available to DL, name of content
    gallery_dl(url, latest, name)
    chapter_info = vol_search(name)
    p("\nClosing headless Firefox... ")
    driver.close()
    sorter(chapter_info, name)
    converter(name)
    os.remove(name + ".cbz") # currently broken as executes at same time as subprocess Gallery-dl
    p("\nDeleting original downloaded files... ")
    shutil.rmtree(storage_subdirectory) # delete mangasee subdirectory by default
    # uncomment below this line to only remove the specific content's folder not the whole subdirectory if there is other content within subdirectory
    #shutil.rmtree(storage_subdirectory / name)
    p("\nDone!\n")
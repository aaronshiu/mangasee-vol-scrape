# mangasee-vol-scrape
Scrapes MangaSee for content, passes URL to Gallery-dl, sorts chapters into volumes via Wikipedia table, converts to MOBI files for the Kindle.
Uses: BeautifulSoup4, Selenium as Python libraries.
*Windows-only for now*

# Why?
Sometimes you want some content displayed on the Kindle where the front-page of the volume is the cover of the volume/block of chapters and not just a random page within the range of chapters. So for the most part, this script simply scrapes MangaSee for content, downloads said content, searches for some chapter/volume information, converts to MOBI for transferring to your Kindle via Calibre or manual USB connection.

# How to use
1) Specify a download location for MangaSee content/main directory to work from i.e. "D:/Mangas". Be sure to change *line 17* to reflect this path.

2a) Download the geckodriver executable browser (Firefox-driver) from: https://github.com/mozilla/geckodriver/releases i.e. geckodriver-v0.30.0-win64.zip.
2b) Unzip the executable file to a path of your choice i.e. "D:/Documents/geckodriver.exe", and be sure to change *line 19* to reflect this path.

3a) Install Gallery-dl from: https://github.com/mikf/gallery-dl. *Tested with Chocolatey*
3b) Make sure that *gallery-dl* is a Windows PATH Environment Variable i.e. if you type *gallery-dl --help* in PowerShell, it produces "usage: gallery-dl.exe [OPTION]... URL..."

4a) Clone/download KindleComicConverter (KCC): https://github.com/ciromattia/kcc and extract the archive to a location if not already unzipped, change *line 19* to reflect the path to the *kcc-c2e.py* file.
4b) As of this commit, modify *line 258* in "kcc/kindlecomicconverter/image.py" as I came across an error when executing KCC conversion, 
      From: "self.image = ImageOps.autocontrast(Image.eval(self.image, lambda a: 255 * (a / 255.) ** gamma))"
      To: "self.image = ImageOps.autocontrast(Image.eval(self.image, lambda a: int(255 * (a / 255.) ** gamma)))"
      
    Essentially, wrapping the "255 * (a / 255.) ** gamma" lambda function in an "int()"... **https://github.com/ciromattia/kcc/issues/406**
5) Search for a particular piece of content (that is hosted on MangaSee) with a **TYPICAL WIKIPEDIA PAGE for a volume-chapter table (see issue 2)**

6) After the program takes the search query, scrapes MangaSee for the query, downloads the specified content through Gallery-dl, sorts the main chapters and side-chapters based on the Wikipedia table, archives the directory into .CBZ and converts to .MOBI through KindleComicConverter, you can transfer the .MOBI files left in the download/storage location to your Kindle, either manually or through the widely-used Calibre e-book manager: https://github.com/kovidgoyal/calibre.

(Optional: DuckDuckGo was chosen as the search engine because it is quite privacy-oriented, but you can modify *line 22* to use any other search engine of choice, i.e. Google, because... well... DuckDuckGo uses Bing... ._.)


# Known issues
1) After transferring files to the Kindle via Calibre or even manually by moving to the *documents* folder in the Kindle, if you connect to the internet the covers for the books/content disappears. From Calibre's explanation it's because Amazon automatically assumes that the files were purchased from Amazon and the Kindle will try to find the appropriate cover on their servers, but end up failing due to the custom sideloaded nature of the files and stay blank. Even with Calibre's transfer with its "PDOC/Personal Document" output format checked in the preferences, this scenario still happens (if you connect to the internet). There is a whacky work-around here: https://www.mobileread.com/forums/showthread.php?t=329945&page=2 by *Androzes*/*hengyu* on the page, that I still use. After sideloading, go to the hidden folder "system/thumbnails" in the Kindle and sort by Date Modified/Created, copy all the relevant thumbnails to the sideloaded content somewhere else. After you disconnect the Kindle and connect to the internet/sync and the covers all go blank, connect to your computer again and replace the dead thumbnails in *system/thumbnails* with the original "good" thumbnails.

2) Due to the nature of the script where it searches online for "<Name of content> + list of chapters" and takes the first Wikipedia link that shows up, less well-known content OR spin-off series that is marked on MangaSee as completely separate content, will most of the time error out as it only comes across either fandom websites OR the main series' chapter/volume information on Wikipedia. It will try to search the chapter/volume table (that might not be standard) in the Wikipedia page but come up dry, as the series you are interested in is a link on the main page as a spin-off and not a separate series with its own table of information.
An example of something that's been tested to work would be:
  - Query: "boruto",
  - Input "1" as the first scraped choice for "Boruto - Naruto Next Generations",
  - Downloads content,
  - Searches for "Boruto - Naruto Next Generations list of chapters" on DuckDuckGo,
  - Goes to "https://en.wikipedia.org/wiki/List_of_Boruto:_Naruto_Next_Generations_chapters"
  - Takes note of the latest Volume in Tankōbon Format as being Volume 15 with the last chapter of the volume being Chapter 59 **as of 08/12/2021** and sorts chapters into volumes,
  - Converts to a Kindle Paperwhite 3/4 optimised MOBI format and deletes original files.

An example of something that does not work would be:
  - Query: "need is kill",
  - Input "1" as the first scraped choice for "All You Need Is Kill",
  - Downloads content, 
  - Searches for "All You Need Is Kill list of chapters" on DuckDuckGo,
  - Goes to "https://en.wikipedia.org/wiki/All_You_Need_Is_Kill"
  - Program fails as there is an absence of a chapter/volume table with the standard format.

There is currently no way around this, so if you would like to keep the original files after scraping on MangaSee and perform no other operations, comment out *lines 164-171*

3) If the MangaSee URL goes down or they some how change the folder/content structure of their website, please either let me know OR modify *lines 21 and 23* accordingly.

This script is probably riddled with bugs and unprofessionalism but hey, it somewhat works xD
SMTPlib was attempted to allow for wireless transfer functionality, but unless you have your own email exchange server (I doubt many do, including myself), most email providers allow a paltry file size for emailing content for the Send-To-Kindle service (even zipped), i.e. 20 MB. Compression was also tried, but if you had to compress some 70 MB+ files down to 20 MB recursively, I would think most lossy-lossy JPEG->JPEG conversions would look tacky at best.
If wiki/fandom sites are more standardised there might be merit in using them for volume/chapter information instead of Wikipedia, but at the end of the day all these websites are all fan-made so there is no standard table with some simple HTML list tag type of chapter information in a neat little organised manner that I can pull from that includes all mainstream and non-mainstream content.

Have a good day! :)

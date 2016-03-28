from bs4 import BeautifulSoup
import requests
from item import Textbook
import webbrowser

def main():
    outfile = ("asdfasdfasdf.txt","w")
    #initializes empty list to store textbook objects
    TEXTBOOKLIST = []
    #prompts user for textbook
    query = input("enter textbook name: ")
    yesPCC = input("would you like to search pcc bookstore? (y/n): ")
    if yesPCC == 'y':   
        #prompts user for department
        department = input("enter department: ")
        #prompts user for course
        course = input("enter class: ")
        #prompts user for crn
        crn = input("enter crn: ")
        PCCbookstoreScrape(TEXTBOOKLIST,department, course, crn)
    print("-----------------------------------------------------------------")

    
    #call function amazon scrape using user query and TEXTBOOKLIST
    amazonScrape(query, TEXTBOOKLIST)

    ebayScrape(query, TEXTBOOKLIST)
    insertionSort(TEXTBOOKLIST)
    #prints items in textbooklist
    for i in range(len(TEXTBOOKLIST)):
        print(str(i+1)+")")
        print(TEXTBOOKLIST[i])
        print("-----------------------------------------------------------------")

    #goes to listing source webpage
    goToSource = input("enter number: ")
    goToSource = int(goToSource)
    webbrowser.open(TEXTBOOKLIST[goToSource-1]._source)

##creates url for first result of initial amazon search
def amazonScrape(searchQuery, objectList):
    #separate words in user input to form url string
    words = searchQuery.split()
    #initialize url string
    url = "http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
    #adds to url string to generate url search query
    for i in range(len(words)):
        url += words[i]
        if words[i] != words[-1]:
            url += "+"

    #obtains html file
    r = requests.get(url)
    soup = BeautifulSoup(r.content)

    #searches for the first result
    firstResult = soup.find("li", {"id":"result_0"})

    #find all links and the name
    links = firstResult.find_all("a")
    name = firstResult.find("h2",{"class":"a-size-medium a-color-null s-inline s-access-title a-text-normal"})

    #obtain the isbn by examining the first link and locating the last 10 digits
    textbookISBN = links[0].get("href")[-10:]

    #generate url for used and new listings
    used = "http://www.amazon.com/gp/offer-listing/"+textbookISBN+"/ref=dp_olp_used?ie=UTF8&condition=used"
    new = "http://www.amazon.com/gp/offer-listing/"+textbookISBN+"/ref=dp_olp_used?ie=UTF8&condition=new"

    #scrape first 2 results of each page
    amazonPageScrape(used, objectList, name.text)
    amazonPageScrape(new, objectList, name.text)


##builds url and information for textbooks off first result from amazonScrape
def amazonPageScrape(url, objectList, title):


    #get html file
    r = requests.get(url)
    soup = BeautifulSoup(r.content)

    #find the price listings
    listings = soup.find_all("span",{"class":"a-size-large a-color-price olpOfferPrice a-text-bold"})


    #shipping = soup.find_all("span",{"class":"olpShippingPrice"})


    #condition is determined by the last word of the url
    condition = url.split("=")[-1]
    #attached to title for user clarity
    title += "("+condition+")"

    #used to retrieve information if the website is using anti crawl or some html differs for each page access
    while not listings:
            r = requests.get(url)
            soup = BeautifulSoup(r.content)
            listings = soup.find_all("span",{"class":"a-size-large a-color-price olpOfferPrice a-text-bold"})
            #shipping = soup.find_all("span",{"class":"olpShippingPrice"})

    #append to list of objects for each textbook with price, and name
    for i in range(0,2):
        objectList.append(Textbook(title,listings[i].text.strip(),url,"amazon"))


    #print(listings[0]+shipping[0]+"="+str(int(listings[0][1:])+int(shipping[0][1:])))

##used for sorting textbook object list
def insertionSort(objectList):
    for i in range(1, len(objectList)):
        next = objectList[i]

        j = i
        while j >0 and objectList[j-1] > next:
            objectList[j] = objectList[j-1]
            j -= 1

        objectList[j] = next

##builds url and information for textbooks off ebay listings
def ebayScrape(searchQuery, objectList):
    words = searchQuery.split()
    #stores all prices
    priceList = []
    #stores all titles
    titleList = []
    #stores all sources
    sourceList = []
    url = "http://search.ebay.com/"

    for i in range(len(words)):
        url += words[i]
        if words[i] != words[-1]:
            url += "+"

    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    #identifies all listings
    listings = soup.find("div",{"class":"rsw"})
    #finds book titles from listings
    titles = listings.find_all("a",{"class":"vip"})
    #finds prices from listings
    prices = listings.find_all("li",{"class":"sresult lvresult clearfix li"})
    #finds sources from listings
    sources = listings.find_all("a")

    #will store first 5 results
    for i in range(0,6):
        setPrice = prices[i].find("span",{"class":"bold"})
        priceList.append(setPrice.text.strip())
        titleList.append(titles[i].text)
        sourceList.append(sources[i].get("href"))

    for i in range(len(titleList)):
        objectList.append(Textbook(titleList[i],priceList[i],sourceList[i],"ebay"))
        
## scrapes pcc bookstore
# @param department subject department(ex. CS)
# @param course class (ex. 3C)
# @param crn crn number
def PCCbookstoreScrape(objectList, department, course, crn):
    department = department.upper()
    url = "http://bookstore.pasadena.edu/ePOS?term=Summer%20201&store=454&step=2&listtype=begin&form=shared3%2ftextbooks%2fno_jscript%2fmain%2ehtml&design=454&campus=Main"
    #gets html
    r = requests.get(url)
    soup = BeautifulSoup(r.content)

    #dictionary for storing department and class
    #for ex. CS is stored as MA-CS because it is part of the math department.
    #most students will know CS but not the abbreviation for the department.
    #this creates a dictionary where the class is the key and the department is the value by scraping the form itself
    departmentDictionary = {}
    options = soup.find_all("select",{"name":"department"})
    parsedList = []

    for option in options:
        parsedList = option.text.split()
       
   #ex. MA-CS-MA is stored as value for key CS
    for i in range(2,len(parsedList)):

        departmentDictionary[parsedList[i][3:]] = parsedList[i][:2]


    #department is formed using the dictionary key and values
    newDepartment = departmentDictionary[department] + "-" + department
    #generates url given these 3 parameters
    url = "http://bookstore.pasadena.edu/ePOS?wpd=1&width=100%25&vlink=%23660000&this_category=1&text=black&term=Summer+201&store=454&step=5&qty=1000&listtype=begin&link=%23000066&host=198.188.4.4&go=Go&form=shared3%2Ftextbooks%2Fno_jscript%2Fmain.html&design=454&department="+newDepartment+"&course="+course+"&colspan=3&cellspacing=1&cellpadding=0&campus=Main&border=0&bgcolor=%23cccccc&alink=%23660000&agent=Mozilla%2F5.0+%28Windows+NT+6.1%3B+WOW64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F41.0.2272.118+Safari%2F537.36&action=list_courses&section="+crn+"&Go=Go"



    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    #scrapes site for price of used, new and finds the book title
    priceNew = soup.find("span",{"id":"price__0"})
    priceUsed = soup.find("span",{"id":"price__1"})
    title = soup.find("span",{"class":"booktitle"})

    #appends to the textbook object list-entry for used and entry for new book
    objectList.append(Textbook(title.text,"$"+priceNew.text,url, "PCC bookstore"))
    objectList.append(Textbook(title.text,"$"+priceUsed.text, url, "PCC bookstore"))
    
main()
    

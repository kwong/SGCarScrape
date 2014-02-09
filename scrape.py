from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime as dt
import time


import re
#testing 1

scrape_url="http://www.sgcarmart.com/used_cars/listing.php?RPG=100&CTS[]=18&VTS[]=13&VTS[]=12&VTS[]=11&VTS[]=8&PR2=40&PR1=20&FR=2007&TO=2014"


#"http://www.sgcarmart.com/used_cars/listing.php?MOD=Car+Make+%2F+Model&ASL=1&PR1=30&PR2=40&FR=2007&TO=2014&TRN=&ENG=&VTS[]=13&VTS[]=12&VTS[]=11&VTS[]=8&FUE=&MIL_C=&OMV_C=&COE_C=&OWN_C=&CTS[]=18&DL=&LOC=&AVL=2"

#"http://www.sgcarmart.com/used_cars/listing.php?MOD=&PR1=30&PR2=40&FR=2007&TO=2014&TRN=&ENG=&FUE=&MIL_C=&OMV_C=&COE_C=&OWN_C=&VTS[]=13&VTS[]=12&VTS[]=11&VTS[]=8&CTS[]=18&DL=&LOC=&AVL=&ASL=1"

base_url = "http://www.sgcarmart.com/used_cars/"

def get_veh_links(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")

    #veh_content = soup.find(id='contentblan===))
    contentblank =  soup.find(id="contentblank")
    links = [base_url + strong.a["href"] for strong in contentblank.findAll("strong") if strong.a is not None]
    links.pop()
    return links
    
def get_veh_details(url):
    print url
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    divbox = soup.find(id="contentblank").find("div", "box")
    car_info = divbox.findAll("td")
    #  print car_info
    i = 0
    res={'price' :None, 'roadtax' :None , 'coe': None, 'omv':None, 'date':None, 'engine':None, 'url':url}

    if re.search("[\S]+ - [\S]+", car_info[1].text):
        return None

    res['price'] = ''.join([x for x in car_info[1].text if x.isdigit()])
    res['roadtax'] = ''.join([x for x in car_info[3].text if x.isdigit()])
    res['coe'] = ''.join([x for x in car_info[30].text if x.isdigit()])
    res['omv'] = ''.join([x for x in car_info[33].text if x.isdigit()])
    if not car_info[15].text == '':
        res['date'] = dt.strptime(car_info[15].text, "%d-%b-%Y")

    res['engine'] = ''.join([x for x in car_info[9].text if x.isdigit()])
    print res
    return res
    
#http://stackoverflow.com/questions/6451655/python-how-to-convert-datetime-dates-to-decimal-years
def toYearFraction(date):
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction


    
def cal_annual_cost(car):
#    print car
    if car is None:
        return
    if car['roadtax'] == '':
        return
#    print "enginesize is", car['engine']
 #   roadtax = float(car['engine'])*0.625
    roadtax = car['roadtax']
 #   print "omv ", car['omv']
    if car['omv'] == '':
        return
    arf = 1.1 * float(car['omv'])
    parf_rebate = arf / 2
    total_dep = float(car['price']) - parf_rebate
    if car['date'] == '':
        return

    years_owned = float(10 - (toYearFraction(dt.now())- toYearFraction(car['date'])))
    
#    print "years ", years_owned
    annual_dep = float(car['roadtax']) + (total_dep / years_owned)
    if annual_dep < 8300:
        print "ADEP=", annual_dep, "YO=", years_owned, "url = ", car['url']
    return annual_dep
    

veh_links = get_veh_links(scrape_url)
res = [get_veh_details(veh_link) for veh_link in veh_links]
for x in res:
   print  cal_annual_cost(x);



#print veh_links



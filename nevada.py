import sys
import mechanize
import re
import json
import time
import urllib
import urllib2
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?NV.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

voter_state = "NV"
source = "State"


result = [("authory_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

file_path = cdir + "nevada-clerks.html"
url = "http://nvsos.gov/index.aspx?page=81"
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2'
headers = {'User-Agent' : user_agent}

req = urllib2.Request(url, headers=headers)
data = urllib2.urlopen(req).read()

output = open(file_path,"w")
output.write(data)
output.close()


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


data = open(file_path).read()
data = data.replace("</a><br><br><strong>","</a><br></a><br><strong>") #to fix one bit of nonstandard code to make later parsing easier.
data = data.replace("&#46;&#117;&#115;</a></p>","&#46;&#117;&#115;</a></p></a>") #to fix one bit of nonstandard code to make later parsing easier.
data = data.replace("<br></strong>","</strong><br>") #to fix one bit of nonstandard code to make later parsing easier.
data = data.replace(", Nevada",", NV")
data = data.replace("&nbsp;","")
h = HTMLParser.HTMLParser()

county_data_re = re.compile("<strong>.+?</a>.+?</a>", re.DOTALL)
county_name_re = re.compile("<strong>(.+? C[OUNI]*TY).*?:")
email_re = re.compile("mailto:(.+?)\"")
name_re = re.compile("<br>(.+?)<br>")
middle_re = re.compile("[A-Z]\.* ")
website_re = re.compile("href=\"(h.+?)\"")

phone_re = re.compile("(\(\d{3}\).+?) F")
fax_re = re.compile("FAX(.+?)<")
area_re = re.compile("\d{3}")

address_re = re.compile("\n.+?<br>([^<>]*?\d.+?[A-Z]{2,2} \d{5}[\d-]*)")
csz_re = re.compile(">([^>,\n]+?, [A-Z]{2} *\d{5}[\d-]*)")
city_re = re.compile("(.+?), [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(P[\. ]*O\.* [BD][or].+?)<", re.DOTALL)
office_name_re = re.compile(">[A-Za-z \.\"]+?, ([A-Za-z\. ]+?) *?<")


#In several counties, it lists a separate mailing address in its own county-like entry.
#So we cycle through the data, and if we find a county that looks like that, add it to the prior county and remove it from the list.

county_names = []


county_data = county_data_re.findall(data)


for i in range(0,len(county_data)):
    try:
        county_data[i] = "\n" + county_data[i]
        county = county_data[i]
    except:
        continue
    county_name = county_name_re.findall(county)[0].title().replace("County","").strip()
    county_names.append(county_name)
    try:
        if county_name.upper() in county_data[i+1]:
            print county_data[i+1]
            county_data[i] = county + "\n" + county_data.pop(i+1)
            print county
    except:
        continue
    


for county in county_data:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)


    print reg_po_state

    county_name = county_names[county_data.index(county)]

    print "___________________________________"
    print county
    print "+++++++++++++++++++++++++++++++++++"

    name = name_re.findall(county)[0].strip()
    first_name, last_name, authority_name, review = dogcatcher.make_name(name, ", ", review)


    email = h.unescape(dogcatcher.find_emails(email_re, county))
    website = dogcatcher.website_find(website_re, county)
    phone = dogcatcher.phone_find(phone_re, county)
    fax = dogcatcher.phone_find(fax_re, county, area_re.findall(phone)[0]) #The fax #s don't come with area codes.


    #We know that there are either one or two address-shaped things in any given county.
    #So we first find all of the addresses, and then proceed based on whether there's one or two.

    addresses = address_re.findall(county)
    if len(addresses)==1:

        #This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
        #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
        #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

        address = addresses[0]
        csz = csz_re.findall(address)[0]

        try:
            po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n")
        except:
            po_street = ""

        street = address.replace(po_street,"").replace(csz,"").replace("<br>",", ")
        street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" \n/,")

        if po_street:
            po_city = city_re.findall(csz)[0].strip()
            po_state = state_re.findall(csz)[0].strip()
            po_zip_code = zip_re.findall(csz)[0].strip()
        if street:
            city = city_re.findall(csz)[0].strip()
            address_state = state_re.findall(csz)[0].strip()
            zip_code = zip_re.findall(csz)[0].strip()

    elif len(addresses)==2:

        #This section recognizes that there are going to be exactly two addresses, the second of which will always be a mailing address.
        #It cleans them sequentially.

        address = addresses[0]
        csz = csz_re.findall(address)[0]
        street = address.replace(csz,"").replace("<br>",", ")
        city = city_re.findall(csz)[0]
        address_state = state_re.findall(csz)[0]
        zip_code = zip_re.findall(csz)[0]

        street = street.replace("\n",", ").replace("\r","").replace(" ,",",").strip(" \n/,")

        address = addresses[1]
        csz = csz_re.findall(address)[0]

        try:
            po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n")
        except:
            po_street = ""

        po_city = city_re.findall(csz)[0].strip()
        po_state = state_re.findall(csz)[0].strip()
        po_zip_code = zip_re.findall(csz)[0].strip()

    else:
        print "There are neither 1 nor 2 addresses. Something is wrong with this county--figure out what it is. Good luck, soldier."
        sys.exit()

    fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)

    result.append([authority_name, first_name, last_name, county_name, fips,
        street, city, address_state, zip_code,
        po_street, po_city, po_state, po_zip_code,
        reg_authority_name, reg_first, reg_last,
        reg_street, reg_city, reg_state, reg_zip_code,
        reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
        reg_phone, reg_fax, reg_email, reg_website, reg_hours,
        phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "nevada.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()
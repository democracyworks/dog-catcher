# -*- coding: latin-1 -*-

import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os
import urllib2

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"


#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

voter_state = "VA"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


file_path = cdir + "virginia-clerks.pdf"
url = "http://www.nngov.com/voter-registrar/downloads/absentee.pdf"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req = urllib2.Request(url, "", headers)
pdf = urllib2.urlopen(req).read()

data = dogcatcher.pdf_to_text(pdf)
output = open(file_path, "w")
output.write(data)
output.close()

data = open(file_path).read()

first_part_re = re.compile("(.+?)\nAccomack",re.DOTALL)

county_re = re.compile("\n[^\n]+? C.+?· \d{4}",re.DOTALL)
county_name_re = re.compile(".+? C.+")

phone_re = re.compile("\(\d{3}\) \d{3} · \d{4}")

address_re = re.compile("  .+?\n.+?\d{5}[\d-]* *\n", re.DOTALL)
csz_re = re.compile(" *([^,\n]+?, [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")

data = data.replace(first_part_re.findall(data)[0],"")

county_data = county_re.findall(data)

for county in county_data:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    authority_name = "Voter Registration Office"

    county_name = county_name_re.findall(county)[0].replace(" County","").replace("Appomatox","Appomattox").replace("&","and").replace("Lunenberg","Lunenburg").strip()

    phone = dogcatcher.phone_find(phone_re, county)


    #There is only one address; it either does or does not contain a PO Box. We identify whether it does, and then find the city, state, and zip code as appropriate.

    address = address_re.findall(county)[0]

    csz = csz_re.findall(address)[0]

    if "PO Box" in address:
        po_city = city_re.findall(csz)[0].strip()
        po_state = state_re.findall(csz)[0].strip()
        po_zip_code = zip_re.findall(csz)[0].strip()
        po_street = address.replace(po_city,"").replace(po_state,"").replace(po_zip_code,"").strip(" \n,").replace("\n",", ")
    else:
        city = city_re.findall(csz)[0].strip()
        address_state = state_re.findall(csz)[0].strip()
        zip_code = zip_re.findall(csz)[0].strip()
        street = address.replace(city,"").replace(address_state,"").replace(zip_code,"").strip(" \n,").replace("\n",", ")



    fips = dogcatcher.fips_find(county_name, voter_state)

    result.append([authority_name, first_name, last_name, county_name, fips,
        street, city, address_state, zip_code,
        po_street, po_city, po_state, po_zip_code,
        reg_authority_name, reg_first, reg_last,
        reg_street, reg_city, reg_state, reg_zip_code,
        reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
        reg_phone, reg_fax, reg_email, reg_website, reg_hours,
        phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open(cdir + "virginia.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()
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

voter_state = "UT"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


#There are two data sources. One (a pdf) has addresses and phone #s; the other (a website) has names and phone #s.
#We take both, nad get the phones and the names out of the website and the addresses out of the pdf.

file_path_1 = cdir + "utah-clerks-1.pdf"
file_path_2 = cdir + "utah-clerks-2.html"
url_1 = "http://elections.utah.gov/Media/Default/Documents/Voter_Forms/VoterRegistrationForm.pdf"
url_2 = "http://vote.utah.gov/county-clerk/"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req = urllib2.Request(url_1, headers=headers)
pdf = urllib2.urlopen(req).read()

data = dogcatcher.pdf_to_text(pdf)
output = open(file_path_1, "w")
output.write(data)
output.close()

data = urllib.urlopen(url_2).read()
output = open(file_path_2, "w")
output.write(data)
output.close()

pdfdata = open(file_path_1).read()
htmldata = open(file_path_2).read()

county_re = re.compile("[A-Z \.]+? County Clerk.+?\d{3}-\d{4}", re.DOTALL)
county_name_re = re.compile("([A-Z \.]+?) County Clerk")

address_re = re.compile("Clerk[\s]+(.+)[\s]+\(\d{3}", re.DOTALL)

csz_re = re.compile(" *([^,\n]+?, [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("(PO Box .+)", re.DOTALL)

county_2_re = re.compile("http://vote.utah.gov/elected-officials/\"><strong>.+?\d{4}", re.DOTALL)
name_re = re.compile("<td> *(.+?) *</td>")
middle_re = re.compile("[A-Z]\.* ")

phone_re = re.compile("\(\d{3}\)-\d{3}-\d{4}")

county_data = county_re.findall(pdfdata)


htmldata = htmldata.replace("&nbsp;","-")


phone_name_data = county_2_re.findall(htmldata) #this carries the phones and names from the website in the same order as in the PDF.

for county in county_data:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    phone_name = phone_name_data[county_data.index(county)]

    official_name = name_re.findall(phone_name)[0]
    first_name, last_name, review = dogcatcher.split_name(official_name, review)

    authority_name = "County Clerk"


    phone = dogcatcher.phone_find(phone_re, phone_name)


    print "_________________________________________________"
   
    #This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

    county_name = county_name_re.findall(county)[0].title()

    address = address_re.findall(county)[0]

    csz = csz_re.findall(address)[0]

    try:
        po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n")
    except:
        po_street = ""

    print po_street
    street = address.replace(po_street,"").replace(csz,"")
    street = street.replace("\n",", ").replace(" ,",",").strip(" \n/,")

    if po_street:
        if street:
            city = city_re.findall(csz)[0]
            address_state = state_re.findall(csz)[0]
            zip_code = zip_re.findall(csz)[0]
        po_city = city_re.findall(csz)[0].strip()
        po_state = state_re.findall(csz)[0].strip()
        po_zip_code = zip_re.findall(csz)[0].strip()
    else:
        city = city_re.findall(csz)[0].strip()
        address_state = state_re.findall(csz)[0].strip()
        zip_code = zip_re.findall(csz)[0].strip()

    print po_street

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

output = open(cdir + "utah.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()
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
tmpdir = cdir + "tmp/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

voter_state = "DE"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


file_path = tmpdir + "delaware-clerks.pdf"
url = "http://elections.delaware.gov/voter/pdfs/absentee.pdf"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req = urllib2.Request(url, "", headers)
pdf = urllib2.urlopen(req).read()

data = dogcatcher.pdf_to_text(pdf)
output = open(file_path, "w")
output.write(data)
output.close()

data = open(file_path).read()


county_re = re.compile("Department of Elections for.+?Website: [^\s]+",re.DOTALL)

county_name_re = re.compile("Department of Elections for (.+) County")

phone_re = re.compile("\(\d{3}\) \d{3}-\d{4}")
website_re = re.compile("Website: (.+)")

address_re = re.compile("Department.+?\n(.+?\d{5}[\d-]*)", re.DOTALL)
csz_re = re.compile(" *([^,\n]+?, [A-Z][A-Z] *\d{5}[\d-]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("P\.O\..+")

many_space_re = re.compile("  +")

for space in many_space_re.findall(data):
    data = data.replace(space," ")

county_data = county_re.findall(data)

for county in county_data:


    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    authority_name = "Department of Elections"

    county_name = county_name_re.findall(county)[0].strip()


    phone = dogcatcher.clean_phone(phone_re.findall(county)[0])
    fax = dogcatcher.clean_phone(phone_re.findall(county)[1])
    website = dogcatcher.find_website(website_re, county)

    #This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

    address = address_re.findall(county)[0]

    csz = csz_re.findall(address)[0]

    try:
        po_street = po_re.findall(address)[0]
    except:
        po_street = ""

    street = address.replace(po_street,"").replace(csz,"").strip(" \n,").replace("\n",", ").replace(" ,",",")

    if po_street:
        po_city = city_re.findall(csz)[0]
        po_state = state_re.findall(csz)[0]
        po_zip_code = zip_re.findall(csz)[0]
    if street:
        city = city_re.findall(csz)[0]
        address_state = state_re.findall(csz)[0]
        zip_code = zip_re.findall(csz)[0]

    fips = dogcatcher.find_fips(county_name, voter_state)

    result.append([authority_name, first_name, last_name, county_name, fips,
        street, city, address_state, zip_code,
        po_street, po_city, po_state, po_zip_code,
        reg_authority_name, reg_first, reg_last,
        reg_street, reg_city, reg_state, reg_zip_code,
        reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
        reg_phone, reg_fax, reg_email, reg_website, reg_hours,
        phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.
dogcatcher.output(result, voter_state, cdir)

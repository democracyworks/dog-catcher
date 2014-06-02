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

voter_state = "MT"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


file_path = tmpdir + "montana-clerks.pdf"

file_path_1 = tmpdir + "montana-clerks-1.pdf"
url_1 = "http://sos.mt.gov/elections/forms/elections/electionadministrators.pdf"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req_1 = urllib2.Request(url_1, headers=headers)
pdf_1 = urllib2.urlopen(req_1).read()

data_1 = dogcatcher.pdf_to_text(pdf_1)
output = open(file_path_1, "w")
output.write(data_1)
output.close()

data_1 = open(file_path_1).read()
data_1 = data_1.replace("Dulcie Bear Don't Walk PO Box 908", "Dulcie Bear Don't Walk\nPO Box 908")
data_1 = data_1.replace("Golden Valley Mary Lu Berry","Golden Valley\nMary Lu Berry")
data_1 = data_1.replace("Lewis & Clark Paulette DeHart", "Lewis & Clark\nPaulette DeHart")
data_1 = data_1.replace("Powder River Karen D Amende", "Powder River\nKaren D Amende")
data_1 = data_1.replace("W i","Wi")


streets = []
counties = []
names = []
cities = []
zips = []
phones = []
emails = []

county_name_address_re = re.compile("ADDRESS\nNAME\nCOUNTY\n(.+?)\n\n", re.DOTALL)

digit_re = re.compile("\d")

county_name_address = county_name_address_re.findall(data_1)[0].split("\n")

for item in county_name_address:
    if digit_re.findall(item) or "Box" in item:
        streets.append(item)
    elif dogcatcher.find_fips(item, voter_state) != None:
        counties.append(item)
    else:
        names.append(item)

cities_re = re.compile("CITY\/STATE\/ZIP\n(.+?)\n\n", re.DOTALL)
cities_and_zips = cities_re.findall(data_1)[0].split("\n")
for item in cities_and_zips:
    city_zip = item.split("MT")
    cities.append(city_zip[0].strip())
    zips.append(city_zip[1].strip())

phones_re = re.compile("PHONE\n(.+?)\n\n", re.DOTALL)
phones = phones_re.findall(data_1)[0].split("\n")

fax_email_re = re.compile(".*\d{4}\s+(.*)")

email_re = re.compile("E-MAIL\n(.+?)\n\n", re.DOTALL)
for item in email_re.findall(data_1)[0].split("\n"):
    emails.append(fax_email_re.findall(item)[0].replace(" ", ""))

for i in range(0, len(counties)):

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    authority_name = "Election Administrator"
    county_name = counties[i].strip()
    official_name = names[i].strip()
    street = streets[i].strip()
    city = cities[i].strip()
    zip_code = zips[i].strip()
    email = emails[i].strip()
    phone = phones[i].strip()
    fax = ""

    #There is only one address, so we know that if "Box" appears in the street address, it's a mailing address.

    if "Box" in street:
        po_street = street
        street = ""
        po_city = city
        po_state = "MT"
        po_zip_code = zip_code
    else:
        city = city
        address_state = "MT"
        zip_code = zip_code


    first_name, last_name, review = dogcatcher.split_name(official_name, review, "ignore")

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

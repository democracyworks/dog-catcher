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


file_path = cdir + "montana-clerks.pdf"

#We grab two datasets. They overlap; we only use one of them for election official names and street addresses, which are much harder to pull out of the other.
#The following section grabs the pdfs and writes them to files. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path_1 = cdir + "montana-clerks-1.pdf"
file_path_2 = cdir + "montana-clerks-2.pdf"
url_1 = "http://sos.mt.gov/elections/forms/elections/electionadministrators.pdf"
url_2 = "http://sos.mt.gov/elections/Officials/Forms/Voter_Registration_Forms/Voter_Registration_Application.pdf"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req_1 = urllib2.Request(url_1, headers=headers)
pdf_1 = urllib2.urlopen(req_1).read()

data_1 = dogcatcher.pdf_to_text(pdf_1)
output = open(file_path_1, "w")
output.write(data_1)
output.close()

req_2 = urllib2.Request(url_2, headers=headers)
pdf_2 = urllib2.urlopen(req_2).read()

data_2 = dogcatcher.pdf_to_text(pdf_2)
output = open(file_path_2, "w")
output.write(data_2)
output.close()

data_1 = open(file_path_1).read()
data_2 = open(file_path_2).read()


streets = []
counties = []
names = []

csz_re = re.compile(".+? MT +\d{5}[\d-]*")
email_re = re.compile("[^\s]+@[^\s]+")
phone_pair_re = re.compile("\d{3}-\d{4}.+?\d{3}-\d{4}",re.DOTALL)
head_re = re.compile("(.+_[\s]*)County\s", re.DOTALL)
onechar_line_re = re.compile("\n.\n")
manyline_re = re.compile("\n\n+")
fix_1_re = re.compile(".+?ADDRESS", re.DOTALL)
fix_2_re = re.compile("PHONE.+?6/28/2012", re.DOTALL)

line_re = re.compile("(.+) \n")
line_2_re = re.compile("(.+?)\n")
digit_re = re.compile("\d")
text_re = re.compile("[a-zA-Z]")

data_1 = data_1.replace("W i","Wi")

#cities, states, and zip codes in dataset 1
csz_all = csz_re.findall(data_1)
for csz in csz_all:
    data_1 = data_1.replace(csz, "")
#emails in dataset 1
email_all = email_re.findall(data_1)
for email in email_all:
    data_1 = data_1.replace(email, "")
#phones and faxes in dataset 1
phone_pair_all = phone_pair_re.findall(data_1)
for pair in phone_pair_all:
    data_1 = data_1.replace(pair, "")

#data cleaning in dataset 2
for item in head_re.findall(data_2):
    data_2 = data_2.replace(item,"")
for item in csz_re.findall(data_2):
    data_2 = data_2.replace(item, "")

data_2 = data_2 + "\n"

for item in onechar_line_re.findall(data_2):
    data_2 = data_2.replace(item, "")

for item in manyline_re.findall(data_2):
    data_2 = data_2.replace(item, "\n")

data_2 = data_2.replace("County \n","")
data_2 = data_2.replace("(cid:191) ","fi")
data_2 = data_2.replace("Election Administrator Address \n","")

#Here we grab street addresses and county names from data_2.

for line in line_re.findall(data_2):
    if digit_re.findall(line) or "Box" in line:
        streets.append(line)
    else:
        counties.append(line)

data_1 = " ".join(data_1.split())

#Having found streets and county names, we remove them from data_1, and do a bit more cleaning.

for item in streets:
    data_1 = data_1.replace(item,"")

for item in counties:
    data_1 = data_1.replace(item,"",1)

for item in fix_1_re.findall(data_1):
    data_1 = data_1.replace(item, "\n")

for item in fix_2_re.findall(data_1):
    data_1 = data_1.replace(item, "\n")

data_1 = data_1.replace(" PO ","")
data_1 = data_1.replace("  ","\n")

#We then take the official names out of data_1.

for line in line_2_re.findall(data_1):
    if text_re.findall(line):
        names.append(line)

city_re = re.compile("(.+?) [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
middle_re = re.compile("[A-Z]\.* ")

for i in range(0, len(counties)):

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    county_name = counties[i].strip().replace("&","and")
    official_name = names[i].strip()
    csz = csz_all[i].strip()
    street = streets[i].strip()
    email = email_all[i].lower().strip()
    phone_pair = phone_pair_all[i].strip()

    #There is only one address, so we know that if "Box" appears in the street address, it's a mailing address.

    if "Box" in street:
        po_street = street
        street = ""
        po_city = city_re.findall(csz)[0]
        po_state = state_re.findall(csz)[0]
        po_zip_code = zip_re.findall(csz)[0]
    else:
        city = city_re.findall(csz)[0]
        address_state = state_re.findall(csz)[0]
        zip_code = zip_re.findall(csz)[0]


    first_name, last_name, review = dogcatcher.split_name(official_name, review, "ignore")

    #The phone pairs contain a phone number and a fax number. In a few cases (found by hand-checking), they're reversed.

    phone_pair = phone_pair.replace(" x","x").replace(" ","\n")
    phones = phone_pair.partition("\n")
    if (((i+1) % 5 == 0) or i in [20,21,22,53,55]) and i != 54 :
        phone = dogcatcher.clean_phone(phones[0], "406")
        fax = dogcatcher.clean_phone(phones[2], "406")
    else:
        phone = dogcatcher.clean_phone(phones[2], "406")
        fax = dogcatcher.clean_phone(phones[0], "406")

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

output = open(cdir + "montana.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()
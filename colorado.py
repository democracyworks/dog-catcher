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

voter_state = "CO"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


file_path = cdir + "colorado-clerks.pdf"
# url = "http://www.sos.state.co.us/pubs/elections/Resources/files/CountyClerkRosterWebsite.pdf"
# user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
# headers = {'User-Agent' : user_agent}

# req = urllib2.Request(url, "", headers)
# pdf = urllib2.urlopen(req).read()

# data = dogcatcher.pdf_to_text(pdf)
# output = open(file_path, "w")
# output.write(data)
# output.close()

data = open(file_path).read()


name_block_re = re.compile("[^ ]([A-Z]+[ ]*[A-Z]+[\s][\s][A-Z][a-z][^\n]+)", re.DOTALL)
address_block_re = re.compile("\n\n(\d[^@]+?\d{5}[-\d]*)\s", re.DOTALL)
phone_block_re = re.compile("\n[^\n]+?\nFax *:[^\n]+?\n[^\n]+?\n", re.DOTALL)
po_full_re = re.compile("\d{5}[-\d]*[\s]*(P\.O\. Box [^ ]+? .+?\d{5}-*\d*)", re.DOTALL)


two_digit_re = re.compile("\n\d{2}[ ]+\n", re.DOTALL)
city_re = re.compile("\n([^\d]+?),* *[A-Z]* \d{5}[-\d]*")
zip_re = re.compile("\d{5}[-\d]*")
po_re = re.compile("P.O. .+ ")


phone_re = re.compile("(\(*\d{3}\)* \d{3}-\d{4}) \nF")
fax_re = re.compile("Fax: (.+?)\n")

email_re = re.compile("[^\s]+?@[^\s]+")

two_digits = two_digit_re.findall(data)
for i in two_digits:
    data = data.replace(i,"")

data = data.replace("  "," ")

#When we clean the PDF, the data breaks down into a handful of regular patterns. These are lines that looks like
#names, lines that look like addresses or PO Boxes, and lines that looks like phones + emails.
#So we turn all of these into lists, and later put items with the same list index together.

names_block = name_block_re.findall(data)
address_block = address_block_re.findall(data)
phone_block = phone_block_re.findall(data)

if len(names_block) != len(address_block) or len(address_block) != len(phone_block) or len(names_block) != len(phone_block):
    sys.exit("There's a mismatch in the lengths of the content blocks.")


#PO Boxes are the only text blocks that don't have 1/county. So we cycle through all of the PO Box items,
#And when we find an address with a matching city, addd the PO Box to that address.

po_full = po_full_re.findall(data)

for po in po_full:
    for address in address_block:
        if city_re.findall(po)[0] == city_re.findall(address)[0]:
            address_block[address_block.index(address)] = address + "\n" + po

for county in names_block:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    index = names_block.index(county)
    county_address = address_block[index]
    county_phones = phone_block[index]

    county_split = county.partition(" \n")
    county_name = county_split[0].title()
    official_name = county_split[2]

    first_name, last_name, review = dogcatcher.split_name(official_name, review, "ignore")

    authority_name = "County Clerk"
    
    address_state = voter_state

    phone = dogcatcher.phone_find(phone_re, county_phones)
    fax = dogcatcher.phone_find(fax_re, county_phones)
    email = dogcatcher.find_emails(email_re, county_phones)

    #First we find the city, which divides the street and the CSZ + P.O. box (if the latter exists.)
    #Then we split the address at the city.
    #The street may have a spare line break in it, so we remove that.
    #Then we check for whether there's a P.O. box in the CSZ. If there is, there may also be a separate zip code.
    #If so, we remove it and check for the second zip code, which we assign to the PO box if it exists.

    city = city_re.findall(county_address)[0]

    address_split = county_address.partition(city)

    street = " ".join(address_split[0].split(" \n"))
    csz = address_split[2]
    print csz
    zips = zip_re.findall(csz)
    zip_code = zips[0]
    if "P.O." in csz:
        po_street = po_re.findall(csz)[0]
        try:
            po_zip_code = zips[1]
        except:
            po_zip_code = zips[0]
        po_city = city
        po_state = address_state

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

output = open(cdir + "oklahoma.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()
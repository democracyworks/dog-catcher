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

voter_state = "AR"
source = "State"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = cdir + "arkansas-clerks.pdf"
url = "http://www.sos.arkansas.gov/elections/Documents/county_clerks_for_website.pdf"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req = urllib2.Request(url, "", headers)
pdf = urllib2.urlopen(req).read()

data = dogcatcher.pdf_to_text(pdf)
output = open(file_path, "w")
output.write(data)
output.close()

data = open(file_path).read()

county_data_re = re.compile("\n.+?[@@][^\s]+? *\n", re.DOTALL)

name_re = re.compile("\n([^\d\n\.,]+? [^\d\n\.,]+)")
county_name_re = re.compile("\n([^\n][^\n]+?)\n")
email_re = re.compile("\n([^\s]+?[@@][^\s]+?) *\n")
middle_re = re.compile("[A-Z].* ")
phone_re = re.compile("Phone: (\d{3}.+?\d{3}.+?\d{4})")
fax_re = re.compile("Fax: (\d{3}.+?\d{3}.+?\d{4})")
hyphen_re = re.compile(" \d{3}([^\s]+?)\d{3}")

address_re = re.compile("\n([^\n]*?\d[^\n]+?\n*[^\n]*? *\d{5}[\d-]*) *\n")
po_re = re.compile("(P\.O\..+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
csz_re = re.compile("[^,]+?, [A-Z][A-Z] \d{5}[\d-]*")
city_re = re.compile("(.+?),")
zip_re = re.compile("\d{5}[\d-]*")
is_street_re = re.compile("[^,\. ]")


#Here we make a number of fixes where the PDF was parsed irregularly. These were found by hand.
data = "\n" + data
data = data.replace("01 27001","")
data = "01 27001\n" + data
data = data.replace("P.O, ","P.O. ")
data = data.replace("","")
data = data.replace("Lafayette \nRegenia Morton \n3rd and Spruce St., Lewisville, AR 71845 \n\nLonoke \nDawn Porterfield \n301 North Center St, Lonoke, AR 72086 \n\nPhone: 870‐921‐4633  Fax: 870‐921‐4505 \nlafayetteclerk@arkansasclerks.com ","Lafayette \nRegenia Morton \n3rd and Spruce St., Lewisville, AR 71845 \n\nPhone: 870‐921‐4633  Fax: 870‐921‐4505 \nlafayetteclerk@arkansasclerks.com \n\nLonoke \nDawn Porterfield \n301 North Center St, Lonoke, AR 72086 ")
data = data.replace("Phone: 501‐676‐2368  Fax: 501‐676‐2423 \ncountyclerk.kburks@yahoo.com ","")
data = data.replace("\nLonoke \nDawn Porterfield \n301 North Center St, Lonoke, AR 72086","\nLonoke \nDawn Porterfield \n301 North Center St, Lonoke, AR 72086\n\nPhone: 501‐676‐2368  Fax: 501‐676‐2423 \ncountyclerk.kburks@yahoo.com ")
data = data.replace("unionclerkarkansasclerks.com","unionclerk@arkansasclerks.com")
data = data.replace("Sherry L. Bell","Sherry Bell")
data = data.replace("Phone: 870‐798‐2517  Fax: 870‐798‐2428 \nhogskinholidays@hotmail.com ","")
data = data.replace("Calhoun \nAlma Davis \nP.O. Box 1175, Hampton, AR 71744 \n\nPhone: 870‐946‐4349  Fax: 870‐946‐4399 \narcoclerkmelissa@centurytel.net ","Phone: 870‐946‐4349  Fax: 870‐946‐4399 \narcoclerkmelissa@centurytel.net \n\nCalhoun \nAlma Davis \nP.O. Box 1175, Hampton, AR 71744 \n\nPhone: 870‐798‐2517  Fax: 870‐798‐2428 \nhogskinholidays@hotmail.com ")
data = data.replace("Phone: 870‐285‐2743  Fax: 870‐285‐3900 \npikeclerk@arkansasclerks.com ","")
data = data.replace("Montgomery \nDebbie Baxter \n105 Hwy 270 East, Mount Ida, AR 71957 \n\nPike \nSandy Campbell \nP.O. Box 218, Murfreesboro, AR 71958 \n\nPhone: 870‐867‐3521  Fax: 870‐867‐2177 \nmontgomeryclerk@arkansasclerks.com ","Montgomery \nDebbie Baxter \n105 Hwy 270 East, Mount Ida, AR 71957 \n\nPhone: 870‐867‐3521  Fax: 870‐867‐2177 \nmontgomeryclerk@arkansasclerks.com \n\nPike \nSandy Campbell \nP.O. Box 218, Murfreesboro, AR 71958 \n\nPhone: 870‐285‐2743  Fax: 870‐285‐3900 \npikeclerk@arkansasclerks.com")
data = data.replace("One","1")
data = data.replace("5KRQGD +DOEURRN","")


county_data = county_data_re.findall(data)

for county in county_data:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    authority_name = "County Clerk"

    county_name = county_name_re.findall(county)[0].strip()

    try:
        #There can be are lots of things that look like a name in the data
        official_name = name_re.findall(county)[len(name_re.findall(county))-1]
        first_name, last_name, review = dogcatcher.split_name(official_name, review, "ignore")
        
        if first_name == "County":
            first_name = ""
        if last_name == "Clerk":
            last_name = ""
    except:
        first_name = ""
        last_name = ""

    email = dogcatcher.find_emails(email_re, county)
    phone = dogcatcher.find_phone(phone_re, county)
    fax = dogcatcher.find_phone(fax_re, county)

    #This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.


    address = " ".join(address_re.findall(county)[0].replace("\n","").split())
    csz = csz_re.findall(address)[0].strip()

    try:
        po_street = po_re.findall(address)[0]
    except:
        po_street = ""

    street = address.replace(csz,"").replace(po_street,"").rstrip(", ")

    if street:
        city = city_re.findall(csz)[0]
        address_state = state_re.findall(csz)[0]
        zip_code = zip_re.findall(csz)[0]
    if po_street:
        po_city = city_re.findall(csz)[0]
        po_state = state_re.findall(csz)[0]
        po_zip_code = zip_re.findall(csz)[0]



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
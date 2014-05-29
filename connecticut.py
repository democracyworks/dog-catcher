import urllib
import re
import sys
import xlrd
import pdfminer
import urllib2
import json
import time
import os
import dogcatcher
import HTMLParser


h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

voter_state = "CT"
source = "State"

result = [("authority_name", "first_name", "last_name", "town_name", "fips", "county_name",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#There are two election offices in CT; each one is in a different PDF. The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)


file_path_1 = tmpdir + "connecticut-clerks-1.pdf"
file_path_2 = tmpdir + "connecticut-clerks-2.pdf"
url_1 = "http://www.ct.gov/sots/LIB/sots/ElectionServices/lists/TownClerkList.pdf"
url_2 = "http://www.sots.ct.gov/sots/lib/sots/electionservices/lists/rovofficeaddresses.pdf"
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

absdata = open(file_path_1).read()
regdata = open(file_path_2).read()


#Check to make sure that W I doesn't appear in the source documents before running.
absdata = dogcatcher.po_standardize(absdata.replace("W I","WI").replace("","").replace("ONE FIRST","1 FIRST"))
regdata = dogcatcher.po_standardize(regdata.replace("W I","WI").replace("","").replace("ONE FIRST","1 FIRST"))
absdata = absdata.replace("\nN. ","\nNorth ")
regdata = regdata.replace("N. S","North S")

header_re = re.compile(".+?\d{2}:\d{2}:\d{2} [AP]M", re.DOTALL)

for item in header_re.findall(absdata):
    absdata = absdata.replace(item,"")

abstown_re = re.compile("([A-Z][A-Z].+?TOWN CLERK.+?)\n\n", re.DOTALL)
regtown_re = re.compile("REGISTRAR[S]* OF .+?CT\s*\d{5}[-\d]*\n\n", re.DOTALL)
regtown_name_re = re.compile("REGIS.+?, (.+)")
abstown_name_re = re.compile("(.+) TOWN CLERK")
party_re = re.compile(" [\[\(].+?[\)\]]")


#This will fail if the only address is a PO Box [A-Z].  Check data for this beforehand.
address_re = re.compile("([^\n]*\d.+?)\n\n",re.DOTALL)
abs_address_re = re.compile("([^\n]*\d.+?)[\s]+Bus",re.DOTALL)
csz_re = re.compile(".+?, *[A-Z][A-Z] *\d{5}[\d-]*")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile(" (\d{5}[\d-]*)")
po_re = re.compile("P*\.*O*\.* *[BD][OR][XA].+")

phone_re = re.compile("Bus: (.+)")
fax_re = re.compile("Fax: (.....+)")
email_re = re.compile("Email: (.+)")
name_re = re.compile(".+")

abstowns = abstown_re.findall(absdata)
regtowns = regtown_re.findall(regdata)

abse = []
reg = []

#The towns came out of the PDF in the lord only knows what order. So we first extract town names from each town and create a list of [town, town_name] pairs in both the registration and absentee data.
#We then sort both lists by town name.

for town in abstowns:
    regtown = regtowns[abstowns.index(town)]
    regtown_name = " ".join(regtown_name_re.findall(regtown)[0].title().strip().split())
    abstown_name = " ".join(abstown_name_re.findall(town)[0].title().split())
    for party in party_re.findall(abstown_name): #The town names also have a party affiliation contained within. Here, we strip that out.
        abstown_name = abstown_name.replace(party,"").strip()

    abse.append([town, abstown_name])
    reg.append([regtown, regtown_name])

abse.sort(lambda x, y: cmp(x[1],y[1]))
reg.sort(lambda x, y: cmp(x[1],y[1]))

for item in abse:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    authority_name = "Town Clerk"
    reg_authority_name = "Registrar of Voters"

    town = item[0]
    abstown_name = item[1]
    try:
        regitem = reg[abse.index(item)]
    except:
        continue
    regtown = regitem[0]
    regtown_name = regitem[1]

    print [abstown_name], [regtown_name]

    if regtown_name == abstown_name:
        town_name = abstown_name
    else:
        print "The lists don't match. Stopping the code."
        print [abstown_name]
        print [regtown_name]
        sys.exit()

    #This section finds the full address for the registrar of voters. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.


    reg_address = address_re.findall(regtown)[0]


    reg_csz = csz_re.findall(reg_address)[0]
    if not reg_address.replace(reg_csz,""):
        reg_address = po_re.findall(regtown)[0]#The address grab will fail if address is only a PO Box [A-Z]. If there's no real address, we try this instead.

    try:
        reg_po_street = po_re.findall(reg_address)[0].replace(reg_csz,"").strip(", \n").title()
    except:
        reg_po_street = ""


    reg_street = reg_address.replace(reg_po_street,"").replace(reg_csz,"")
    reg_street = reg_street.replace("\n",", ").replace(" ,",",").strip(" \n/,").title()

    if reg_po_street:
        reg_po_city = city_re.findall(reg_csz)[0].strip().title()
        reg_po_state = state_re.findall(reg_csz)[0].strip()
        reg_po_zip_code = zip_re.findall(reg_csz)[0].strip().title()
    if reg_street:
        reg_city = city_re.findall(reg_csz)[0].strip().title()
        reg_state = state_re.findall(reg_csz)[0].strip()
        reg_zip_code = zip_re.findall(reg_csz)[0].strip().title()



    phone = dogcatcher.find_phone(phone_re, town, areacode = "203")

    if ("(203) 203-") in phone:
        phone = dogcatcher.clean_phone(phone.partition(" ")[2])
        print phone

    email = dogcatcher.find_emails(email_re, town)
    fax = dogcatcher.find_phone(fax_re, town)

    official_name = name_re.findall(town)[0].title()
    first_name, last_name, review = dogcatcher.split_name(official_name, review)

    #This section finds the full address for the town clerk. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.


    address = abs_address_re.findall(town)[0]

    csz = csz_re.findall(address)[0]

    if not address.replace(csz,""):
        address = po_re.findall(town)[0]#The address grab will fail if address is only a PO Box [A-Z]. If there's no real address, we try this instead.

    try:
        po_street = po_re.findall(address)[0].replace(csz,"").strip(", \n").title()
    except:
        po_street = ""


    street = address.replace(po_street,"").replace(csz,"")
    street = street.replace("\n",", ").replace(" ,",",").strip(" \n/,").title()

    if po_street:
        po_city = city_re.findall(csz)[0].strip().title()
        po_state = state_re.findall(csz)[0].strip()
        po_zip_code = zip_re.findall(csz)[0].strip().title()
    if street:
        city = city_re.findall(csz)[0].strip().title()
        address_state = state_re.findall(csz)[0].strip()
        zip_code = zip_re.findall(csz)[0].strip().title()

    if street:
        fips, county_name = dogcatcher.map_fips(city, address_state, town_name, zip_code)
    else:
        fips, county_name = dogcatcher.map_fips(po_city, po_state, town_name, po_zip_code)

    result.append([authority_name, first_name, last_name, town_name, fips, county_name,
    street, city, address_state, zip_code,
    po_street, po_city, po_state, po_zip_code,
    reg_authority_name, reg_first, reg_last,
    reg_street, reg_city, reg_state, reg_zip_code,
    reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
    reg_phone, reg_fax, reg_email, reg_website, reg_hours,
    phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.
dogcatcher.output(result, voter_state, cdir, "cities")

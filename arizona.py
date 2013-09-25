import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

url = "http://www.azsos.gov/election/county.htm"
file_path = cdir + "arizona-clerks.html"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

voter_state = "AZ"
source = "State"

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

data = open(file_path).read()

data = data.replace("&quot;","'")

county_data_re = re.compile("Register to vote\.\.\.(.+?)EARLY BALLOT", re.DOTALL)#<td width=\"10%\" valign=\"top\" class=\"Normal\">&nbsp;</td>", re.DOTALL)
county_name_re = re.compile("target=\".+?\">(.+?)\s+?Recorder website", re.DOTALL)

name_re = re.compile("[\s<pbng^/]+?>([^<>\d]+? [^<>\d\s]+?)\s*<[/brstong ]*>")
name_2_re = re.compile("[^<>]+")
middle_name_re = re.compile(" ([a-zA-z]\. )")

name_re = re.compile("([A-Z][A-Za-z \.'-]+?) *<[br /]+>")

phone_re = re.compile("TELEPHONE\s*(.+?)<br />", re.DOTALL)
fax_re = re.compile("FAX\s*(.+?)<br />", re.DOTALL)

email_re = re.compile("<a href=\"[Mm]ailto:(.+?)\"")
website_re = re.compile("href=\"([^@]+?)\"")
csz_re = re.compile("\s*(.+?, [A-Z][A-Z] \d{5}[-\d]*?)")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]) ")
zip_re = re.compile("(\d{5}[-\d]*?)")

#address_re = re.compile("\s+(.+\r\n +.+?, [A-Z][A-Z] \d{5}[-\d]*?)")#, re.DOTALL)
address_re = re.compile("<b>.+?,.+?</b>(.+?, [A-Z][A-Z] \d{5}[-\d]*?)", re.DOTALL)
po_re = re.compile("(P\.*\s*O\.*)")
digit_re = re.compile("\d")
letter_re = re.compile("[a-zA-Z]")

county_data = county_data_re.findall(data)

for county in county_data:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)
    print "________________________________________________________"
    print [county]

    authority_name = "County Recorder"

    county_name = county_name_re.findall(county)[0].title().replace("County","").strip(" \r\n")

    print "COUNTY NAME: " + county_name

    #The addresses are formatted in the following way: "</b>[Street or PO Box]<br />...City, State Zip<br />"
    #This finds the complete address; extracts the line with the city, state, and zip (csz), and then, based on whether there's a PO Box or a street, extracts the city, state, and zip code, and forms the street address or PO box by removing the csz and extra text from the full address.

    address = address_re.findall(county)[0]

    csz = csz_re.findall(address)[0]

    if po_re.search(address):
        po_city = city_re.findall(csz)[0]
        po_state = state_re.findall(csz)[0]
        po_zip_code = zip_re.findall(csz)[0]
        po_street = address.replace(csz,"").replace("</b>","").replace("<br />","").strip(" \r\n")
    else:
        city = city_re.findall(csz)[0]
        address_state = state_re.findall(csz)[0]
        zip_code = zip_re.findall(csz)[0]
        street = address.replace(csz,"").replace("</b>","").replace("<br />","").strip(" \r\n")

    official_name = name_re.findall(county)[0]

    first_name, last_name, review = dogcatcher.split_name(official_name, review)

    phone = dogcatcher.find_phone(phone_re, county)

    fax = dogcatcher.find_phone(fax_re, county)

    email = dogcatcher.find_emails(email_re, county)

    if county_name == "Apache":
        email = "lfulton@co.apache.az.us"

    #print [street]

    website = dogcatcher.find_website(website_re, county)

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
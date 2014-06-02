import urllib
import re
import sys
import xlrd
import urllib2
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

voter_state = "OK"
source = "state"


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#The following section grabs the pdf and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

file_path = tmpdir + "oklahoma-clerks.txt"
url = "http://www.ok.gov/elections/documents/cebinfo.pdf"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

req = urllib2.Request(url, headers=headers)
pdf = urllib2.urlopen(req).read()

data = dogcatcher.pdf_to_text(pdf)
output = open(file_path, "w")
output.write(data)
output.close()

data = open(file_path).read()

phone_name_re = re.compile("(\d{3}-\d{3}-\d{4} \d{3}.+? [^\d\n\t\r]+)")
hours_re = re.compile("\d:\d{2}-.+")
county_name_re = re.compile("\n(\d[\d ] *[A-Z][a-zA-Z ]+)")

lowercase_clean_re = re.compile("[^ ] +[a-z]") #Sometimes there's a random break between an uppercase letter and a lowercase. This catches and cleans those.

for item in lowercase_clean_re.findall(data):
    item_rep = item.replace(" ","")
    data = data.replace(item, item_rep)

#When we clean the PDF, the data breaks down into a handful of regular patterns. These are lines that looks like
#phones and names, lines that look like county names, lines that look like office hours, and blocks of lines that look like addresses.
#First thing we do is find the phone/name lines, the county names, and the hours.
#Then we remove them from the complete data; clean out a bit of junk that messes up our formatting; and pull out the addresses.

phone_names = phone_name_re.findall(data)
hours_all = hours_re.findall(data)
county_names = county_name_re.findall(data)

#Huge amount of data cleaning follows.

county_name_error_re = re.compile("\d[\d ] *N Main St") #This is an address which gets picked up in the regex used to detect county names.

for item in county_name_error_re.findall(data):
    while county_names.count(item) >0:
        county_names.remove(item)

county_name_error_re = re.compile("\d[\d ] *Court Pl") #This is an address which gets picked up in the regex used to detect county names.

for item in county_name_error_re.findall(data):
    while county_names.count(item) >0:
        county_names.remove(item)

data = data.replace("","")
data = data.replace("\nst","").replace("\nnd","").replace("\nth","").replace("\nrd","")

for item in phone_names:
    data = data.replace(item,"\n")
for item in county_names:
    data = data.replace(item,"\n",1)
for item in hours_all:
    data = data.replace(item,"\n")

#Cleaning some junk text out of the remaining data:

numbers_clean_re = re.compile("COUNTY[^-]+HOURS *")
revised_re = re.compile("REVISED: .+")
disclaimer_re = re.compile("\*.+")
email_clean_re = re.compile("E-mail.+?Information", re.DOTALL)

for item in numbers_clean_re.findall(data):
    data = data.replace(item,"")
for item in revised_re.findall(data):
    data = data.replace(item,"")
for item in disclaimer_re.findall(data):
    data = data.replace(item,"")
for item in email_clean_re.findall(data):
    data = data.replace(item,"")

#Constructing address blocks and putting them in the correct order:

print data

address_block_re = re.compile("[^\n]+?\n+[^\n]+",re.DOTALL)
zip_split_re = re.compile("\d{5}-\n\d{4}", re.DOTALL)
space_end_re = re.compile(" +\n")
multi_break_re = re.compile("\n\n+")

#Sometimes the zip code splits down the middle. This fixes that.
for item in zip_split_re.findall(data):
    item_rep = item.replace("\n","")
    data = data.replace(item, item_rep)

#This cleans out extra spaces at the end of a line.
for item in space_end_re.findall(data):
    data = data.replace(item, "\n")

#In several places, things we'd like to have be two lines are one--this bit of code sorts through them and breaks them up.
single_lines = ["101 420", "101 110", "105 325", "101 109", "5 114 W  Hollis St", "108 210", "301 PO Box 9", "120 PO Box 216"]
for item in single_lines:
    item_rep = item.replace(" "," \n",1)
    data = data.replace(item, item_rep)

for item in multi_break_re.findall(data):
    data = data.replace(item,"\n")

#Finally, we turn the address blocks into a list of addresses.
address_blocks = address_block_re.findall(data)

print "Number of phone_names", len(phone_names)
print "Number of hours_all", len(hours_all)
print "Number of county_names", len(county_names)
print "Number of address_blocks", len(address_blocks)

if len(phone_names) != 77:
    sys.exit("ISSUE: Something's wrong with the phone, fax, or names items. There are the wrong number of items.")
if len(hours_all) != 77:
    sys.exit("ISSUE: Something's wrong with the office hours items. There are the wrong number of items.")
if len(county_names) != 77:
    sys.exit("ISSUE: Something's wrong with the county names. There are the wrong number of items.")
if len(address_blocks) != 77:
    sys.exit("ISSUE: Something's wrong with the address blocks. There are the wrong number of items.")


mailing_re = re.compile(".+?\d{5}[\d-]*")
cz_re = re.compile(", [^,]+")
zip_re = re.compile("\d{5}[\d-]*")

for i in range(0,77):

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    #print "___________________________________________"
    authority_name = "County Election Board"
    phone_name = phone_names[i]
    hours = hours_all[i]
    county_name = county_names[i].replace("LeFlore","Le Flore")
    address_block = address_blocks[i]

    phone = dogcatcher.clean_phone(phone_name.partition(" ")[0])
    fax = dogcatcher.clean_phone(phone_name.partition(" ")[2].partition(" ")[0])


    official_name = phone_name.partition(" ")[2].partition(" ")[2]
    first_name, last_name, review = dogcatcher.split_name(official_name, review, "ignore")

    county_name = county_name.replace(str(i+1),"").strip() #Every county name is attached to a number. We want to remove them.

    #One of the items in the address is a mailing address (which may be the same as the physical address.)
    #We extract it first, and pull the city/zip pair (states are not included in the data) out of it.
    #Then we see if there's a street address left when we remove the mailing address and the cz from the full mailing block.
    #If there is, the mailing address must be different from the physical address.
    #If not, there's only a physical address.

    mailing = mailing_re.findall(address_block)[0]
    cz = cz_re.findall(mailing)[len(cz_re.findall(mailing))-1]

    zip_code = zip_re.findall(cz)[0]
    city = cz.replace(zip_code,"").strip(", ")

    street = address_block.replace(mailing,"").strip(", \n")

    if street:
        po_street = mailing.replace(cz,"").strip(", \n")
        po_zip_code = zip_code
        po_city = city
        po_state = address_state
    else:
        po_street = ""

    if "PO Box" not in po_street and po_street:
        review = review + "h"

    #Reg forms are supposed to go to the state election office. Its information follows.

    reg_street = "2300 N Lincoln Blvd"
    reg_city = "Oklahoma City"
    reg_zip_code = "75312"
    reg_po_street = "PO Box 53156"
    reg_phone = "(405) 521-2391"
    reg_email = "info@elections.ok.gov"


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

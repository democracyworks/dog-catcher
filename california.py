import os
import urllib
import re
import sys
import dogcatcher

voter_state = "CA"
source = "State"

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time in testing.)

url = "http://www.sos.ca.gov/elections/elections_d.htm"
file_path = cdir + "california-clerks.html"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

data = open(file_path).read()


county_name_re = re.compile("<h2>(.+?) \(\d{2}\)</h2>")
county_data_re = re.compile("(<h2>[^\n]+? \(\d{2}\)</h2>[\s]*<ul class=\"list-no-disc\">.+?)</ul>", re.DOTALL)
county_data_item_re = re.compile("<li.*?>(.+?)</li")
phone_re = re.compile("(\(\d{3}\) \d{3}-\d{4})[^F]*<")
fax_re = re.compile("(\(\d{3}\) \d{3}-\d{4}) F")
email_re = re.compile("E-[Mm]ail: <a href=[ \"]*m.*?>(.+?)</a>")
website_re = re.compile("Website: <a href= *\"(.*?)\">.+?</a>", re.DOTALL)
zip_re = re.compile(".+?(\d{5}[-\d]*)")
city_re = re.compile("(.+?),")
state_re = re.compile(" [A-Z]{2} ")
address_re = re.compile("<li>([^<>]*?\d.+?\d{5}[\d -]*</li>)", re.DOTALL)
csz_re = re.compile("<li>(.+?, CA .+?)</li>")
name_line2_re = re.compile("\d")

data = data.replace("&amp;","&")

#This splits the complete data into a list containing one item/county.

county_data = county_data_re.findall(data)


for county in county_data:

  authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

  county_name = county_name_re.findall(county)[0]

  county_data_item = county_data_item_re.findall(county)

  first_name, last_name, authority_name, review = dogcatcher.make_name(county_data_item[0], ", ", review)

  print county_data_item[0]

  #print authority_name + " | " + first_name + " " + last_name


  #This section generates the address. It does so by identifying whether there are one or two address-looking things in the data. (CA explicitly prints a separate mailing address when counties have them.)
  #CA addresses are formatted "Street\nCity, State, Zip"
  #If there is one, it is the mailing and registration address; if there are two, the second is the mailing address, and the first is the address.
  #After finding these, it applies the same procedure to both: it identifies a city/state/zip (csz) combination and removes that from the full address, leaving behind a street address with some garbage.
  #It then cleans up the street address and pulls the city, state, and zip out of the csz.

  address_full = address_re.findall(county)
  address = address_full[0]
  if len(address_full)>1:
    mailing_address = address_full[1]
  else:
    mailing_address = ""

  csz = csz_re.findall(address)[0]

  if mailing_address:
    mailing_csz = csz_re.findall(mailing_address)[0]
    po_street = mailing_address.replace(mailing_csz,"")
    po_street = po_street.replace("<li>","").replace("</li>","").replace("\n",", ").replace("\r","").replace(" ,",",").strip(" ,")
  
  street = address.replace(csz,"")
  street = street.replace("<li>","").replace("</li>","").replace("\n",", ").replace("\r","").replace(" ,",",").strip(" ,")

  if po_street:
    if street:
      city = city_re.findall(csz)[0]
      address_state = state_re.findall(csz)[0]
      zip_code = zip_re.findall(csz)[0]
    po_city = city_re.findall(mailing_csz)[0].strip()
    po_state = state_re.findall(mailing_csz)[0].strip()
    po_zip_code = zip_re.findall(mailing_csz)[0].strip()
  else:
    city = city_re.findall(csz)[0].strip()
    address_state = state_re.findall(csz)[0].strip()
    zip_code = zip_re.findall(csz)[0].strip()

  #This fixes bad data in a particular county.

  if "555 Escobar Street" in street:
    street = "555 Escobar Street"
    city = "Martinez"
    address_state = "CA"

  phone_data = dogcatcher.find_phone(phone_re, county)
  fax = dogcatcher.find_phone(fax_re, county)

  # phone_re.findall(county)
  # phone = phone_data[0][0]
  # fax = phone_data[1][0]

  email = dogcatcher.find_emails(email_re, county)
  if county == "Ventura":
    email = ""

  print po_street


  website = dogcatcher.find_website(website_re, county)

  #Any given county may or may not have included Hours.
  	
  if "Hours:" in county_data_item[5]:
    hours = county_data_item[5].split("s: ")[1]
  else:
    hours = ""

  fips = dogcatcher.find_fips(county_name, voter_state)

  print street

  result.append([authority_name, first_name, last_name, county_name, fips,
  street, city, address_state, zip_code,
  po_street, po_city, po_state, po_zip_code,
  reg_authority_name, reg_first, reg_last,
  reg_street, reg_city, reg_state, reg_zip_code,
  reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
  reg_phone, reg_fax, reg_email, reg_website, reg_hours,
  phone, fax, email, website, hours, voter_state, source, review])

  print "___________________________________________"

#This outputs the results to a separate text file.

dogcatcher.output(result, voter_state, cdir)
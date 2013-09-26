import os
import urllib
import re
import sys
import HTMLParser
import json
import time
import dogcatcher

h = HTMLParser.HTMLParser()

voter_state = "MA"
source = "State"

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
file_path = cdir + "massachusetts-clerks.html"

url = "http://www.sec.state.ma.us/ele/eleclk/clkidx.htm"
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

town_data_re = re.compile("(<span class=\"citytown\">.+?)</p>", re.DOTALL)
town_data_item_re = re.compile("\r\n.+?(\S.+?)(?:<br />|</p>)")
town_name_re = re.compile("\"citytown\">(.+?)</span>")
office_name_re = re.compile("\"citytown\">.+?</span><br />(.+?)", re.DOTALL)


address_re = re.compile("<br />[\s]* (.+?\r\s*\d{5}[\d-]*)", re.DOTALL)
text_only_re = re.compile("<br />\s*[^\d]+<br />\s*")
break_re = re.compile("<br />\s*")
csz_re = re.compile("([^,]+?, [A-Z][A-Z], \d{5}[\d-]*)")
is_street_re = re.compile("[\s,]")
city_re = re.compile("(.+?),")
state_re = re.compile(" ([A-Z][A-Z]), ")
zip_re = re.compile(", (\d{5}[\d-]*)")
hours_re =re.compile("Hours: (.+)")

town_name_fix_re = re.compile("<a name=\"[a-z]\" id=\"[a-z]\"></a>")

mailing_address_re = re.compile("(PO.+?)<br />")
po_re = re.compile("(P\.* *O\.* .+?)<br />")
email_re = re.compile("Email: <a href=\".+?\">(.+?)</a>")
fax_re = re.compile("Fax: (.+?)<br />")
phone_re = re.compile("Phone: (.+?)<br />")
digit_re = re.compile("\d| ONE | TWO | THREE | FOUR | FIVE | SIX | SEVEN | EIGHT | NINE ")
website_re = re.compile("Website: <a href=\".+?\">(.+?)</a>")

data = data.replace("<br/>","<br />")
data = data.replace("<br>","<br />")
data = data.replace("&rsquo;","'").replace("&amp;","&")

#fixing an error in Uxbridge

data = data.replace("</a>kbickford@uxbridge-ma.gov","kbickford@uxbridge-ma.gov</a>")

for letter in town_name_fix_re.findall(data):
  data = data.replace(letter,"")

#This breaks the complete dataset into a list of strings, each of which is a town.

town_data = town_data_re.findall(data)


for town in town_data:
  authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

  town_data_item = town_data_item_re.findall(town)

  town_name = town_name_re.findall(town)[0].title().strip()

  #The MA data is highly variable in what it includes per state. So the code makes an attempt at grabbing all of the possible secondary pieces of info available, but recognizes that it may not be able to get everything.

  fax = dogcatcher.find_website(fax_re, town)
  phone = dogcatcher.find_phone(phone_re, town)
  try:
    email = email_re.findall(town)[0].lower()
  except:
  	email = ""
  try: 
    website = dogcatcher.find_website(website_re, town)
  except:
  	website = ""


  if town_name == "Ware":
    town_data_item.insert(0, "TOWN CLERK")

  authority_name = town_data_item[0].title().replace("'S","'s").replace(town_name.upper(),"").strip(", ")
  
  #This section generates the address.
  #MA addresses are formatted "Street\nAdditional namep--i.e., Town Clerk (maybe)\nMailing(If it exists)\nCity, State (If city isn't the town name)\nZip"
  #It first sees whether there is a mailing adddress, and if so, stores that address.
  #It next removes every line break to get the entire address into one line.
  #It then sees whether there is a city/state combination.
  #It then follows the normal procedure: generating the street address by removing everything else, identifying the city and state, and so forth.

 
  address = address_re.findall(town)[0].replace(authority_name.upper(),"").strip(" ,")

  try:
    po_street = po_re.findall(address)[0].replace(authority_name.upper(),"").strip(" ,")
  except:
    po_street = ""

  #This strips any line which is only text--usually "Town Clerk" or something--from the address

  for text in text_only_re.findall(address):
    address = address.replace(text,", ")
  for lbreak in break_re.findall(address):
    address = address.replace(lbreak,", ")
  try:
    csz = csz_re.findall(address)[0]
  except:
    csz = ""
  address = " ".join(address.split())

  zip_code = zip_re.findall(address)[0]
  
  if po_street:
    street = address.replace(csz,"").replace(po_street,"").replace(town_data_item[0],"").replace(zip_code,"")
  else:
    street = address.replace(csz,"").replace(po_street,"").replace(zip_code,"")
  street = street.strip(", ")

  #This was the part that was adding the authority name.
  #if not is_street_re.findall(street):
   # street = ""
    #po_street = town_data_item[0] + ", " + po_street

  if csz:
    if street:
      city = city_re.findall(csz)[0].strip()
      address_state = state_re.findall(csz)[0].strip()
    if po_street:
      po_city = city_re.findall(csz)[0].strip()
      po_state = state_re.findall(csz)[0].strip()
      po_zip_code = zip_code
  else:
    if street:
      city = town_name
      if po_street:
        po_city = town_name
        po_zip_code = zip_code
    else:
      po_city = town_name
      po_zip_code = zip_code

  if town_name == "Rowe" and street == "34 BROADWAY":
    street = "321 Zoar Road"
  
  hours = hours_re.findall(town)[0]

  #This matches the towns to counties to acquire accurate FIPS.

  print "___________________"
  base_url = "http://maps.google.com/maps/api/geocode/json?sensor=false&address=%s"

  if street:
    fips, county_name = dogcatcher.map_fips(city, address_state, zip_code)
  else:
    fips, county_name = dogcatcher.map_fips(po_city, po_state, po_zip_code)

  result.append([authority_name, first_name, last_name, town_name, fips,
  street, city, address_state, zip_code,
  po_street, po_city, po_state, po_zip_code,
  reg_authority_name, reg_first, reg_last,
  reg_street, reg_city, reg_state, reg_zip_code,
  reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
  reg_phone, reg_fax, reg_email, reg_website, reg_hours,
  phone, fax, email, website, hours, voter_state, source, review])

dogcatcher.output(result, voter_state, cdir, "cities")
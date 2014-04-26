import sys
import mechanize
import re
import json
import time
import urllib
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"


voter_state = "PA"
source = "State"


result = [("authory_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


#Every county is a different item in a dropdown menu, so we have to cycle through them all.
#To do so, we grab the dropdown menu, extract a list of counties, then grab a series of web pages based on that list.
#This grabs a page containing a list of PA counties and writes it to a file. Writing it isn't strictly necessary, but saves some run time in the long run.
#We save separate lists of county names and county references because the references used in the dropdown menus are different from the county's names.


county_ref_list_re = re.compile("option value=\"(.+?)\">[A-Z ]+</option>")
county_names_re = re.compile("option value=\".+?\">([A-Z ]+)</option>")

file_path = cdir + "pennsylvania-counties.html"
url = "http://www.portal.state.pa.us/portal/server.pt?open=514&objID=1174076&parentname=ObjMgr&parentid=60&mode=2"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

#print data

county_ref_list = county_ref_list_re.findall(data)
county_names = county_names_re.findall(data)

trim_re = re.compile("<div id=\"ContactInfo99273.+?<div(.+?)</form>", re.DOTALL)

#This uses the mechanize package to submit every item in county_list--the list of county names as used in the menu--and grab and save webpage based on each one.

for county in county_ref_list:
	print county
	
	br = mechanize.Browser() #Creates a mechanize browser object.
	br.set_handle_robots(False) # ignore robots.txt
	br.open(url) #Opens the page.
	br.select_form(name = "form1_99273") #The drop-down menu is titled form1_99273.
	br["ddlCounty"] = [county,] #It takes an input called ddlCounty.
	res = br.submit() #res is the resulting page when we submit the inputs from earlier
	content = res.read() #this creates a string of the page.
	trimmed_content = trim_re.findall(content)[0] #this trims the page down to only what we need.
	#This writes the page to a file.
	file_path = cdir + county + "-pa-clerks.html"
	output = open(file_path,"w")
	output.write(trimmed_content)
	output.close()


county_data_item_re = re.compile("(.+?)<br>")
phone_re = re.compile("Telephone: (.+)<")
fax_re = re.compile("Fax: (.+)<")
email_re = re.compile("[^<> ]+@[^<> ]*")
website_re = re.compile("(http://.+?)<")
phone_re = re.compile("(\(\d{3}.+?)<")

name_re = re.compile("</div><div +> *(.+?)<")
address_re = re.compile(">([^<>]*?\d.+?[A-Z]{2,2} \d{5}[\d-]*)")
po_re = re.compile("(P\.O\..+?)[<,]")
csz_re = re.compile("[^<>]+?, [A-Z]{2,2} [\d-]+")
city_re = re.compile(" *(.+?),")
state_re = re.compile("[A-Z]{2,2}")
zip_re = re.compile("\d{5}[\d-]*")

digit_re = re.compile("\d")
direct_re = re.compile(">([A-Za-z/., &-]+)<")

paren_re = re.compile("\(.+?\)")

clean_re = re.compile("[a-z]+=\".+?\"")

t_re = re.compile("\t+")

for county_id in county_ref_list:
	
	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	file_path = cdir + county_id + "-pa-clerks.html"


	county = open(file_path).read().replace("&nbsp;"," ").replace("&nbsp","").replace("Post Office","P.O.")
	for item in clean_re.findall(county):
		county = county.replace(item,"")
	for item in t_re.findall(county):
		county = county.replace(item," ")

	county_name = county_names[county_ref_list.index(county_id)].title()

	print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"

	if county_name == "Northampton":
		print county
		#sys.exit()

	#PA has both absentee and registration offices, so we need to split it.
	#They split in a neat place, so we're able to use partition instead of a regular expression.
	#Another part of the content is the county website, so we split that off as well.
	#This yields three pieces of data: absentee (absentee voting official), registration (registration official), and county_web (website official).

	offices = county.partition("div  >Voter Registration")
	absentee = offices[0]
	regweb = offices[2].partition("County Website")
	registration = regweb[0]
	county_web = regweb[2]

	
	website = dogcatcher.find_website(website_re, county_web)
	reg_website = website


	email = dogcatcher.find_emails(email_re, absentee)
	reg_email = dogcatcher.find_emails(email_re, registration)

	phone = dogcatcher.find_phone(phone_re, absentee)
	reg_phone = dogcatcher.find_phone(phone_re, registration)


	# print absentee
	# print registration
	print name_re.findall(absentee)
	absentee_official = name_re.findall(absentee)[0].replace("</div>","") #In one county, the regular expression used yields </div> as a response. The other easy fix creates more problems, so we just remove the </div>.
	first_name, last_name, review = dogcatcher.split_name(absentee_official, review)

	if absentee_official:
		authority_name = direct_re.findall(absentee)[2].replace(county_name + " County","").replace(county_name + " Co","").replace(county_name,"").replace(" . "," ").strip(", .")
	else:
		authority_name = direct_re.findall(absentee)[1].replace(county_name + " County","").replace(county_name + " Co","").replace(county_name,"").replace(" . "," ").strip(", .")


	reg_official = name_re.findall(registration)[0].replace("</div>","") #In one county, the regular expression used yields </div> as a response. The other easy fix creates more problems, so we just remove the </div>.
	reg_first, reg_last, review = dogcatcher.split_name(reg_official, review)

	print ["0", reg_official]
	print ["1", absentee]
	print ["2", regweb]

	if reg_official and direct_re.findall(registration):
		reg_authority_name = direct_re.findall(registration)[1].replace(county_name + " County","").replace(county_name + " Co","").replace(county_name,"").replace(" . "," ").strip(", .")
	elif direct_re.findall(registration):
		reg_authority_name = direct_re.findall(registration)[0].replace(county_name + " County","").replace(county_name + " Co","").replace(county_name,"").replace(" . "," ").strip(", .")
	else:
		reg_authority_name = authority_name

	#This section finds the full address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and mailing address.

	abs_address = address_re.findall(absentee)[0]
	
	csz = csz_re.findall(abs_address)[0].strip()

	try:
		po_street = po_re.findall(abs_address)[0]
	except:
		po_street = ""

	street = abs_address.replace(po_street,"").replace(csz,"").replace("<br />",", ")
	street = " ".join(street.replace(" ,",",").strip(" \n/,").split())

	if street:
		city = city_re.findall(csz)[0]
		address_state = state_re.findall(csz)[0]
		zip_code = zip_re.findall(csz)[0]
	if po_street:
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()

	reg_address = address_re.findall(registration)[0]

	reg_csz = csz_re.findall(reg_address)[0].strip()
	#print registration

	try:
		reg_po_street = po_re.findall(reg_address)[0]
	except:
		reg_po_street = ""

	reg_street = reg_address.replace(reg_po_street,"").replace(reg_csz,"").replace("<br />",", ")
	reg_street = " ".join(reg_street.replace(" ,",",").strip(" \n/,").split())

	if reg_street:
		reg_city = city_re.findall(reg_csz)[0]
		reg_state = state_re.findall(reg_csz)[0]
		reg_zip_code = zip_re.findall(reg_csz)[0]
	if reg_po_street:
		reg_po_city = city_re.findall(reg_csz)[0].strip()
		reg_po_state = state_re.findall(reg_csz)[0].strip()
		reg_po_zip_code = zip_re.findall(reg_csz)[0].strip()


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
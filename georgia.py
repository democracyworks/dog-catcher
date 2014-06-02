import mechanize
import re
import sys
import urllib
import dogcatcher
import os

voter_state = "GA"
source = "State"

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"
tmpdir = cdir + "tmp/"

#Every county is a different item in a dropdown menu, so we have to cycle through them all.
#To do so, we grab the dropdown menu, extract a list of counties, then grab a series of web pages based on that list.
#This grabs a page containing a list of GA counties and writes it to a file. Writing it isn't strictly necessary, but saves some run time in the long run.

file_path = tmpdir + "georgia-counties.html"

url = "http://sos.georgia.gov/cgi-bin/countyregistrarsindex.asp"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

data = open(file_path).read()

#This extracts a list of county names as referred to in the HTML of the drop-down menu from the webpage grabbed earlier

county_list_re = re.compile("option value=\"(.+?)\"")
county_list = county_list_re.findall(data)

trim_re = re.compile("<span class=\"Style49\"><b>(.+?)</b></span>", re.DOTALL)

#This uses the mechanize package to submit every item in county_list--the list of county names as used in the menu--and grab a webpage based on each one.

for county in county_list:
#	print county

	br = mechanize.Browser() #Creates a mechanize browser object.
	br.set_handle_robots(False) # ignore robots
	br.open(url) #Opens the page.
	br.select_form(name = "form1") #The drop-down menu is titled form1.
	br["CountyName"] = [county,] #It takes an input called CountyName.
	res = br.submit() #res is the resulting page when we submit the inputs from earlier
	content = res.read() #this creates a string of the page.

	trimmed_content = trim_re.findall(content)
	if trimmed_content != None and len(trimmed_content) > 0:
		trimmed_content = trimmed_content[0]
	else:
		print "No content found for", county
		continue

	#This writes the page to a file.
	file_path = tmpdir + county + "-ga-clerks.html"
	output = open(file_path,"w")
	output.write(trimmed_content)
	output.close()

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]


county_data_item_re = re.compile("(.+?)<br>")
phone_re = re.compile("Telephone: (.+)<")
fax_re = re.compile("Fax: (.+)<")
email_re = re.compile("mailto:(.+?)\"")
website_re = re.compile("href=\"(h.+?)\"")
zip_re = re.compile("[A-Z][A-Z] (\d{5}[\d-]*)")

city_re = re.compile("(.+?), [A-Z][A-Z]")
state_re = re.compile(" ([A-Z][A-Z]) ")
po_re = re.compile("(P[\. OST]*O[\.FICE]* [BbD].+), ", re.DOTALL)
digit_re = re.compile("\d")
mailing_re = re.compile(".+?\(mailing address\)")

paren_re = re.compile("\(.+?\)")

#This cycles through every county name; grabs the appropriate file; and cleans the data in there.

for county_name in county_list:

	file_path = tmpdir + county_name + "-ga-clerks.html"

	county = open(file_path).read().replace("&nbsp;"," ").replace("Post Office","P.O.")

	county_data_item = county_data_item_re.findall(county)

	#The first line is always the authority name; this grabs it, and then removes it from the entire data set.
	authority_name = county_data_item[0]
	county_data_item.pop(0)

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	phone = dogcatcher.find_phone(phone_re, county)

	fax = dogcatcher.find_phone(fax_re,county)

	email = dogcatcher.find_emails(email_re, county)

	try:
		website = dogcatcher.find_website(website_re, county)
	except:
		website = ""

	# print "+++++++++++++++++++++++++++++++++++++++++++++++"
	# print county
	# print "-----------------------------------------------"

	#The address can start at an irregular place in the address, and lasts for an irregular length.
	#This finds the line that the address starts at by looking for a number from 0-10 (which first appear in the address) and creates address_start
	# It then finds the line it ends at and makes it address_end.

	address_start = -1
	for item in county_data_item:
		if address_start == -1 and digit_re.findall(item):
			address_start = county_data_item.index(item)
		if zip_re.findall(item):
			address_end = county_data_item.index(item)
			break

	#This makes the street address out of every line of the address except for the addresS_end line, which is the CSZ (city, state, zip).

	street = ", ".join(county_data_item[address_start:address_end-1]) + ", "
	csz = county_data_item[address_end]

	#This checks whether there's a PO box or a line marked "(mailing address)" in the street address. If there is, it extracts that and removes it from the street address.
	#If not, it sets po_street to null.

	if po_re.findall(street):
		po_street = po_re.findall(street)[0]
		street = street.replace(po_street,"")
	elif mailing_re.findall(county):
		po_street = mailing_re.findall(county)[0].replace("(mailing address)","")
		street = street.replace(po_street,"").replace("(mailing address)","")
	else:
		po_street = ""

	#This cleans the street address as needed.

	street = " ".join(street.replace(" ,",",").strip(" \n/,").split())

	#This extracts city, state, and zip from the CSZ as appropriate based on whether there exists a mailing address and a street address.

	if po_street:
		if street:
			city = city_re.findall(csz)[0]
			address_state = state_re.findall(csz)[0]
			zip_code = zip_re.findall(csz)[0]
		po_city = city_re.findall(csz)[0].strip()
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	else:
		city = city_re.findall(csz)[0].strip()
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()

	#Some of the addresses have a more detailed zip code appended in a parenthetical. This checks for that and extracts it as appropriate.

	paren = paren_re.findall(street)
	if paren:
		if digit_re.findall(paren[0]):
			zip_code = paren[0].strip("()")
		street = street.replace(paren[0],"").strip(", \n/")

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

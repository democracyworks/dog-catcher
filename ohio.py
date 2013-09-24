import urllib
import re
import sys
import dogcatcher
import os
import HTMLParser

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time in testing.)

url = "http://www.sos.state.oh.us/sos/elections/electionsofficials/boeDirectory.aspx"
file_path = cdir + "ohio-clerks.html"

data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()


result = [("authority_name", "first_name", "last_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

source = "State"
voter_state = "OH"

data = open(file_path).read()

county_data_re = re.compile("<td valign=\"top\">(.+?)</td>", re.DOTALL)
county_name_re = re.compile("([^<>]+?) *COUNTY</strong>")

website_re = re.compile("Website:.+?<a href=\"(.+?)\" ", re.DOTALL)
email_re = re.compile("E-mail: *<.+?> *<.+?> *(.+?)</a>", re.DOTALL)
phone_re = re.compile("Telephone.+?(\(.+?) *<br />")
fax_re = re.compile("Fax.+?(\(.+?) *<br />")
hours_re = re.compile("Office Hours: (.+?<br />.*?)Telephone:")
address_re = re.compile("</em><br />(.+?\d{5}[-\d]*?) *<br />", re.DOTALL)

city_re = re.compile("(.+?),")
state_re = re.compile(" [A-Z][A-Z] ")
zip_code_re = re.compile("\d{5}[-\d]*?")

county_data = county_data_re.findall(data)

for county in county_data:

	

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(county)[0].title()
	
	website = dogcatcher.find_website(website_re, county)
	email = dogcatcher.find_emails(email_re, county)

	phone = dogcatcher.find_phone(phone_re, county)
	fax = dogcatcher.find_phone(fax_re, county)

	print "_____________________________"

	print county

	hours = " ".join(hours_re.findall(county)[0].replace("<br />"," ").replace("&amp;","&").split())

	#There are no mailing addresses in the source data; there are only street addreses. The first three lines of code in this section check that and quit if it's changed.

	if "box" in county.lower():
		print "There must be a PO Box in some county. The code wasn't built to handle that. Look into the source data."
		sys.exit()

	address = " ".join(address_re.findall(county)[0].split(" "))
	address = " ".join(address.replace("<br />",", ",address.count("<br />")-1).replace(" ,",",").split())
	address_split = address.partition("<br />")
	street = address_split[0]

	csz = address_split[2]
	city = city_re.findall(csz)[0].strip()
	address_state = state_re.findall(csz)[0].strip()
	zip_code = zip_code_re.findall(csz)[0].strip()

	fips = dogcatcher.find_fips(county_name, voter_state)

	print "*8888888888888888: "
	print [hours]

	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

dogcatcher.output(result, voter_state, cdir)
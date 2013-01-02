import urllib
import re
import sys
import dogcatcher
import HTMLParser

h = HTMLParser.HTMLParser()

#acquiring the FIPs lists that are necessary later

fips_data_re = re.compile(".+?NC.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)


#The following section grabs the website and writes it to a file. (Writing it to a file isn't strictly necessary, but saves some time down the line.)

url = "http://www.ncsbe.gov/content.aspx?id=14"
file_path = "C:\Users\pkoms\Documents\TurboVote\Scraping\\north-carolina-clerks.html"
data = urllib.urlopen(url).read()
output = open(file_path,"w")
output.write(data)
output.close()

result = [("authority_name", "first_name", "last_name", "county_name", "fips"
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

voter_state = "NC"
source = "State"


data = open(file_path).read()

data = data.decode("utf-8").encode("ascii","ignore")

data = h.unescape(data)

data = data.replace("2427 Fayetteville","2427<br />Fayetteville")#.replace("&nbsp;"," ")

county_data_re = re.compile("<tr>.+?<td align=\"middle\">.+?<a href=\"/county/.+?\" (target=\"_blank\">.+?)</tr>", re.DOTALL)
county_data_item_re = re.compile("<td align.+?>(.+?)</td>", re.DOTALL)

county_name_re = re.compile("\"_blank\">(.+?)</a>")

hours_re = re.compile("</a>.+?<br />(.+?)</td>", re.DOTALL)
name_re = re.compile("<td align=\"middle\">([^\d]+?)<br />", re.DOTALL)

phone_re = re.compile("Phone: (.+?)<br />")
fax_re = re.compile("Fax: (.+?)</td>")

email_re = re.compile("<br />\s+([^\s]+?@[^\s]+?)<", re.DOTALL)

middle_name_re = re.compile(" ([a-zA-z]\. )")

city_re = re.compile("(.+?),")
state_re = re.compile(" [A-Z][A-Z] ")
zip_re = re.compile("\d{5}[^\s]*")

if "300 S. Garnett St Henderson" in data:
	data = data.replace("300 S. Garnett St Henderson","300 S. Garnett St <br /> Henderson")
else:
	"This is no longer a useful piece of code. Remove it."
	sys.exit()

county_data = county_data_re.findall(data)
for county in county_data:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_data_item = county_data_item_re.findall(county)
	county_name = county_name_re.findall(county)[0]

	official_name = name_re.findall(county)[0].replace("\r\n","").lstrip()

	first_name, last_name, review = dogcatcher.split_name(official_name, review)
	
	#NC gives two addresses: a mailing address and a street, each formatted "Streeet <br /> City, State Zip". The mailing address may be identical to thes treet address.
	#This gets the address by running a RE to grab each and split it at the "<br />".
	#It then checks whether the mailing and non-mailing addresses are identical. If not

	po_address = " ".join(county_data_item[1].replace("\r\n","").split()).partition("<br />")
	address = " ".join(county_data_item[2].replace("\r\n","").split()).partition("<br />")
	print "__________________________________________________"

	if po_address == address:
		address_state = state_re.findall(address[2])[0].strip()
		city = city_re.findall(address[2])[0].strip()
		zip_code = zip_re.findall(address[2])[0].strip()
		street = address[0].strip()
	else:
		po_street = po_address[0].strip()
		po_city = city_re.findall(po_address[2])[0].strip()
		po_zip_code = zip_re.findall(po_address[2])[0].strip()
		po_state = state_re.findall(po_address[2])[0].strip()
		address_state = state_re.findall(address[2])[0].strip()
		city = city_re.findall(address[2])[0].strip()
		zip_code = zip_re.findall(address[2])[0].strip()
		street = address[0].strip()


	phone = dogcatcher.phone_find(phone_re, county)
	fax = dogcatcher.phone_find(fax_re, county)

	email = dogcatcher.find_emails(email_re, county)
	hours = hours_re.findall(county)[0].strip(" \r\n")


	if "PO Box" not in po_street:
		review = review + "c"

	fips = dogcatcher.fips_find(county_name, fips_names, fips_numbers)

	if fips == "":
		print county_name + " has no findable FIPS. It may be a spellling difference."
		sys.exit()
	
	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city,	po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\\north_carolina.txt", "w")
for r in result:
	s = []
	for item in r:
		s.append(item.encode("ascii", "ignore"))
	output.write("\t".join(s))
	output.write("\n")
output.close()
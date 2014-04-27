import urllib
import re
import sys
import dogcatcher
import HTMLParser
import os

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"


file_path = os.path.join(cdir, "state_list.csv")

jurisdiction_re = re.compile("(<tr><td colspan=\"1\" rowspan=\"1\" class=\"name\">.+?)</table></td></tr>", re.DOTALL)
jurisdiction_data_item_re = re.compile("<td colspan=\"1\" rowspan=\"1\" class=\"(.+?)\"></td>")
jurisdiction_name_re = re.compile("<tr><td colspan=\"1\" rowspan=\"1\" class=\"name\">\s+(.+?)\s+</td>", re.DOTALL)

mailing_address_1_re = re.compile("</td><td colspan=\"1\" rowspan=\"1\" class=\"address\">\s*(.+?\d{5}[-\d]*?)<br clear=\"none\"/><", re.DOTALL)
mailing_address_2_re = re.compile("(.+?)\\n[^<]+?,\\n", re.DOTALL)
po_re = re.compile("([pP][.\s]*[oO][.\s]* .+?)<br clear=\"none\"/>")

city_re = re.compile("\n([^\n]+?),\n\n", re.DOTALL)
address_state_re = re.compile("([A-Z][A-Z]) \d{5}")
zip_code_re = re.compile("[\s]*(\d{5}[-\d]*?)<br ")

phone_re = re.compile("Phone:</td><td colspan=\"1\" rowspan=\"1\">(.+?)</td>")
fax_re = re.compile("Fax:</td><td colspan=\"1\" rowspan=\"1\">(.+?)</td>")

email_re = re.compile("<a shape=\"rect\" href=\"mailto:(.+?)\">")
digit_re = re.compile("\d")

data = open(file_path).read()

state_re = re.compile("(..)")

states = state_re.findall(data)

fvap_url = []

source = "FVAP"

city_result = [("authority_name", "first_name", "last_name", "town_name", "jurisdiction_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

county_result = [("authority_name", "first_name", "last_name", "jurisdiction_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

for i in range(0, len(states)):
	voter_state = states[i]
	fvap_base = "https://www.fvap.gov/r3/jurisdictions/" + voter_state
	doc_base = cdir + voter_state + "_fvap_clerks.html"

	fvap_url.append(fvap_base)
	state_data = urllib.urlopen(fvap_url[i]).read()
	output = open(doc_base,"w")
	output.write(state_data)
	output.close()
	file_path = doc_base

	data = open(file_path).read()

	jurisdiction_data = jurisdiction_re.findall(data)


	#acquiring the FIPs lists that are necessary later
	fips_re_string = ".+?" + voter_state + ".+?\n"
	fips_data_re = re.compile(fips_re_string)
	fips_data = dogcatcher.make_fips_data(fips_data_re)
	fips_numbers = dogcatcher.make_fips_numbers(fips_data)
	fips_names = dogcatcher.make_fips_names(fips_data)

	
	
	for jurisdiction in jurisdiction_data:

		jurisdiction_name = jurisdiction_name_re.findall(jurisdiction)[0]

			#grab & format address
		try:
			mailing_address_stage_1 = mailing_address_1_re.findall(jurisdiction)[0]
			mailing_address = mailing_address_2_re.findall(mailing_address_stage_1)[0]
			#clean up some random known bugs in addresses
			mailing_address = " ".join(mailing_address.replace("<br clear=\"none\"/>","").replace("\n",", ").replace(",, ,",",").replace("v: ","").split()).replace(" ,",",")
		except:
			mailing_address = ""

		try:
			po_street = po_re.findall(jurisdiction)[0].replace("v: ","")
		except:
			po_street = ""


		if not po_street:
			street = mailing_address.replace("v: ","")
		elif digit_re.findall(mailing_address.replace(po_street,"")):
			street = mailing_address.replace(po_street,"")
		else:
			po_street = mailing_address
		street = street.rstrip(",")


		email = dogcatcher.find_emails(email_re, jurisdiction)
		phone = dogcatcher.phone_find(phone_re, jurisdiction)
		fax = dogcatcher.phone_find(fax_re, jurisdiction)

		try:
			city = city_re.findall(jurisdiction)[0].replace("v: ","")
		except:
			city = ""

		zip_code_all = zip_code_re.findall(jurisdiction)
		if len(zip_code_all) == 2:
			zip_code = zip_code_all[1].replace("v: ","")
		elif len(zip_code_all) == 1:
			zip_code = zip_code_all[0].replace("v: ","")
		else:
			zip_code = ""

		try:
			address_state = address_state_re.findall(jurisdiction)[0].replace("v: ","")
		except:
			address_state = ""

		if street and not po_street:
			po_city = ""
			po_state = ""
			po_zip_code = ""
		elif not street:
			po_city = city
			po_state = address_state
			po_zip_code = zip_code
		else:
			po_city = city
			po_state = address_state
			po_zip_code = zip_code


		if voter_state != "MI":
			if " County" in jurisdiction_name or " Parish" in jurisdiction_name or " Island" in jurisdiction_name or " Board of Elections" in jurisdiction_name or " Borough" in jurisdiction_name:
				county_result.append([authority_name, first_name, last_name, jurisdiction_name, fips,
				street, city, address_state, zip_code,
				po_street, po_city,	po_state, po_zip_code,
				reg_authority_name, reg_first, reg_last,
				reg_street, reg_city, reg_state, reg_zip_code,
				reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
				reg_phone, reg_fax, reg_email, reg_website, reg_hours,
				phone, fax, email, website, hours, voter_state, source, review])
			else:
				print jurisdiction_name
				city_result.append([authority_name, first_name, last_name, jurisdiction_name, fips,
				street, city, address_state, zip_code,
				po_street, po_city,	po_state, po_zip_code,
				reg_authority_name, reg_first, reg_last,
				reg_street, reg_city, reg_state, reg_zip_code,
				reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
				reg_phone, reg_fax, reg_email, reg_website, reg_hours,
				phone, fax, email, website, hours, voter_state, source, review])
		else:
			if "(" in jurisdiction_name:
				city_result.append([authority_name, first_name, last_name, jurisdiction_name, fips,
				street, city, address_state, zip_code,
				po_street, po_city,	po_state, po_zip_code,
				reg_authority_name, reg_first, reg_last,
				reg_street, reg_city, reg_state, reg_zip_code,
				reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
				reg_phone, reg_fax, reg_email, reg_website, reg_hours,
				phone, fax, email, website, hours, voter_state, source, review])
			else:
				county_result.append([authority_name, first_name, last_name, jurisdiction_name, fips,
				street, city, address_state, zip_code,
				po_street, po_city,	po_state, po_zip_code,
				reg_authority_name, reg_first, reg_last,
				reg_street, reg_city, reg_state, reg_zip_code,
				reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
				reg_phone, reg_fax, reg_email, reg_website, reg_hours,
				phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to two separate text files: one for counties in the US, and one for cities.

output = open(cdir + "fvap_city.txt", "w")
for c in city_result:
	r = h.unescape(r)
	output.write("\t".join(c))
	output.write("\n")
output.close()


output = open(cdir + "fvap_county.txt", "w")
for c in county_result:
	r = h.unescape(r)
	output.write("\t".join(c))
	output.write("\n")
output.close()
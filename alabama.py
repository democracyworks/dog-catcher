import urllib
import re
import sys
import HTMLParser
import dogcatcher

voter_state = "AL"
source = "State"

h = HTMLParser.HTMLParser()

cdir = os.path.dirname(os.path.abspath(__file__)) + "/"

#acquiring the FIPs lists that are necessary later
fips_data_re = re.compile(".+?AL.+?\n")
fips_data = dogcatcher.make_fips_data(fips_data_re)
fips_numbers = dogcatcher.make_fips_numbers(fips_data)
fips_names = dogcatcher.make_fips_names(fips_data)

result = [("authority_name", "first_name", "last_name", "county_name", "fips",
	"street", "city", "address_state", "zip_code",
	"po_street", "po_city", "po_state", "po_zip_code",
	"reg_authority_name", "reg_first", "reg_last",
	"reg_street", "reg_city", "reg_state", "reg_zip_code",
	"reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
	"reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
	"phone", "fax", "email", "website", "hours", "voter_state", "source", "review")]

#Alabama has two sets of offices; one which handles registrations, and one which handles absentee ballot requests. Each one's data is on a different webpage.
#The following section grabs the websites and writes them to files. (Writing it to a file isn't strictly necessary, but saves some time in testing.)

file_path_1 = cdir + "alabama-clerks-1.html"
file_path_2 = cdir + "alabama-clerks-2.html"
url_1 = "http://www.sos.state.al.us/vb/election/all.aspx?trgtoffice=Board%20of%20Registrars"
url_2 = "http://www.sos.state.al.us/vb/election/all.aspx?trgtoffice=Absentee%20Election%20Manager"


data = urllib.urlopen(url_1).read()
output = open(file_path_1, "w")
output.write(data)
output.close()

data = urllib.urlopen(url_2).read()
output = open(file_path_2, "w")
output.write(data)
output.close()

#All of the counties use Alabama in the address, instead of the more useful "AL."

regdata = open(file_path_1).read().replace(", Alabama",", AL")
regdata = h.unescape(regdata.replace("&nbsp;"," "))
absdata = open(file_path_2).read().replace(", Alabama",", AL")
absdata = h.unescape(absdata.replace("&nbsp;"," "))

absdata = absdata.replace("Evergreen, AL <","Evergreen, AL 34601<").replace("Dekalb","DeKalb").replace("Geneva, AL <","Geneva, AL 36340<")

county_re = re.compile("<tr v[^>]+?>\s+<td width=\"150.+?\d[^>]+?<.+?\(*\d{3}\)*-* *\d{3}-*\d{4}.+?</TD>",re.DOTALL)
middle_re = re.compile("[A-Z]\.* ")
tab_re = re.compile("\t\t+")
city_re = re.compile("(.+?)[A-Z]{2} ")
state_re = re.compile("([A-Z]{2})")
zip_re = re.compile("\d{5}[\d-]*")

phone_re = re.compile("(\d{3}-\d{3}-.+) \s+")

county_name_re = re.compile("<td width=\"150\">(.+?)<")
content_re = re.compile("250\">(.+?) *</td>")

#There are a lot of excessive tabs in the data; I clean them out here to make reading the data easier while working on the code.

for item in tab_re.findall(absdata):
	absdata = absdata.replace(item,"")
for item in tab_re.findall(regdata):
	regdata = regdata.replace(item,"")

#This splits the complete datasets into two lists each containing one item/county. I refer to these as registration (reg) counties and absentee (abs) counties.

county_abs = county_re.findall(absdata)
county_reg = county_re.findall(regdata)

#I cycle through the data one absentee county at a time.

for abse in county_abs:

	authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

	county_name = county_name_re.findall(abse)[0]

	#The county registration offices sometimes have two addresses given; one a street address, and one a PO Box. Each of these forms a different reg county item in the data.
	#This works by comparing the names found in each reg county with the abs county currently being used.
	#If we find a second reg county with the same name, we assign it to be the "other" reg county, and later extract an address from it.

	reg = ""

	for item in county_reg:

		reg_county_name_check = county_name_re.findall(item)[0]
		reg_other = ""

		if reg_county_name_check in county_name and not reg:

			reg = item
			reg_county_name = reg_county_name_check
			continue

		if reg_county_name_check in county_name and reg:

			reg_other = item
			break

	#The authority names are uniform between counties.

	authority_name = "Absentee Election Manager"
	reg_authority_name = "Board of Registrars"

	print abse
	print reg

	abs_content = content_re.findall(abse)

	official_name = abs_content[0]

	first_name, last_name, review = dogcatcher.split_name(official_name, review)

	#This section finds the full address and splits it at its line break. The first half is either a street address or a PO Box; the second half is the city, state, and zip.

    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.
    #It then does the same for the registration office, with the caveat that it checks for an additional registration address (reg_other) first, and turns that into an address as needed.
    #If reg_other does exist, reg always has the PO box, and reg_other is always the street address, so it only checks for reg_other if it first finds a PO box.

	address = abs_content[1].partition("<BR>")
	reg_content = content_re.findall(reg)

	csz = address[2]

	if "PO Box" in address[0]:
		po_street = address[0]
		po_city = city_re.findall(csz)[0].strip(", ")
		po_state = state_re.findall(csz)[0].strip()
		po_zip_code = zip_re.findall(csz)[0].strip()
	else:
		street = address[0]
		city = city_re.findall(csz)[0].strip(", ")
		address_state = state_re.findall(csz)[0].strip()
		zip_code = zip_re.findall(csz)[0].strip()

	reg_address = reg_content[0].partition("<BR>")
	reg_csz = address[2]

	if "PO Box" in address[0]:
		reg_po_street = address[0]
		reg_po_city = city_re.findall(reg_csz)[0].strip(", ")
		reg_po_state = state_re.findall(reg_csz)[0].strip()
		reg_po_zip_code = zip_re.findall(reg_csz)[0].strip()
		if reg_other:
			other_content = content_re.findall(reg_other)
			other_address = other_content[0].partition("<BR>")
			other_csz = other_address[2]
			reg_street = other_address[0]
			reg_city = city_re.findall(other_csz)[0].strip()
			reg_address_state = state_re.findall(other_csz)[0].strip()
			reg_zip_code = zip_re.findall(other_csz)[0].strip()
	else:
		reg_street = address[0]
		reg_city = city_re.findall(reg_csz)[0].strip(", ")
		reg_state = state_re.findall(reg_csz)[0].strip()
		reg_zip_code = zip_re.findall(reg_csz)[0].strip()

	
	phone = dogcatcher.phone_find(phone_re, abse)

	reg_phone = dogcatcher.phone_find(phone_re, reg)

	fips, county_name = dogcatcher.maps_fips(town_name, voter_state, zip_code, fips_names, fips_numbers)


	result.append([authority_name, first_name, last_name, county_name, fips,
	street, city, address_state, zip_code,
	po_street, po_city, po_state, po_zip_code,
	reg_authority_name, reg_first, reg_last,
	reg_street, reg_city, reg_state, reg_zip_code,
	reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
	reg_phone, reg_fax, reg_email, reg_website, reg_hours,
	phone, fax, email, website, hours, voter_state, source, review])

#This outputs the results to a separate text file.

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\\alabama.txt", "w")
for r in result:
	r = h.unescape(r)
    output.write("\t".join(r))
    output.write("\n")
output.close()
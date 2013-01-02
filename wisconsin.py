import urllib
import urllib2
import re
import sys
import xlrd
import dogcatcher
import HTMLParser

h = HTMLParser.HTMLParser()

voter_state = "WI"
source = "State"

result = [("authority_name", "first_name", "last_name", "town_name", "county_name", "fips",
    "street", "city", "address_state", "zip_code",
    "po_street", "po_city", "po_state", "po_zip_code",
    "reg_authority_name", "reg_first", "reg_last",
    "reg_street", "reg_city", "reg_state", "reg_zip_code",
    "reg_po_street", "reg_po_city", "reg_po_state", "reg_po_zip_code",
    "reg_phone", "reg_fax", "reg_email", "reg_website", "reg_hours",
    "phone", "fax", "email", "website", "hours", "voter_state", "source", "review", "town_name_full")]

#Currently I grab the CSV file by hand. At some point, I will need to grab it using mechanize.

filename = "C:\Users\pkoms\Documents\TurboVote\Scraping\wisconsin-xl-clerks.csv"

data = open(filename).read()

data = data.replace("'","^^^^^")
data = data + "\"99999\""


header_re = re.compile("\"Municipality.+")
reports_re = re.compile("\"Suprep.+")

town_data_re = re.compile("[^\n]+\"\d{5}\".+?(?=[^\n]+\"\d{5}\")", re.DOTALL)

fax_re = re.compile("Fax: (\(\d{3}\) [2-90].+?)\"")
phone_re = re.compile("Phone \d: (\(\d{3}\) [2-90].+?)\"")

county_name_re = re.compile("\"([^\"]+?) COUNTY\"")

email_re = re.compile("\"([^\"]+?@.+?)\"")

website_re = re.compile("\"([^\s\"A-Z@]+\.[^\s\"A-Z@]+)\"")

count_re = re.compile("\"\d{5}\"")

address_re = re.compile(",,,\"(.+?,,,)\"Phone \d", re.DOTALL)
csz_re = re.compile(",,,\"(.+ [A-Z]{2} +\d{5}[\d-]*)")
po_re = re.compile("(P[\. ]*O[\. ]* .+?)\"")
city_re = re.compile("(.+?) [A-Z]{2} ")
state_re = re.compile(" ([A-Z]{2}) ")
zip_re = re.compile("\d{5}[\d-]*")

deputy_re = re.compile("[A-Z /,-]*:[ /A-Z,-^']+,.+?\"")

item_re = re.compile("\"(.+?)\"")

#These are the only non-data words, but they aren't clearly identifiable as such in the data. Thus, they need to be removed as the program runs.

for item in header_re.findall(data):
    data = data.replace(item,"")
for item in reports_re.findall(data):
    data = data.replace(item,"")

#counts = ""

    #fixing a series of bad bits of data
data = data.replace("475 \nWAUSAUKEE, WI","475\"\n,,,\"WAUSAUKEE, WI 54177")
    #town = town.replace("\"DEPUTY CLERK: O'BRIEN, COLLEEN  \"","")


town_data = town_data_re.findall(data)

#The towns don't have a completely regular length or format, so identifying particular pieces of data can be messy. For this reason, from the simplest data to the hardest data to identify,
#we identify the data and then clean it using dogcatcher functions, and then get a separate copy to remove it from the full town data.
    
for town in town_data:

    authority_name, first_name, last_name, county_name, town_name, fips, street, city, address_state, zip_code, po_street, po_city, po_state, po_zip_code, reg_authority_name, reg_first, reg_last, reg_street, reg_city, reg_state, reg_zip_code, reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code, reg_phone, reg_fax, reg_email, reg_website, reg_hours, phone, fax, email, website, hours, review = dogcatcher.begin(voter_state)

    town_item = item_re.findall(town)

    town_name_full = town_item[0].title()
    town_name = town_name_full.replace("Town Of ","").replace("Village Of ","").replace("City Of ","")

    #town_item 2 is the name, which is formatted "Clerk: Stein, James J."

    first_name, last_name, authority_name, review = dogcatcher.make_name(town_item[2], ": ", review, "reverse")

    county_name = county_name_re.findall(town)[0].strip().title()
    if county_name == "Fond Du Lac":
        county_name = "Fond du Lac"

    phone = dogcatcher.phone_find(phone_re, town)

    email = dogcatcher.find_emails(email_re, town)
    for item in email_re.findall(town):
        town = town.replace(item,"",1)

    website = dogcatcher.website_find(website_re, town)
    for item in website_re.findall(town):
        town = town.replace(item,"",1)

    fax = dogcatcher.phone_find(fax_re, town)
    
    if county_name == "Wood":
        print "___________________________________________"
        print [town]
        print town_item
        print email

    #This does some additional cleaning of the town before obtaining the address, including removing the town name and every deputy clerk's name.

    town = town.replace(town_name_full.upper(),"",1).replace(" \n","")
    town = town + ",,,\"Phone 1"
    for item in deputy_re.findall(town):
        town = town.replace(item,"",1)

    #This section finds athe address. After finding the address, it identifies a city/state/zip (csz) combination and a PO Box number if that exists.
    #It removes both the CSZ and the PO Address (if it exists) from the full address, leaving behind a street address with some garbage.
    #It then cleans up the street address and pulls the city, state, and zip out of the csz, and assigns them as appropriate to the street address and state.

    address = address_re.findall(town)[0]

    csz = csz_re.findall(town)[0]

    try:
        po_street = po_re.findall(address)[0]
    except:
        po_street = ""

    street = address.replace(csz,"").replace(po_street,"").strip(",\" \n:-")

    if po_street:
        if street:
            city = city_re.findall(csz)[0].strip(",")
            address_state = state_re.findall(csz)[0]
            zip_code = zip_re.findall(csz)[0]
        po_city = city_re.findall(csz)[0].strip().strip(",")
        po_state = state_re.findall(csz)[0].strip()
        po_zip_code = zip_re.findall(csz)[0].strip()
    else:
        city = city_re.findall(csz)[0].strip().strip(",")
        address_state = state_re.findall(csz)[0].strip()
        zip_code = zip_re.findall(csz)[0].strip()

    #counts = counts + count_re.findall(town)[0]

    fips = dogcatcher.fips_find(county_name, voter_state)

    result.append([authority_name, first_name, last_name, town_name, county_name, fips,
    street, city, address_state, zip_code,
    po_street, po_city,	po_state, po_zip_code,
    reg_authority_name, reg_first, reg_last,
    reg_street, reg_city, reg_state, reg_zip_code,
    reg_po_street, reg_po_city, reg_po_state, reg_po_zip_code,
    reg_phone, reg_fax, reg_email, reg_website, reg_hours,
    phone, fax, email, website, hours, voter_state, source, review, town_name_full])

output = open("C:\Users\pkoms\Documents\TurboVote\Scraping\wisconsin.txt", "w")
for r in result:
    r = h.unescape(r)
    output.write("\t".join(r).replace("^^^^^","'"))
    output.write("\n")
output.close()

# print len(count_re.findall(data))
# print len(result)

# for item in count_re.findall(data):
#     if item not in counts:
#         print item
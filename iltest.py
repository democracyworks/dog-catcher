import urllib
import urllib2
import re
import sys
import webbrowser


voter_state = "IL"
source = "State"

file_path = "C:\Users\pkoms\Documents\TurboVote\Scraping\\test-clerks.html"
# method = "POST"
# formdata = "ctl00$ContentPlaceHolder1$ddlCounty": 'All'
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

#req = urllib2.Request(url, formdata, headers)
# data = urllib2.urlopen(req).read()

# output = open(file_path,"w")
# output.write(data)
# output.close()

# result = []

# data = open(file_path).read()

# print data

url = "http://sos.georgia.gov/cgi-bin/countyregistrarsindex.asp"
#data = data.encode('ascii')
#req = urllib.Request(url, data, headers)
data = urllib.urlencode({'CountyName' : 'Appling'})
response = urllib2.urlopen(url, data, headers).read()
webbrowser.open(file_path)
output = open(file_path,"w")
output.write(response)
output.close()
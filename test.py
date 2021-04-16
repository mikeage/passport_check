import mechanicalsoup
import re
import numpy
import time

jerusalem_start = 'https://evisaforms.state.gov/acs/default.asp?postcode=JRS&appcode=1'
telaviv_start = 'https://evisaforms.state.gov/acs/default.asp?postcode=TLV&appcode=1'
appt_dir = 'https://evisaforms.state.gov/acs/'
jerusalem_service = 'chkservice'
jerusalem_service_value = '03' # name is chkservice
jerusalem_read_instructions = 'chkbox01' # name
jerusalem_read_instructions_value = 'on'
ta_service = 'chkservice'
ta_service_value = 'AA'
ta_read_instructions = 'chkbox01' # name
ta_read_instructions_value = 'on'
regular_colors = ['"#ADD9F4"', '"#C0C0C0"', '"#c0c0c0"']


browser = mechanicalsoup.StatefulBrowser()
site = "Jerusalem"
browser.open(jerusalem_start)
input_field = browser.page.find_all('input')[0]
r = re.compile("(make.*)';")
temp = str(input_field['onclick'])
m = r.findall(temp)[0]
browser.open(appt_dir + m)
browser.select_form('form')
browser[jerusalem_service] = jerusalem_service_value
browser[jerusalem_read_instructions] = jerusalem_read_instructions_value

response = browser.submit_selected()
form = browser.select_form()
form.set_select({'nMonth': 7 })
response = browser.submit_selected()

# This response is the current month's calendar of appointments
month = browser.page.find_all('h3')[0].contents[0].replace('\xa0', ' ')

calendar = browser.page.find_all(id="Table3")[0]
c_re = re.compile('<td.*?(\"#.*?\")')
bgcolors = c_re.findall(str(calendar))

c_tr = re.compile('(<tr)')
trs = c_tr.findall(str(calendar))
num_trs = len(trs) - 1 # don't count header row

c_tr2 = re.compile('<tr bgcolor="#ffffc0">\n</tr>')
empty_tr = len(c_tr2.findall(str(calendar))) == 1
adjust = 0
if empty_tr:
    adjust = 1


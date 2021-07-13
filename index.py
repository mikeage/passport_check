# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name
# look for appointments in Israel
# Using mechanicalsoup.readthedocs.io

import datetime
import re
import mechanicalsoup

def check_months(browser, site):
    for m in range(datetime.datetime.today().month + 1, 14):
        r = browser.submit_selected()
        assert r.ok
        month = browser.page.find_all('h3')[0].contents[0].replace('\xa0', ' ')
        found = check_month(browser)
        alert = ""
        if found:
            alert = "  !!!!!!!!!!!!!!!!!!!!!!!"
        print(f"{site}: {month}--{found}{alert}")

        if m <= 12:
            # Get ready for the next month
            form = browser.select_form()
            form.set_select({'nMonth': str(m) })

def check_month(browser):
    found = False

    # id=Table3 is the calendar
    # Find all the td elements. bgcolor #c0c0c0 is grey, date passed/no appt
    # bgcolor #ADD9F4 is blue, full
    # bgcolor #ffffc0 is available appt!!!
    calendar = browser.page.find_all(id="Table3")[0]
    c_re = re.compile('<td.*?(\"#.*?\")')
    bgcolors = [b.upper().replace("'", "").replace('"', '') for b in c_re.findall(str(calendar))]

    # the number of tr elements
    c_tr = re.compile('(<tr)')
    trs = c_tr.findall(str(calendar))
    num_trs = len(trs) - 1 # don't count header row
    c_tr2 = re.compile('<tr bgcolor="#ffffc0">\n</tr>') # an empty tr?
    empty_tr = len(c_tr2.findall(str(calendar))) == 1
    if empty_tr:
        num_trs = num_trs - 1
    # if the number of bgcolors is not number of calendar rows by 7 days 
    if len(bgcolors) != (num_trs * 7):
        found = True
        return found

    unique = list(set(bgcolors))
    for color in unique:
        if color not in regular_colors:
            found = True
    return found

def lookup(browser):
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
    check_months(browser, site)

    site = "Tel Aviv"
    browser.open(telaviv_start)
    input_field = browser.page.find_all('input')[0]
    r = re.compile("(make.*)';")
    temp = str(input_field['onclick'])
    m = r.findall(temp)[0]
    browser.open(appt_dir + m)
    browser.select_form('form')
    browser[ta_service] = ta_service_value
    browser[ta_read_instructions] = ta_read_instructions_value
    check_months(browser, site)

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
regular_colors = ["#ADD9F4", "#C0C0C0"]

def main():
    browser = mechanicalsoup.StatefulBrowser()
    while True:
        lookup(browser)

main()

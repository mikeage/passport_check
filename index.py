# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name
# look for appointments in Israel
# Using mechanicalsoup.readthedocs.io

import datetime
import re
import mechanicalsoup


def check_months(browser, site):
    for m in range(datetime.datetime.today().month + 1, 14):
        r = browser.submit_selected()
        try:
            assert r.ok
        except AssertionError:
            print(r)
            raise
        month = browser.page.find_all('h3')[0].contents[0].replace('\xa0', ' ').strip()
        found = check_month(browser, site, month)
        # print(f"{site}: {month} {found}")

        if m <= 12:  # Get ready for the next month
            form = browser.select_form()
            form.set_select({'nMonth': str(m)})


def check_month(browser, site, month):
    print(f"Checking {site} for {month}")
    found = False

    # id=Table3 is the calendar
    # Find all the td elements. bgcolor #c0c0c0 is grey, date passed/no appt
    # bgcolor #ADD9F4 is blue, full
    # bgcolor #ffffc0 is available appt!!!
    unavailable_colors = ["#ADD9F4", "#C0C0C0"]

    calendar = browser.page.find(id="Table3")

    cur_time = datetime.datetime.now().isoformat()
    for table_row in calendar.select("tr"):
        cells = table_row.findAll('td')
        for cell in cells:
            bgcolor = cell.attrs.get('bgcolor', None)
            if bgcolor and bgcolor.upper() not in unavailable_colors:
                print(f"At {cur_time}, found an appointment at {site} on {month} ({cell.text})")
                found = True
    return found


def lookup(browser):  # pylint: disable=too-many-locals
    jerusalem_start = 'https://evisaforms.state.gov/acs/default.asp?postcode=JRS&appcode=1'
    telaviv_start = 'https://evisaforms.state.gov/acs/default.asp?postcode=TLV&appcode=1'
    appt_dir = 'https://evisaforms.state.gov/acs/'
    jerusalem_service = 'chkservice'
    jerusalem_service_value = '03'  # name is chkservice
    jerusalem_read_instructions = 'chkbox01'  # name
    jerusalem_read_instructions_value = 'on'
    ta_service = 'chkservice'
    ta_service_value = 'AA'
    ta_read_instructions = 'chkbox01'  # name
    ta_read_instructions_value = 'on'

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


def main():
    browser = mechanicalsoup.StatefulBrowser()
    while True:
        lookup(browser)


main()

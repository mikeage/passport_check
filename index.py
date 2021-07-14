# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name
# look for appointments in Israel
# Using mechanicalsoup.readthedocs.io

import datetime
import re
import mechanicalsoup
import telegram_send


def check_site(browser, site):
    browser.open(site["start_url"])
    input_field = browser.page.find_all('input')[0]
    r = re.compile("(make.*)';")
    temp = str(input_field['onclick'])
    m = r.findall(temp)[0]
    browser.open('https://evisaforms.state.gov/acs/' + m)
    browser.select_form('form')
    browser["chkservice"] = site["service_value"]
    browser["chkbox01"] = 'on'

    for m in range(datetime.datetime.today().month + 1, 14):
        r = browser.submit_selected()
        try:
            assert r.ok
        except AssertionError:
            print(r)
            raise
        month = browser.page.find_all('h3')[0].contents[0].replace('\xa0', ' ').strip()
        found = check_month(browser, site["site"], site["type"], month)
        # print(f"{site}: {month} {found}")

        if m <= 12:  # Get ready for the next month
            form = browser.select_form()
            form.set_select({'nMonth': str(m)})


def check_month(browser, site, apt_type, month):
    print(f"Checking {site} for {apt_type} in {month}")
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
                try:
                    split = cell.text.split("Available ")
                    text = f"{split[0]} {month} count: {split[1]}"
                except:  # pylint: disable=bare-except
                    text = f"{month} {cell.text}"
                print(f"At {cur_time}, found an appointment for {apt_type} at {site} on {month} ({cell.text})")
                try:
                    telegram_send.send(messages=[f"Found an appointment in {site}! {text}"])
                except telegram_send.ConfigError:
                    pass
                found = True
    return found


def lookup(browser):  # pylint: disable=too-many-locals
    sites = [
            {
                "site": "Jerusalem",
                "type": "First Passport",
                "start_url": 'https://evisaforms.state.gov/acs/default.asp?postcode=JRS&appcode=1',
                "service_value": "02"
                },
            {
                "site": "Jerusalem",
                "type": "CRBA",
                "start_url": 'https://evisaforms.state.gov/acs/default.asp?postcode=JRS&appcode=1',
                "service_value": "02B"
                },
            {
                "site": "Tel Aviv",
                "type": "All Passport",
                "start_url": 'https://evisaforms.state.gov/acs/default.asp?postcode=TLV&appcode=1',
                "service_value": "AA"
                },
            {
                "site": "Tel Aviv",
                "type": "CRBA",
                "start_url": 'https://evisaforms.state.gov/acs/default.asp?postcode=TLV&appcode=1',
                "service_value": "02B"
                },
            ]

    for site in sites:
        check_site(browser, site)


def main():
    try:
        telegram_send.send(messages=["Starting up!"])
    except telegram_send.ConfigError:
        print("Telegram not configured. Run telegram-send --configure once to get started. Notifications will be disabled")
    browser = mechanicalsoup.StatefulBrowser()
    while True:
        lookup(browser)


main()

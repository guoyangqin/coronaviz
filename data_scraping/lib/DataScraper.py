from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import re
import json
import pandas as pd
import time


class DataScraper:
    def __init__(self, browser='chrome'):
        if browser == 'chrome':
            chrome_options = Options()
            chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})

            # https://stackoverflow.com/a/44771628
            caps = DesiredCapabilities().CHROME
            # caps["pageLoadStrategy"] = "normal"  # complete load
            # caps["pageLoadStrategy"] = "eager"  # interactive
            caps["pageLoadStrategy"] = "none"

            self.driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)
        else:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("javascript.enabled", False)

            caps = DesiredCapabilities().FIREFOX
            # caps["pageLoadStrategy"] = "normal"  # complete load
            caps["pageLoadStrategy"] = "eager"  # interactive
            # caps["pageLoadStrategy"] = "none"

            self.driver = webdriver.Firefox(profile=profile, desired_capabilities=caps)

        self.url_base = 'https://www.worldometers.info/coronavirus/country/%s/'
        self.country = None

    def open_page(self, country):
        self.country = country
        self.country_coded = self.country.lower().replace(' ', '-')

        url = self.url_base % self.country_coded
        self.driver.get(url)

    def css_select_elements(self, css_query):
        elems = self.driver.find_elements_by_css_selector(css_query)

        return elems

    def faster_get_data_from_worldmeters(self):
        # Wait until script is loaded, but before all page is loaded: to save time
        while True:
            try:
                data_df = self.get_data_from_worldmeters()
                break
            except:
                time.sleep(2)
        return data_df

    def get_data_from_worldmeters(self):
        def get_script_text_by(id):
            # Extract script text
            elem_list = self.css_select_elements('script')
            elem_text_list = [e.get_attribute('text') for e in elem_list]

            elem_text = [e for e in elem_text_list if id in e][0]

            # Clean text
            text = elem_text.replace('\n', '').replace('\'', '"').replace(' ', '')
            text = [t for t in text.split('Highcharts.chart') if id in t][0]

            # Find {} data: https://stackoverflow.com/a/15864833
            string = re.search("({.*})", text).group(1)

            # Add quote: https://stackoverflow.com/a/34813280
            string_patched = re.sub('([{,:])(\w+)([},:])', '\\1\"\\2\"\\3', string)

            # Convert to json
            d = json.loads(string_patched)

            # Extract date and case number
            date_list = d['xAxis']['categories']
            data_list = d['series'][0]['data']
            data_list = [int(d) for d in data_list]

            return date_list, data_list

        date_list, cases_list = get_script_text_by('coronavirus-cases-linear')
        _, deaths_list = get_script_text_by('coronavirus-deaths-linear')

        data_df = pd.DataFrame(date_list, columns=['date'])
        data_df.date = '2020' + data_df.date
        data_df.date = pd.to_datetime(data_df.date, format='%Y%b%d').map(lambda x: x.strftime("%Y%m%d"))

        data_df['cum_cases'] = cases_list
        data_df['cum_deaths'] = deaths_list

        data_df['new_cases'] = data_df['cum_cases'].diff()
        data_df['new_deaths'] = data_df['cum_deaths'].diff()

        nan_ind = data_df['new_cases'].isnull()
        data_df.loc[nan_ind, 'new_cases'] = data_df.loc[nan_ind, 'cum_cases']
        data_df.new_cases = data_df.new_cases.astype(int)

        nan_ind = data_df['new_deaths'].isnull()
        data_df.loc[nan_ind, 'new_deaths'] = data_df.loc[nan_ind, 'cum_deaths']
        data_df.new_deaths = data_df.new_deaths.astype(int)

        data_df['country'] = self.country

        return data_df

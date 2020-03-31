from lib.DataScraper import DataScraper
import pandas as pd
import time


def extract_case_data_by_country(country_list):
    # Initiate a browser instance
    start = time.time()
    ds = DataScraper()

    # Extract data
    result = pd.DataFrame()
    for country in country_list:
        print('[%dsec] Extracting %s\'s COVID-19 case data...' % ((time.time() - start), country))
        ds.open_page(country)
        data_df = ds.faster_get_data_from_worldmeters()

        result = pd.concat([result, data_df], ignore_index=True)

    print('[%dsec] Completed...' % (time.time() - start))

    # Export data
    result.to_csv('export/covid19_case_data_lastest.csv', index=False)

    return result

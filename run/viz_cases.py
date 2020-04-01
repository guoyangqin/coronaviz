from viz.lib.plot_figure import plot_figure
from data_scraping.lib.extract_case_data_by_country import extract_case_data_by_country
from data_scraping.config.country_list import country_list

# Extract data and export
result = extract_case_data_by_country(country_list)

# Plot figure
plot_figure()

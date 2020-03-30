import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plt.rcParams['font.family'] = "arial"
plt.rcParams['svg.fonttype'] = 'none'

data_dir = '../data_scraping/export/covid19_case_data_20200330.csv'
data = pd.read_csv(data_dir)
num_cases_pivot = pd.pivot_table(data, values='new_cases', index=['date'], columns=['country']).fillna(0)
num_deaths_pivot = pd.pivot_table(data, values='new_deaths', index=['date'], columns=['country']).fillna(0)

# Get latest cum_cases for each country
cum_cases = data.groupby('country')['cum_cases'].max().reset_index()
cum_cases = cum_cases.sort_values(by='cum_cases', ascending=False).reset_index(drop=True)
max_num_new_cases = np.max(data.new_cases)

top_num = 12
country_selected = cum_cases[:top_num].country.values
data = data[data.country.isin(country_selected)]

cum_deaths = data.groupby('country')['cum_deaths'].max().reset_index()
cum_deaths = cum_deaths.sort_values(by='cum_deaths', ascending=False).reset_index(drop=True)
max_num_new_deaths = np.max(data.new_deaths)

data['fatality_rate'] = data.cum_deaths / data.cum_cases
data['fatality_rate'] = data['fatality_rate'].fillna(0)
fatality_rate = data.groupby('country', group_keys=False)['fatality_rate'].agg('last').reset_index()
fatality_rate = fatality_rate.sort_values(by='fatality_rate', ascending=False).reset_index(drop=True)

max_fatality_rate = np.max(data.fatality_rate)

figure1, axes1 = plt.subplots(top_num, 1, figsize=(8, 14), sharey=True)
figure2, axes2 = plt.subplots(top_num, 1, figsize=(8, 14), sharey=True)
figure3, axes3 = plt.subplots(top_num, 1, figsize=(8, 14), sharey=True)

figure1.subplots_adjust(left=0.05, bottom=0.06, right=0.95, top=0.98, wspace=0, hspace=0.25)
figure2.subplots_adjust(left=0.05, bottom=0.06, right=0.95, top=0.98, wspace=0, hspace=0.25)
figure3.subplots_adjust(left=0.05, bottom=0.06, right=0.95, top=0.98, wspace=0, hspace=0.25)

axes1 = axes1.T.flatten()
axes2 = axes2.T.flatten()
axes3 = axes3.T.flatten()

scale = 1000
current_date = data.date.max()
date_range = np.sort(data.date.unique())

data_source = 'www.worldometers.info/coronavirus/'

for i in range(top_num):
    cases_country = cum_cases.country[i]
    deaths_country = cum_deaths.country[i]
    fatality_rate_country = fatality_rate.country[i]

    sub_num_cases = num_cases_pivot[cases_country].reset_index()
    total_cases1 = cum_cases[cum_cases.country == cases_country].cum_cases.values[0]
    total_deaths1 = cum_deaths[cum_deaths.country == cases_country].cum_deaths.values[0]

    sub_num_deaths = num_deaths_pivot[deaths_country].reset_index()
    total_cases2 = cum_cases[cum_cases.country == deaths_country].cum_cases.values[0]
    total_deaths2 = cum_deaths[cum_deaths.country == deaths_country].cum_deaths.values[0]

    sub_num_cases1 = num_cases_pivot[fatality_rate_country].reset_index()
    total_cases3 = cum_cases[cum_cases.country == fatality_rate_country].cum_cases.values[0]
    sub_num_deaths1 = num_deaths_pivot[fatality_rate_country].reset_index()
    total_deaths3 = cum_deaths[cum_deaths.country == fatality_rate_country].cum_deaths.values[0]
    sub_fatality_rate = sub_num_cases.copy()
    sub_fatality_rate[fatality_rate_country] = (
            sub_num_deaths1[fatality_rate_country].cumsum() / sub_num_cases1[fatality_rate_country].cumsum()).values

    sub_fatality_rate[fatality_rate_country] = sub_fatality_rate[fatality_rate_country].fillna(0)

    ax1, ax2, ax3 = axes1[i], axes2[i], axes3[i]

    ax1.tick_params(labelright=True)
    ax2.tick_params(labelright=True)
    ax3.tick_params(labelright=True)

    if i == 0:
        ax1.set_title('Number of new cases (x%d) per day by country (%d)' % (scale, current_date))
        ax2.set_title('Number of new deaths per day by country (%d)' % current_date)
        ax3.set_title('Fatality rate (%%) per day by country (%d)' % current_date)

    # Bar plot
    ax1 = sns.barplot(x='date', y=cases_country, data=sub_num_cases, color="salmon", saturation=1, zorder=999, ax=ax1)
    ax2 = sns.barplot(x='date', y=deaths_country, data=sub_num_deaths, color="#333333", saturation=1, zorder=999,
                      ax=ax2)
    ax3.stackplot(sub_fatality_rate.index, sub_fatality_rate[fatality_rate_country], color="#999999", zorder=999)

    # === Set params ===
    # 1. Off labels
    if i == (top_num - 1):
        xlabel = 'Date\n Data source: %s' % data_source
        ax1.set_xlabel(xlabel)
        ax2.set_xlabel(xlabel)
        ax3.set_xlabel(xlabel)
    else:
        ax1.set_xlabel('')
        ax2.set_xlabel('')
        ax3.set_xlabel('')

    ax1.set_ylabel('')
    ax2.set_ylabel('')
    ax3.set_ylabel('')

    # 2. Set ticklabels
    label = np.arange(20200101, current_date, 100)
    label = np.append(label, current_date)
    ticklabel_list = list(ax1.get_xticklabels())
    texts = np.array([[i, int(xtl._text)] for i, xtl in enumerate(ticklabel_list) if int(xtl._text) in label])

    ax1.set_xticks(texts[:, 0])
    ax1.set_xticklabels(texts[:, 1], ha='right')
    ax2.set_xticks(texts[:, 0])
    ax2.set_xticklabels(texts[:, 1], ha='right')
    ax3.set_xticks(texts[:, 0])
    ax3.set_xticklabels(texts[:, 1], ha='right')
    ax3.set_xlim(0, sub_fatality_rate.index[-1])

    gap = 4000
    label1 = np.arange(gap, max_num_new_cases, gap)
    ax1.set_yticks(label1)
    ax1.set_yticklabels(np.int_(label1 / scale))
    ax1.set_ylim(0, max_num_new_cases)

    gap = 200
    label2 = np.arange(gap, max_num_new_deaths, gap)
    ax2.set_yticks(label2)
    ax2.set_yticklabels(np.int_(label2))
    ax2.set_ylim(0, max_num_new_deaths)

    max_fatality_rate = 0.15
    gap = 0.02
    label3 = np.arange(gap, max_fatality_rate, gap)
    ax3.set_yticks(label3)
    ax3.set_yticklabels(np.int_(label3 * 100))
    ax3.set_ylim(0, max_fatality_rate)

    ax1.grid(color='#cccccc', zorder=1)
    ax2.grid(color='#cccccc', zorder=1)
    ax3.grid(color='#cccccc', zorder=1)

    ax1.text(int(len(ticklabel_list) / 2), max_num_new_cases * 0.9,
             '%s\n%d cases, %d deaths (%0.2f%%)' % (
                 cases_country, total_cases1, total_deaths1, (total_deaths1 / total_cases1 * 100)),
             bbox=dict(facecolor='w', alpha=0.5, edgecolor='none'),
             ha='center', va='top', zorder=9999)

    ax2.text(int(len(ticklabel_list) / 2), max_num_new_deaths * 0.9,
             '%s\n%d cases, %d deaths (%0.2f%%)' % (
                 deaths_country, total_cases2, total_deaths2, (total_deaths2 / total_cases2 * 100)),
             bbox=dict(facecolor='w', alpha=0.5, edgecolor='none'),
             ha='center', va='top', zorder=9999)

    ax3.text(int(len(ticklabel_list) / 2), max_fatality_rate * 0.9,
             '%s\n%d cases, %d deaths (%0.2f%%)' % (
                 fatality_rate_country, total_cases3, total_deaths3, (total_deaths3 / total_cases3 * 100)),
             bbox=dict(facecolor='w', alpha=0.5, edgecolor='none'),
             ha='center', va='top', zorder=9999)

# Save figures
figure1.savefig('figures/num_cases_%d.pdf' % current_date, transparent=True)
figure2.savefig('figures/num_deaths_%d.pdf' % current_date, transparent=True)
figure3.savefig('figures/fatality_rate_%d.pdf' % current_date, transparent=True)

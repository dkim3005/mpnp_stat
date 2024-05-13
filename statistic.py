import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt

def month_to_number(df):
    month_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                  "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    df['Month'] = df['Month'].map(month_dict)
    return df

def plot_yearly_trends(df, section_name):
    df = month_to_number(df)

    for year in df['Year'].unique():
        yearly_data = df[df['Year'] == year]

        fig, ax = plt.subplots()
        for column_name in yearly_data.columns.drop(['Year', 'Month']):
            ax.plot(yearly_data['Month'], yearly_data[column_name], label=column_name)

        ax.set_title(f'{year} {section_name} Monthly Trends')
        ax.set_xlabel('Month')
        ax.set_ylabel('Data Value')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax.legend()

        plt.savefig(f'{section_name.replace(" ", "_").lower()}_{year}_monthly_trends.png')
        plt.close()

lst = ["https://immigratemanitoba.com/data/monthly-data-2020/",
       "https://immigratemanitoba.com/data/monthly-data-2021/",
       "https://immigratemanitoba.com/data/monthly-data-2022/",
       "https://immigratemanitoba.com/data/monthly-data-2023/",
       "https://immigratemanitoba.com/data/monthly-data-2024/"]

required_columns = ['Year', 'SW', 'In Assessment', 'Pending', 'SW Nominations']

all_data = {}

headers = {"User-Agent": "Mozilla/5.0"}

for link in lst:
    year = re.findall(r'\d{4}', link)[0]

    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    sections = ["Nominations and approvals", "Applications received",
                "Applications in assessment and pending assessment"]
    for section in sections:
        section_heading = soup.find(string=section)
        if section_heading:
            section_table = section_heading.find_next("table")
            if section_table:
                df = pd.read_html(str(section_table), header=0)[0]
                df['Year'] = year
                df['Section'] = section
                available_columns = [col for col in ['Month', 'Total'] + required_columns if col in df.columns]
                df = df[available_columns]
                if section not in all_data:
                    all_data[section] = df
                else:
                    all_data[section] = pd.concat([all_data[section], df], ignore_index=True)

for section, df in all_data.items():
    cleaned_section_name = section.replace(" ", "_").lower()
    df.to_csv(f'output_{cleaned_section_name}_with_month.csv', index=False, encoding='utf-8-sig')
    df.to_excel(f'output_{cleaned_section_name}_with_month.xlsx', index=False)

    plot_yearly_trends(df, section)

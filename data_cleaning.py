import pandas as pd
import numpy as np
import io
import os
from bs4 import BeautifulSoup

ABS_DIR = os.path.realpath('.')
ABS_DIR = '/Users/aurelien/capstone'
def get_path(file_name):
    return os.path.join(ABS_DIR, 'data', file_name)

# # To be fixed : doubles codes postaux et valeurs NaN dans income

# # Import the data
# ### candidates
# First we create a dataframe  **`candidates`**  with the list of candidates

f = io.open(get_path('list_candidates.xml'), encoding='utf-8')
soup = BeautifulSoup(f, features='xml')
cand_list = soup.find_all('Candidat')
candidates = []

for c in cand_list:
    temp_dict = {}
    temp_dict['cand_id'] = c.find_all('NumPanneauCand')[0].text
    temp_dict['last_name'] = c.find_all('NomPsn')[0].text
    temp_dict['first_name'] = c.find_all('PrenomPsn')[0].text
    temp_dict['civilite'] = c.find_all('CivilitePsn')[0].text
    candidates.append(temp_dict)
f.close()
candidates = pd.DataFrame(candidates)

candidates
# ### election results
# We then build the dataframe  **`results`**  containing all the elections results

header = ['dpt_code','dpt_name','circo_code','circo_name','city_code','city_name','poll_station',
          'registered','abst','abst_perc','voting','voting_perc','white','white_perc_ins','white_perc_vot',
          'nullv', 'nullv_perc_ins', 'nullv_perc_vot','valid','valid_perc_ins','valid_perc_vot'
         ]

def pattern(i):
    tmp = ['cand_id','sex','last_name','first_name','votes','perc_ins','perc_exp']
    for j in range(len(tmp)):
        tmp[j] = str(i) + '_' + tmp[j]
    return tmp

for i in range(1,len(candidates)+1):
    header.extend(pattern(i))


results = pd.read_csv(get_path('results_pres_election.txt'),
        sep=';',
        encoding='iso-8859-1',
        header=0,
        names = header,
        dtype={'dpt_code': 'str', 'city_code':'str'}
        )


# We create a smaller dataframe  **`df`**  with the interesting columns

colums_to_keep = results.columns[[list(range(0,9)) + [10] + [12] + [15] + [18] + list(range(25,98,7))]]
df = results[colums_to_keep]


# ### income data
# we create a dataframe  **`income`**  with income data by city


income = pd.read_excel(get_path('income_by_city.xls'), skiprows=4)
income_dict = {}
for col in income.columns.values:
    income_dict[income[col][0]] = col

income = pd.read_excel(get_path('income_by_city.xls'), skiprows=5)

print(income.head(2))



print(income['MED13'].isnull())


# ### table from insee code to zipcode

insee_to_zip = pd.read_csv(get_path('insee_to_zipcode.csv'), sep=';', dtype='str')
print(insee_to_zip.head(3))


# # Cleaning the data

sorted(list(set(df['dpt_code'].values)))[-7:]
results_abroad_idx = df['dpt_code'].isin(sorted(list(set(df['dpt_code'].values)))[-7:])
results_abroad = df[results_abroad_idx]
df = df[~results_abroad_idx]


df['dpt_code'].replace('Z.',u'97', regex=True, inplace=True)
temp = df['dpt_code'] + df['city_code']
df.loc[:,'insee_code'] = temp
df = pd.merge(df, insee_to_zip[['insee_com','postal_code']], how='left', left_on='insee_code', right_on='insee_com')


# List of insee codes which map to several zip code (will have to be fixed)

list(set(df[df['postal_code'].str.len() > 5]['postal_code']))


df[df['city_code'].str.len() != 3]


# # Groupby test

f = {'dpt_name': lambda x: list(set(x))[0],
     'registered':['sum'], 'abst':['sum'], 'voting':['sum'], 'white':['sum'],
     'nullv':['sum'], 'valid':['sum'], '1_votes':['sum'], '2_votes':['sum'], '3_votes':['sum'],
     '4_votes':['sum'], '5_votes':['sum'], '6_votes':['sum'], '7_votes':['sum'], '8_votes':['sum'],
     '9_votes':['sum'], '10_votes':['sum'], '11_votes':['sum']}


votes_by_dpt = df.groupby('dpt_code').agg(f)


votes_by_dpt.head(3)

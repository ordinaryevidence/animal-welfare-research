"""Build data/aquaculture_quantity.csv from a FAO FishStat aquaculture release.

Download and unzip a release from https://www.fao.org/fishery/en/collection/aquaculture
(e.g. Aquaculture_2026.1.0.zip), then run:

    uv run python aquaculture.py path/to/unzipped/release
"""

import sys
from pathlib import Path

import pandas as pd

ISSCAAP_GROUPS = [
    'Carps, barbels and other cyprinids',
    'Cods, hakes, haddocks',
    'Flounders, halibuts, soles',
    'Herrings, sardines, anchovies',
    'Marine fishes not identified',
    'Miscellaneous coastal fishes',
    'Miscellaneous demersal fishes',
    'Miscellaneous diadromous fishes',
    'Miscellaneous freshwater fishes',
    'Miscellaneous pelagic fishes',
    'Salmons, trouts, smelts',
    'Shrimps, prawns',
    'Sturgeons, paddlefishes',
    'Tilapias and other cichlids',
    'Tunas, bonitos, billfishes',
]

src = Path(sys.argv[1])
quantity = pd.read_csv(src / 'Aquaculture_Quantity.csv')
species = pd.read_csv(src / 'CL_FI_SPECIES_GROUPS.csv',
                      usecols=['3A_Code', 'ISSCAAP_Group_En'])
countries = pd.read_csv(src / 'CL_FI_COUNTRY_GROUPS.csv',
                        usecols=['UN_Code', 'Name_En'])

df = (quantity[quantity['MEASURE'] == 'Q_tlw']
      .merge(species, left_on='SPECIES.ALPHA_3_CODE', right_on='3A_Code')
      .merge(countries, left_on='COUNTRY.UN_CODE', right_on='UN_Code'))
df = df[df['ISSCAAP_Group_En'].isin(ISSCAAP_GROUPS)]

wide = df.pivot_table(index=['Name_En', 'ISSCAAP_Group_En'], columns='PERIOD',
                      values='VALUE', aggfunc='sum')
wide = wide[sorted(wide.columns, reverse=True)]
wide.columns = [f'{year} value' for year in wide.columns]
wide.index.names = ['Country Name En', 'ISSCAAP group Name En']
wide.insert(0, 'Unit Name', 'Tonnes - live weight')
wide.to_csv('data/aquaculture_quantity.csv')

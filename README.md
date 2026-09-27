# Animal Welfare Dashboard

A [Streamlit app](app.py) that estimates net global welfare of farmed animals over time and summarizes grants from major farm animal welfare funders.

```bash
uv run streamlit run app.py
```

## Net global welfare

Total welfare for each species is population × welfare range × welfare value. Welfare ranges come from [Rethink Priorities](https://rethinkpriorities.org/publications/welfare-range-estimates); welfare values are rough judgments. Both live in `data/welfare-params.csv` and can be adjusted in the app.

`net-global-welfare.ipynb` builds `data/population.csv` (country × year, 1961–2024) from:

- **Land animals**: FAOSTAT [Crops and livestock products](https://www.fao.org/faostat/en/#data/QCL) stocks of cattle, chickens, ducks, goats, pigs and sheep (`data/FAOSTAT_data_en_*.csv`).
- **Farmed fish and shrimp**: FAO FishStat [aquaculture production](https://www.fao.org/fishery/en/collection/aquaculture) in tonnes, converted to a standing population using average weight and lifespan from [fishcount.org.uk](https://fishcount.org.uk/) (`data/aqua-params.csv`). `aquaculture.py` builds `data/aquaculture_quantity.csv` from a FishStat release zip.

## Grants

Grant data lives in the "Animal Welfare Grants" Google Sheet, with one tab per source and an "All" tab that combines them:

- **Coefficient Giving** (formerly Open Philanthropy): the [Farm Animal Welfare](https://coefficientgiving.org/funds/farm-animal-welfare/) grants database.
- **Animal Welfare Fund**: EA Funds [grants](https://funds.effectivealtruism.org/grants) from the Animal Welfare Fund.
- **Animal Charity Evaluators**: [Movement Grants](https://animalcharityevaluators.org/movement-grants/past-movement-grants-recipients/) and [Recommended Charity Fund](https://animalcharityevaluators.org/donate/donor-resources/recommended-charity-fund/past-distributions/) distributions.

To update, export the "All" tab to `data/Animal Welfare Grants - All.csv` and run the first three cells of `grants-analysis.ipynb` to write `data/grants.csv`, then update the "Last updated" caption in `app.py`. The current year is partial.

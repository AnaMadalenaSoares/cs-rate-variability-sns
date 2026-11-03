# Caesarean Section Rate Variation across Portuguese National Health Service Units: An LLM-Assisted Analysis

Supporting data, analysis scripts, results and prompts for the MSc dissertation in Industrial Engineering and Management at Instituto Superior Técnico, Universidade de Lisboa.

- **Author:** Ana Madalena Silva de Oliveira Soares
- **Supervisor:** Prof. Miguel Pereira
- **Year:** 2026
- **Repository:** https://github.com/AnaMadalenaSoares/cs-rate-variability-sns

## About the study

This repository accompanies a longitudinal, observational study of caesarean section (CS) rate variability across 37 public hospital units of the Portuguese National Health Service (SNS) in mainland Portugal, analysed at the unit-year level from 2013 to 2025. The analysis follows a logic of successive exclusion: it describes how much of the variability in CS rates remains once units are compared with others that share the same characteristics (hospital level, management sector, region and delivery volume), and then examines area-level and contextual indicators. A longitudinal analysis of delivery volume and CS rates within units over time, with unit and year fixed effects, complements the descriptive analysis.

The data analysis was conducted with the support of a large language model, Claude Opus 5.5 (Anthropic), guided by a structured prompt and organised into sequential phases. All calculations were performed in Python code generated and executed by the model. The scripts were retained so that the results can be reproduced outside the LLM.

## Repository structure

```
README.md                          This file
requirements.txt                   Python packages required
LICENSE                            Licence terms
scripts_analise_CS/                Phased analysis
├── LEIA-ME.md                     Detailed description of each script and source file (in Portuguese)
├── correr_tudo.py                 Runs all scripts in the order used in the analysis
├── f0_auxiliares.py … fxl.py      Analysis scripts, one or more per phase
├── f13_longitudinal.py            Longitudinal analysis (run separately)
├── dados/                         The 16 source files (3 correspondence tables, the hospital
│                                  workbook and 12 PORDATA files)
├── dados_intermedios/             Auxiliary files in readable form (CSV and JSON)
└── w/                             Outputs (created when the scripts are run)
results/
└── Resultados finais - análise CS (validado).xlsx
                                   Validated results workbook: one sheet per phase, the harmonised
                                   unit-year database, exclusions, the decision log and the list of
                                   cells changed in the final validation
longitudinal_analysis/
└── results/                       Outputs of the longitudinal analysis (CSV)
prompts/
└── prompt_analise_taxas_CS.md     Structured prompt used in the phased analysis (in Portuguese)
supplementary/
└── Supplementary_Material.pdf     Supplementary tables, figures and prompts
```

## Hospital codes

Units are identified by codes A01–A37. The codes are used to simplify the analysis, not for anonymisation; the correspondence between each code and the name of the unit is given in the Annex of the dissertation and in the correspondence tables in `scripts_analise_CS/dados/`. Codes A38–A40 appear in the source data but record no births and are not part of the study.

## Data sources

All data are aggregated at unit, municipal, regional or national level and come from publicly available sources:

- **SNS Transparência** – monthly cumulative births and caesarean sections by unit (`Excel_1_-_hospitais.xlsx`, sheet "SNS transparência"; the column without a header contains the researcher's notes on data anomalies)
- **PORDATA** – municipal, regional and national indicators on population, health workforce and health services (12 files, sheet "Quadro"; other sheets are working sheets and are not used)
- **Correspondence tables** – built by the author from primary legal sources (Diário da República, including Decreto-Lei n.º 102/2023), linking former hospital designations, ULS, regions and municipalities to the unit codes

No individual patient data are included in this repository. The complete list of source files and the scripts that use each of them is given in `scripts_analise_CS/LEIA-ME.md` and in Table S4 of the Supplementary Material.

## How to reproduce the phased analysis

1. Download or clone this repository.
2. Install Python 3 and the required packages:
   ```
   pip install -r requirements.txt
   ```
3. In the `scripts_analise_CS` folder, run:
   ```
   python correr_tudo.py
   ```
   The scripts run in the order used in the analysis. Calculation outputs (`out*.md`) and figures are written to `w/`, and the results workbook `Resultados finais - análise CS.xlsx` is written to the `scripts_analise_CS` folder.

Run from scratch on the source files, the scripts reproduce the calculation outputs of all phases. The workbook they produce is the version before the final validation; the corrections made during the validation were applied afterwards, cell by cell, and are listed in the sheet "Validação – alterações" of the validated workbook in `results/`. The manual data preparation steps that precede the scripts are described in the dissertation.

## Longitudinal analysis

The longitudinal analysis was carried out separately from the phased analysis, with a separate prompt (reproduced in the Supplementary Material). The script is `scripts_analise_CS/f13_longitudinal.py`. It reads only the hospital workbook and is not run by `correr_tudo.py`. To reproduce it, run in the `scripts_analise_CS` folder:

```
python f13_longitudinal.py
```

The outputs are written to `w/`. The outputs of the run reported in the dissertation are in `longitudinal_analysis/results/`: the annual panel (`f13_painel_anual.csv`), the estimates of the main and sensitivity specifications (`f13_resultados.csv`) and the auxiliary tables on excluded units, excluded unit-years, data completeness and implausible monthly values.

## Prompts

The structured prompt used in the phased analysis is in `prompts/`, in the original Portuguese. Both prompts, including the one used in the longitudinal analysis, are also reproduced in the Supplementary Material.

## Citation

> Soares, A. M. S. O. (2026). *Caesarean Section Rate Variation across Portuguese National Health Service Units: An LLM-Assisted Analysis*. MSc dissertation, Instituto Superior Técnico, Universidade de Lisboa.

## Licence

Code is released under the MIT Licence. Documentation, results and the correspondence tables are released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0). The source data from SNS Transparência and PORDATA remain subject to the terms of use of the original sources.

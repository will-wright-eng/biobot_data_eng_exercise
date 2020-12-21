# Data Engineering Exercise for Biobot

![biobot](https://github.com/william-cass-wright/biobot_data_eng_exercise/blob/master/images/logo.png)

## Table of Contents

- [Responses](README.md#responses)
- [Instructions](README.md#instructions)
- [References](README.md#references)

## Responses

1. Write a Python function to parse the provided Excel template into a pandas dataframe.

```python
def excel_to_rep_df(filename):
	'''excel_to_rep_df docstring
	generate single dataframe from replicate sheets'''
    xl = pd.ExcelFile(filename)
    sheets = list(xl.sheet_names)
    rep_sheets = [i for i in sheets if 'rep' in i]
    dfs = []
    expected_shape = (96, 8)

    for sheet in rep_sheets:
        df = xl.parse(sheet)
        try:
            assert df.shape == expected_shape
        except AssertionError as e:
            print(e,'\n Excel sheet {} in {} was an unexpected shape'.format(sheet,filename))
            break

        df = df[[i for i in df.columns if 'Unnamed' not in i]]
        df['total_copies'] = df.Cq.apply(lambda x: std_curve_conversion(sheet,x))
        df['sheet'] = sheet
        dfs.append(df)

    ndf = pd.concat(dfs)
    return xl, ndf, sheets
```

2. Write skeleton Python code to convert the Ct values into sewage concentration.

```python
def main():
    filename = 'sample_data.xlsx'
    xl, ndf, sheets = excel_to_rep_df(filename)
    df = gen_info_df(xl,sheets) 
    ndf = ndf.merge(df,on='Well',how='left')
    ndf['sewage_conc'] = ndf.apply(lambda x: sewage_conc_conversion(x), axis=1)
    save_results(ndf,filename)
```

3. Describe the tools and technologies you will use to ingest the lab data into the pipeline and store it into a cloud-hosted database. 

### Extract
- Ideally the instrument software has an API and webhooks with well documented endpoints for extracting testing data. I haven't been in a lab in a few years but I think it's safe to say this is not an ideal assumption. The next best thing would be a LIMS that fits this criteria of API, webhooks, and documentation. If this is the case then the extraction process is building a vehicle for communicating with the instrument in a programatic way either via scheduled HTTP calls or with a simple webhook listener.
- Since I'm most familar with python this is the language I would use for such a step. 

### Transform
- The transformation step of this process is covered in the rest of the exercise. Assuming that the data provided is representative of what was extracted then pandas would be sufficient.
- A few things I would add given more time:
	- replace print statements with logging
	- parameterize things like column and file names
	- make executable via bash script
	- add edge case testing to account for expected variability in lab data
	- orgaize code into class with OOP naming conventions

### Load
- Since the lab data will need to be used in reporting, monitoring, and studies it's ideal that it be accessable through a database. This could be in the form of an OLAP database such as BigQuery, Snowflake, or Redshift. These options are ideal for scaling reporting and analytics via SQL however other options such as a managed Postgres database might be a better option if a compute cluster and query optimization, such as those offered by the three OLAP DBs, isn't needed.

### Workflow
- Other elements of the data pipeline would include scheduling and model execution through tools like Airflow or dbt (data build tool) respectively. 

4. How will you ensure that the Excel template has the correct format?
- One could check formatting by checking that the column headers are equivalent to, such as the assertion on line 78, but this does not take into account spelling errors or cells that aren't in the expected postion for the `read_csv` method. 

5. What data QC analyses will you pursue or build? How will you provide visibility into data QC for the team? What will happen if a sample on a qPCR plate or an entire qPCR plate fails QC?
- Looking at the data in aggregate you could use anomoly detection methods or more simply a box plot where anything in the first or fourth quartile is flagged for additional inspection.
- More than the data itself, you could monitor metadata on the files and the database in order to derive latency and completness metrics and thereby trust in the pipeline. 

6. What constraints do you expect to face? How will you balance trade-offs between ensuring reliable, robust data ingestion and QC but enabling automated and quick processing times?
- Since latency isn't an issue then reliability and robustness through redundancy is the preferred option. 

7. How will you implement the process of updating the standard curve each week into your pipeline and script?
- Equation coefficients can be called from a key-value store. The key-value for each coefficient can be updated via a schedule or event trigger.

8. How can you expand the base pipeline for Covid-19 to include other qPCR targets such as influenza A and B?
- If the additional targets adhere to the same standards and calcutions then the tests could easily be added to the program. If test set varies between customers and accross time then it would be efficient to parameterize the tests and associated calculations.

9. How do you collaborate with the lab team and other engineers to build the pipeline? (Some key areas to explore are methods of communication between and within teams, visibility on requirements, working together on the same repository)
- Methods of Communication: daily or weekly standup meetings, clear priorities, and project boundries
- Visibility on Requirements: documentation on company wiki
- Working Repo: use of templates for issues and commits along with good testing practices prior to merging to production


## Instructions
```
Take-home exercise:

1. Write a Python function to parse the provided Excel template into a pandas dataframe.
a. Apart from the “sample layout” sheet, the sheets are labeled like: “<primer> rep<primer replicate>”. The lab sometimes includes additional sheets with
notes or intermediate work. These sheets can be ignored.

2. Write skeleton Python code to convert the Ct values into sewage concentration.
a. Our current standard curve is: y = -0.3068*x + 12.506 for N1 and y = -0.2876*x + 11.912 for N2, where x is the Ct call and y is log10(total copies). We use the N1 standard curve to get relative quantification for PMMV.
b. We convert total copies to sewage concentration by multiplying by the dilution factor provided in the Excel file and then dividing by 15 mL, which is the input sewage volume.

3. Describe the tools and technologies you will use to ingest the lab data into the pipeline and store it into a cloud-hosted database. Feel free to provide a Python pseudocode in interfacing with a relational database (i.e. Postgres) to store the sewage concentrations and/or a schematic to display the pipeline workflow. Please also discuss how often your code will run and how it will be triggered.

Other questions we’re interested to have you explore. Feel free to address these questions in the code/pseudocode above, prepare an overview of your data pipeline architecture that addresses these points, or answer directly in a format of your choice:

● How will you ensure that the Excel template has the correct format?

● What data QC analyses will you pursue or build? How will you provide visibility into data
QC for the team? What will happen if a sample on a qPCR plate or an entire qPCR plate
fails QC?

● What constraints do you expect to face? How will you balance trade-offs between
ensuring reliable, robust data ingestion and QC but enabling automated and quick
processing times?

● How will you implement the process of updating the standard curve each week into your
pipeline and script?

● How can you expand the base pipeline for Covid-19 to include other qPCR targets such
as influenza A and B?

● How do you collaborate with the lab team and other engineers to build the pipeline?
(Some key areas to explore are methods of communication between and within teams,
visibility on requirements, working together on the same repository)

● What are the things we aren’t considering but should be thinking about based on
everything you’ve heard throughout the interview process?
```
## References

- https://assets.thermofisher.com/TFS-Assets/LSG/brochures/CO28730-Crt-Tech-note_FLR.pdf

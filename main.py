'''
Author: William Wright
Date: 2020-12-19

# additional tests
    # check to make sure non-null Cq wells match accross all sheets
    # dataframe shape matches expected
    # three replicates for each measure (warning not error; may be intentional at times)

# assumptions
    # NA present in Cq field when florescence levels did not exceed threshold value (10 sd above baseline)
'''

import os

import datetime as dt
import pandas as pd
import numpy as np


def std_curve_conversion(sheet, ele):
    '''std_curve_conversion docstring
	calculate total copies
	N1: y = -0.3068*x + 12.506
	N2: y = -0.2876*x + 11.912
	'''
    if isinstance(ele, str):
        return np.nan
    else:
        if ('N1' in sheet) or ('PMMV' in sheet):
            return 10**(-0.3068 * ele + 12.506)
        elif 'N2' in sheet:
            return 10**(-0.2876 * ele + 11.912)
        else:
            return np.nan


def sewage_conc_conversion(row):
    '''sewage_conc_conversion docstring
	convert total copies to sewage conc
	sewage_conc = total_copies * dilution_factor / 15 mL
	'''
    sheet = row.sheet
    if ('N1' in sheet) or ('N2' in sheet):
        dilution_factor = row['Dilution factor SARS-CoV-2']
        return row.total_copies * dilution_factor / 15
    elif ('PMMV' in sheet):
        dilution_factor = row['Dilution factor PMMV']
        return row.total_copies * dilution_factor / 15
    else:
        return np.nan


def gen_info_df(xl, sheets):
    '''gen_info_df docstring
	generates dataframe of sample info from first sheet with
	"sample" in the sheet name
	'''
    expected_cols = [
        'Well', 'Sample ID', 'Dilution factor SARS-CoV-2',
        'Dilution factor PMMV'
    ]
    expected_cols = [i.lower() for i in expected_cols]
    info = [i for i in sheets if 'sample' in i]

    try:
        assert len(info) == 1
        info = info[0]
    except AssertionError as e:
        print(
            e, '\n unexpected number of sheets with "sample" in name, \
			attempting to run with first')
        info = info[0]
        # make process recursive such that each 'info' sheet is tried before erroring out
    df = xl.parse(info)
    l = list(df)[:4]
    # test not resilient to spelling errors
    assert all([(i.lower() in expected_cols) for i in l])
    df = df[l]
    return df


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
            print(
                e, '\n Excel sheet {} in {} was an unexpected shape'.format(
                    sheet, filename))
            break

        df = df[[i for i in df.columns if 'Unnamed' not in i]]
        df['total_copies'] = df.Cq.apply(
            lambda x: std_curve_conversion(sheet, x))
        df['sheet'] = sheet
        dfs.append(df)

    ndf = pd.concat(dfs)
    return xl, ndf, sheets


def save_results(df, filename):
    '''save_results docsting'''
    folder_name = 'results'
    try:
        os.mkdir(folder_name)
    except FileExistsError as e:
        print(e)
    today = str(dt.datetime.today()).split(' ')[0]
    df.to_csv(folder_name + '/' + today + '_processed_exp_' +
              filename.split('.')[0] + '.csv',
              index=False)


def main():
    '''main docstring'''
    filename = 'sample_data.xlsx'
    xl, ndf, sheets = excel_to_rep_df(filename)
    df = gen_info_df(xl, sheets)
    ndf = ndf.merge(df, on='Well', how='left')
    ndf['sewage_conc'] = ndf.apply(lambda x: sewage_conc_conversion(x), axis=1)
    save_results(ndf, filename)


if __name__ == '__main__':
    main()

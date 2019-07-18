import pandas as pd
import numpy as np
import requests
import datetime
import traceback
import zipfile
import os
import shutil
import json
import datefinder

from amc.models import AMC_Portfolio_Process, Scheme_Portfolio, Scheme_Portfolio_Data

from todo.models import Scheme, AMC
from amc.jobs.util import ExcelFile, read_excel, match_fund_name_from_sheet, find_date_from_sheet, find_row_with_isin_heading, get_amc_common_names

from amc.jobs.util import aum_path

from fuzzywuzzy import fuzz, process

from amc.models import Scheme_AUM_Process, Scheme_AUM_Process_Log, Scheme_AUM

"""
https://mutualfund.adityabirlacapital.com/forms-and-downloads/total-expense-ratio
https://www.icicipruamc.com/Downloads/total-expense-ratio.aspx
https://www.dspim.com/quick-links/total-expense-ratio-of-mutual-fund-schemes
https://www.hdfcfund.com/statutory-disclosure/total-expense-ratio-of-mutual-fund-schemes/reports
https://www.principalindia.com/all-downloads/disclosures
http://www.quant-mutual.com/statutory-disclosures
https://www.jmfinancialmf.com/Downloads/Remuneration.aspx?SubReportID=0383C306-CFB7-4CFE-B516-2A8FE89ABF5D
# this works when you delete the first sheet named Notice from excel
https://assetmanagement.kotak.com/total-expense-ratio
https://www.licmf.com/total-expense-ratio
https://www.reliancemutual.com/investor-services/downloads/total-expense-ratio-of-mutual-fund-schemes
https://www.sbimf.com/en-us/disclosure/total-expense-ratio-of-mutual-fund-schemes
https://www.franklintempletonindia.com/investor/reports
http://www.saharamutual.com/downloads/TotalExpenseRatio.aspx
https://www.sundarammutual.com/TER
https://www.canararobeco.com/investor-corner/total-expense-ratio
https://old.canararobeco.com/forms-downloads/Pages/expenseratio.aspx
https://www.utimf.com/forms-and-downloads/#js-ter-wrapper
http://www.tatamutualfund.com/our-funds/total-expense-ratio
https://www.dspim.com/quick-links/total-expense-ratio-of-mutual-fund-schemes

only latest data is needed not old

"""


def start_process():
    process_zip_file()
    process_file()

    # Scheme_TER_Process
    pass


def process_file():
    for (dirpath, dirnames, filenames) in os.walk(aum_path):
        for f in filenames:
            if "lock" in f:
                continue

            if ".xls" in f.lower() or ".xlsx" in f.lower():

                process_aum(os.path.join(aum_path, f), f)
                break

                # try:
                #     os.mkdir(os.path.join(aum_path, "processed_files"))
                # except FileExistsError:
                #     pass

                # os.rename(os.path.join(aum_path, f), os.path.join(
                #     os.path.join(aum_path, "processed_files"), f))

                # process_ter(os.path.join(
                #     os.path.join(aum_path, "processed_files"), f), f)

                # break

        break  # this break is important to prevent further processing of sub directories
    pass


def process_zip_file():
    # many mf have portfolio as zip files so first we need to extract them

    for (dirpath, dirnames, filenames) in os.walk(aum_path):
        for f in filenames:
            if ".zip" in f:

                print("processing file ", f)
                with zipfile.ZipFile(os.path.join(aum_path, f)) as zip_file:
                    for member in zip_file.namelist():
                        filename = os.path.basename(member)
                        # skip directories
                        if not filename:
                            continue

                        # copy file (taken from zipfile's extract)
                        source = zip_file.open(member)
                        target = open(os.path.join(
                            aum_path, filename), "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)

                with zipfile.ZipFile(os.path.join(aum_path, f), "r") as zip_ref:
                    print(aum_path)
                    zip_ref.extractall(aum_path)
                # os.remove(os.path.join(path, f))
                try:
                    os.mkdir(os.path.join(aum_path, "processed_zips"))
                except FileExistsError:
                    pass

                os.rename(os.path.join(aum_path, f), os.path.join(
                    os.path.join(aum_path, "processed_zips"), f))

        break  # this break is important to prevent further processing of sub directories


def process_aum(filename, f):

    print("filename ", filename)
    # print("amc ", amc.name)

    #  = "/mnt/c/work/newdref/mf_ter_download/Total Expense Ratio of Mutual Fund Schemes.xlsx"

    aum_process = Scheme_AUM_Process(file_name=filename)
    aum_process.save()

    xls = ExcelFile(filename)

    try:
        sheet_names = xls["sheet_names"]
    except:
        sheet_names = xls.sheet_names

    if len(sheet_names) > 5:
        print(" multiple sheets means ter is divided into different sheets. hence our default approach wont work ")
        aum_process.addLog(
            "multiple sheets means ter is divided into different sheets. hence our default approach wont work")

        return

    df1 = pd.read_excel(xls, 0)

    # print(df1.head(1))

    col_indexes = find_head_row(df1.head(10))

    print(col_indexes)

    if "Scheme" in col_indexes and "Grand_Total" in col_indexes:

        date = find_date_from_sheet(df1, f)

        print("Date found ", date)

        columns = [""] * df1.shape[1]

        df1.columns = columns

        for key in col_indexes:
            if key != "row_index" and key != "indexes":
                idx = col_indexes[key]
                columns[idx] = key

        # print(columns)

        df1.columns = columns

        # print(df1.iloc[col_indexes["row_index"]:, col_indexes["indexes"]])

        # df2 = df1.iloc[(col_indexes["row_index"]+1):, col_indexes["indexes"]]

        df2 = df1.drop("", axis=1)
        df2 = df2.fillna(False)

        df2 = df2[df2["Grand_Total"] != False]

        amc, amc_unique = identify_amc(df2)

        if amc is not None:
            print("found amc")
            print(amc)
            print(getattr(amc, "name"))

            aum_process.setAMC(getattr(amc, "name"))

            

            schemes = Scheme.objects.get_funds(amc=amc)

            df4 = df2.copy()

            scheme_map = {}

            scheme_name_map = {}
            scheme_not_found = []
            for fund in schemes:
                fund_name = getattr(fund, "fund_name")
                scheme_name_map[fund_name] = fund
                mask = df4.apply(lambda x: fund_name ==
                                 x["Scheme"], axis=1)

                df3 = df4[mask]

                if len(df3.index) > 0:
                    # print(df3)
                    df4.drop(labels=df3.index, axis=0, inplace=True)
                    print("fund name direct match ", fund_name)
                    # df3 = df3.drop_duplicates(subset="Total TER", keep="last")
                    # print(df3)
                    scheme_map[fund_name] = df3["Scheme"].iloc[0]
                else:
                    # print("fund name not found or some other error", fund_name)
                    scheme_not_found.append(fund_name)

            print(df4.shape)

            # print(df4)

            scheme_still_not_found = []
            for fund_name in scheme_not_found:
                short_fund_name = fund_name.replace(amc_unique, "")

                def m(x):
                    scheme = str(x["Scheme"]).replace(amc_unique, "")

                    return fuzz.token_set_ratio(
                        short_fund_name, scheme) > 95

                mask = df4.apply(m, axis=1)
                df3 = df4[mask]

                if len(df3.index) > 0:
                    # there is a problem in here in rare cases there can be multiple matches
                    # i.e multiple places with ratio > 95
                    # but we are always considering the index = 0 which is not correct in most cases
                    # rather we should take the index with heighest score.
                    # but its more cmplex logic so leaving it for now
                    # fixing above now :) :)

                    if len(df3.index) > 1:
                        df3['ratio'] = df3.apply(lambda row: fuzz.token_set_ratio(
                            fund_name, row["Scheme"]), axis=1)
                        df3 = df3.sort_values(by="ratio")
                        print(df3)

                    df4.drop(labels=df3.index, axis=0, inplace=True)
                    print("fund name fuzzy match ", fund_name,
                          " with ", df3["Scheme"].iloc[0])
                    scheme_map[fund_name] = df3["Scheme"].iloc[0]
                else:
                    # print("fund name not found or some other error", fund_name)
                    scheme_still_not_found.append(fund_name)

            # print(df2)
            for fund_name in scheme_map:
                fund_map_name = scheme_map[fund_name]
                mask = df2.apply(lambda x: fund_map_name ==
                                 x["Scheme"], axis=1)

                df3 = df2[mask]

                print(df3)

                print(fund_name)
                for row in df3.itertuples():
                    print(row)

                    # save_row_to_db(row, scheme_name_map[fund_name])

                # print(df3)
                # break
                # df4.drop(labels=df3.index, axis=0)

            """
            # this is taking too long when data is too much i.e excel sheet has like 1500 rows
            # the fuzzy match takes too long so need to optmize so comparing length
            # need to reduce data
            for fund_name in scheme_not_found:

                fund_name = fund_name.replace(amc_unique, "")

                def m(x):
                    scheme = x["Scheme"].replace(amc_unique, "")
                    print(scheme, 'xxx')

                    return fuzz.token_set_ratio(
                        fund_name, scheme) > 95

                mask = df4.apply(m, axis=1)
                df3 = df4[mask]

                if len(df3.index) > 0:
                    # df2.drop(labels=df3.index, axis=0, inplace=True)
                    print("fund name", fund_name)
                    # df3 = df3.drop_duplicates(subset="Total TER", keep="last")
                    # print(df3)
                else:
                    # print("fund name not found or some other error", fund_name)
                    scheme_not_found.append(fund_name)

            """

            move_file_finally(aum_path, amc, filename, f, aum_process)

            # break
            # print(scheme_map)
            print(scheme_still_not_found)
            aum_process.addLog(json.dumps(scheme_map))
            aum_process.addLog(json.dumps(scheme_still_not_found))
            # for row in df2.itertuples():
            #     print(row)

        else:
            print("unable to identify amc!")
            aum_process.addCritical("unable to identify amc!")
    else:
        aum_process.addCritical("columns not present unable to parse")
        print(col_indexes)
        print("columns not present unable to parse ", filename)


def identify_amc(df):

    df3 = df.drop_duplicates(subset="Scheme", keep="last")

    df3 = df3.head(15)

    schemes = df3.loc[:, "Scheme"].values

    return identify_amc_from_scheme_array(schemes)


def move_file_finally(aum_path, amc, filename, f, aum_process):
    try:
        os.mkdir(os.path.join(os.path.join(
            aum_path, "processed_files"), getattr(amc, "name")))
    except FileExistsError:
        pass

    os.rename(filename, os.path.join(os.path.join(os.path.join(
        aum_path, "processed_files"), getattr(amc, "name")), f))

    aum_process.updateFile(os.path.join(os.path.join(os.path.join(
        aum_path, "processed_files"), getattr(amc, "name")), f))


def identify_amc_from_scheme_array(schemes):
    amcs = get_amc_common_names()
    amc_score = {}

    for amc_name in amcs:
        for scheme_name in schemes:
            ratio = fuzz.token_set_ratio(amc_name, scheme_name)
            if ratio > 95:
                if amc_name in amc_score:
                    amc_score[amc_name] += 1
                else:
                    amc_score[amc_name] = 1
                break

    max_score = 0
    final_amc = None

    for key in amc_score:
        if amc_score[key] > max_score:
            final_amc = key

    if final_amc is not None:
        return AMC.objects.match_amc_with_short_name(final_amc), final_amc
    else:
        return None, None


def find_head_row(df):
    # most of our logic is based on scheme in row
        # this row is most important is present in all excel sheet

    df.loc[-1] = df.columns
    df.index = df.index + 1
    df = df.sort_index()

    print(df)

    col_indexes = {}

    indexes = find_col_index(df, "Scheme Name")

    # i have seen that all these expected cols can be in different rows so thats why this method

    if len(indexes) > 0:
        col_indexes["Scheme"] = indexes[0]

    indexes = find_col_index(df, "Grand Total")

    if len(indexes) > 0:
        col_indexes["Grand_Total"] = indexes[0]

    return col_indexes


def find_row_index(df, to_match):
    mask = df.apply(lambda x: x.astype(str).str.contains(to_match, False))
    df1 = df[mask.any(axis=1)]

    # print(df1)

    indexes = df1.index.values

    if len(indexes) > 0:
        return indexes[0]
    else:
        return -1


def find_col_index(df, col_name, strict=False):
    mask = df.apply(lambda x: x.astype(str).str.contains(col_name, False))
    df1 = df[mask.any(axis=1)]

    # print(df1)

    indexes = df1.index.values

    # print(indexes)

    if len(indexes) > 0:
        if strict is False:
            index = indexes[0]

            base_row = df.iloc[index].to_numpy()

            # print(base_row)
            indexes = []
            for val in base_row:
                val = str(val)
                ratio = fuzz.token_set_ratio(col_name, val)
                if col_name in val or ratio > 95:
                    i = list(base_row).index(val)
                    indexes.append(i)

        else:
            for index in indexes:
                base_row = df.iloc[index].to_numpy()
                indexes = []
                for val in base_row:
                    val = str(val)
                    if col_name == val:
                        i = list(base_row).index(val)
                        indexes.append(i)

    return indexes


def save_row_to_db(row, scheme):
    date = None
    if row.Date is False:
        return
    if isinstance(row.Date, pd._libs.tslibs.timestamps.Timestamp):
        date = row.Date.to_pydatetime()
    else:
        if isinstance(row.Date, datetime.date):
            date = row.Date
        else:
            matches = datefinder.find_dates(row.Date)
            for date in matches:
                break

    if date is not None:
        ter = row.Total_TER
        print(date)
        if isinstance(ter, str):
            ter = ter.replace("%", '')
            ter = float(ter)

        try:
            sc = Scheme_TER.objects.get(
                scheme=scheme, date=date)
            Scheme_TER.objects.filter(pk=sc.id).update(ter=ter)
        except:
            tr_db = Scheme_AUM(
                scheme=scheme,
                date=date,
                ter=ter
            )
            tr_db.save()

    else:
        print("unable to identify date!!")

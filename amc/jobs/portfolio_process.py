import pandas as pd
import numpy as np
import requests
from fuzzywuzzy import fuzz, process

import datetime
import traceback
import shutil

from colorama import Fore, Back, Style, init

import os

from amc.models import AMC_Portfolio_Process, Scheme_Portfolio, Scheme_Portfolio_Data

from todo.models import Scheme, AMC
from amc.jobs.util import match_fund_name_from_array, match_match_force_via_string, generic_process_zip_file, ExcelFile, read_excel, match_fund_name_from_sheet, find_date_from_sheet, find_row_with_isin_heading, get_amc_common_names

from amc.jobs.util import portfolio_path as mf_download_files_path, local_base_path, server_base_path

init(autoreset=True)


"""

portfolio not found for this scheme at all Aditya Birla Sun Life Pharma and Healthcare Fund
portfolio not found for this scheme at all Baroda ELSS 96 Plan B(Direct)
portfolio not found for this scheme at all HDFC Mid Cap Opportunities Fund
portfolio not found for this scheme at all JM Multicap Fund (Direct)
portfolio not found for this scheme at all JM Liquid Fund Unclaimed Redemption (Direct) Growth Plan
portfolio not found for this scheme at all JM Liquid Fund Unclaimed Dividend (Direct) Growth Plan
portfolio not found for this scheme at all JM Liquid Fund Unclaimed Redemption IEF (Direct) Growth Plan
portfolio not found for this scheme at all JM Liquid Fund Unclaimed Dividend IEF (Direct) Growth Plan
portfolio not found for this scheme at all Kotak Gilt Investment Provident Fund and Trust
portfolio not found for this scheme at all Kotak Focused equity Fund
portfolio not found for this scheme at all LIC MF Government Securities Fund
portfolio not found for this scheme at all LIC MF Savings Fund
portfolio not found for this scheme at all LIC NOMURA MF INDIA VISION FUND
portfolio not found for this scheme at all LIC MF Banking & PSU Debt Fund
portfolio not found for this scheme at all LIC NOMURA MF SYSTEMATIC ASSET ALLOCATION FUND
portfolio not found for this scheme at all LIC NOMURA MF TOP 100 FUND
portfolio not found for this scheme at all LIC MF Infrastructure Fund
portfolio not found for this scheme at all LIC MF Banking and Financial Services Fund
portfolio not found for this scheme at all LIC MF Arbitrage Fund
portfolio not found for this scheme at all LIC MF Short Term Debt Fund
portfolio not found for this scheme at all LIC MF Overnight Fund
portfolio not found for this scheme at all ICICI Prudential Moderate Fund
portfolio not found for this scheme at all ICICI Prudential Regular Savings Fund
portfolio not found for this scheme at all ICICI Prudential Medium Term Bond Fund
portfolio not found for this scheme at all ICICI Prudential Asset Allocator Fund
portfolio not found for this scheme at all ICICI Prudential Regular Gold Savings Fund
portfolio not found for this scheme at all ICICI Prudential Thematic Advantage Fund
portfolio not found for this scheme at all ICICI Prudential Long Term Bond Fund
portfolio not found for this scheme at all ICICI Prudential Constant Maturity Gilt Fund
portfolio not found for this scheme at all ICICI Prudential Overnight Fund
portfolio not found for this scheme at all ICICI Prudential Retirement Fund  Hybrid Conservative
portfolio not found for this scheme at all ICICI Prudential Retirement Fund  Hybrid Aggressive
portfolio not found for this scheme at all ICICI Prudential MNC Fund
portfolio not found for this scheme at all Reliance Vision Fund
portfolio not found for this scheme at all Reliance Japan Equity Fund
portfolio not found for this scheme at all Reliance Equity Savings Fund
portfolio not found for this scheme at all Reliance US Equity Opportunites Fund
portfolio not found for this scheme at all SBI Small Cap Fund
portfolio not found for this scheme at all Tata Retirement Savings Fund Moderate
portfolio not found for this scheme at all Tata Retirement Savings Fund Conservative
portfolio not found for this scheme at all Franklin India Feeder  Franklin US Opportunities Fund
portfolio not found for this scheme at all UTI MMF
portfolio not found for this scheme at all UTI  Master Share
portfolio not found for this scheme at all UTI  Core Equity Fund
portfolio not found for this scheme at all UTI  Hybrid Equity Fund
portfolio not found for this scheme at all UTI  NIFTY Index Fund
portfolio not found for this scheme at all UTI CCF Investment Plan
portfolio not found for this scheme at all UTI Transpotation and Logistics Fund
portfolio not found for this scheme at all UTI Corporate Bond Fund
portfolio not found for this scheme at all UTI Equity Savings Fund
portfolio not found for this scheme at all Canara Robeco Overnight Fund
portfolio not found for this scheme at all Sundaram Large and Midcap Fund
portfolio not found for this scheme at all Sundaram Equity Savings Direct Plan Growth
portfolio not found for this scheme at all Sahara Liquid Fund Fixed Pricing
portfolio not found for this scheme at all SaharaTax Gain
portfolio not found for this scheme at all Sahara Midcap Fund
portfolio not found for this scheme at all Sahara Wealth Plus Fund Fixed Pricing Option
portfolio not found for this scheme at all Sahara Wealth Plus Fund Variable Pricing Option
portfolio not found for this scheme at all Sahara Infrastructure Fund  FIXED PRICING OPTION
portfolio not found for this scheme at all Sahara Infrastructure Fund  VARIABLE PRICING OPTION
portfolio not found for this scheme at all Sahara R.E.A.L Fund
portfolio not found for this scheme at all Sahara Power & Natural resources Fund
portfolio not found for this scheme at all SAHARA BANKING & FINANCIAL SERVICES FUND
portfolio not found for this scheme at all SAHARA SHORT TERM BOND FUND
portfolio not found for this scheme at all Sahara Super 20 Fund
portfolio not found for this scheme at all Sahara Star Value Fund
portfolio not found for this scheme at all SAHARA INTERVAL FUND QUARTERLY PLAN
portfolio not found for this scheme at all QUANTUM INDIA ESG EQUITY FUND
portfolio not found for this scheme at all BOIAXAEQUITY DEBT REBALANCER FUND DIRECT PLAN GROWTH
portfolio not found for this scheme at all BOI AXA Small Cap Fund Direct Plan Growth
portfolio not found for this scheme at all Edelweiss Aggressive Hybrid Fund
portfolio not found for this scheme at all Edelweiss Overnight Fund
portfolio not found for this scheme at all IDFC DEF_Direct Plan_Growth
portfolio not found for this scheme at all IDFC CBF_Direct Plan_Growth
portfolio not found for this scheme at all Axis Children's Gift Fund  without Lock in
portfolio not found for this scheme at all Essel Large Cap Equity Fund
portfolio not found for this scheme at all ESSEL FLEXIBLE INCOME FUND
portfolio not found for this scheme at all Essel Regular Savings Fund
portfolio not found for this scheme at all Essel Liquid Fund
portfolio not found for this scheme at all Essel 3 in 1 Fund
portfolio not found for this scheme at all Essel Ultra Short Term Fund
portfolio not found for this scheme at all Essel Long Term Advantage Fund
portfolio not found for this scheme at all Essel Large & Midcap Fund
portfolio not found for this scheme at all Essel Equity Hybrid Fund
portfolio not found for this scheme at all Essel Multi Cap Fund
portfolio not found for this scheme at all Essel Arbitrage Fund
portfolio not found for this scheme at all IDBI UST Growth Direct
portfolio not found for this scheme at all BNP Paribas Mid Cap Fund
portfolio not found for this scheme at all IIFL SHORT TERM INCOME FUND DIRECT PLAN GROWTH OPTION
portfolio not found for this scheme at all Indiabulls Overnight Fund
portfolio not found for this scheme at all Shriram Balanced Advantage Fund
portfolio not found for this scheme at all Mahindra Dhan Sanchay Equity Savings Yojana
portfolio not found for this scheme at all Mahindra Low Duration Bachat Yojana
portfolio not found for this scheme at all Mahindra Unnati Emerging Business Yojana
portfolio not found for this scheme at all Mahindra Credit Risk Yojana
portfolio not found for this scheme at all Mahindra Rural Bharat and Consumption Yojana
portfolio not found for this scheme at all Mahindra Pragati Bluechip Yojana
portfolio not found for this scheme at all Mahindra Hybrid Equity Nivesh Yojana
portfolio not found for this scheme at all Mahindra Overnight Fund
portfolio not found for this scheme at all Mirae Asset Midcap Fund
portfolio not found for this scheme at all HSBC Large Cap Equity Fund
portfolio not found for this scheme at all HSBC Infrastructure Equity Fund
portfolio not found for this scheme at all HSBC Brazil Fund
portfolio not found for this scheme at all HSBC Cash Fund
portfolio not found for this scheme at all HSBC Global Emerging Market Fund
portfolio not found for this scheme at all HSBC Multi Cap Equity Fund
portfolio not found for this scheme at all HSBC Flexi Debt Fund
portfolio not found for this scheme at all HSBC Debt Fund
portfolio not found for this scheme at all HSBC Short Duration Fund
portfolio not found for this scheme at all HSBC Low Duration Fund
portfolio not found for this scheme at all HSBC Small Cap Equity Fund
portfolio not found for this scheme at all HSBC Regular Savings Fund
portfolio not found for this scheme at all HSBC Tax Saver Equity Fund
portfolio not found for this scheme at all HSBC Asia Pacific (Ex Japan) Dividend Yield Fund
portfolio not found for this scheme at all HSBC Managed Solutions  Moderate
portfolio not found for this scheme at all HSBC Managed Solutions  Conservative
portfolio not found for this scheme at all HSBC Managed Solutions
portfolio not found for this scheme at all HSBC Global Consumer Opportunities Fund
portfolio not found for this scheme at all HSBC Equity Hybrid Fund
portfolio not found for this scheme at all HSBC Large and Mid Cap Equity Fund
portfolio not found for this scheme at all HSBC Overnight Fund
portfolio not found for this scheme at all Invesco India Dynamic Equity Fund
portfolio not found for this scheme at all Invesco India Contra Fund
portfolio not found for this scheme at all Invesco India Growth Opportunities Fund
portfolio not found for this scheme at all Invesco India Financial Services Fund
portfolio not found for this scheme at all Invesco India Largecap Fund
portfolio not found for this scheme at all Invesco India PSU Equity Fund
portfolio not found for this scheme at all Invesco India Arbitrage Fund
portfolio not found for this scheme at all Invesco India Midcap Fund
portfolio not found for this scheme at all Invesco India Infrastructure Fund
portfolio not found for this scheme at all Invesco India Multicap Fund
portfolio not found for this scheme at all Invesco India Tax Plan
portfolio not found for this scheme at all Invesco India Banking & PSU Debt Fund
portfolio not found for this scheme at all Invesco India Corporate Bond Fund
portfolio not found for this scheme at all Invesco India Money Market Fund
portfolio not found for this scheme at all Invesco India Gilt Fund
portfolio not found for this scheme at all Invesco India Gold Fund
portfolio not found for this scheme at all Invesco India Liquid Fund
portfolio not found for this scheme at all Invesco India Ultra Short Term Fund
portfolio not found for this scheme at all Invesco India Short Term Fund
portfolio not found for this scheme at all Invesco India Treasury Advantage Fund
portfolio not found for this scheme at all Invesco India Feeder  Invesco Pan European Equity Fund
portfolio not found for this scheme at all Invesco India Feeder  Invesco Global Equity Income Fund
portfolio not found for this scheme at all Invesco India Credit Risk Fund
portfolio not found for this scheme at all Invesco India Equity & Bond Fund
portfolio not found for this scheme at all Invesco India Smallcap Fund
portfolio not found for this scheme at all Invesco India Equity Savings Fund
portfolio not found for this scheme at all Parag Parikh Tax Saver Fund

https://mutualfund.adityabirlacapital.com/forms-and-downloads/portfolio
https://www.barodamf.com/Downloads/Pages/Latest-Factsheet-and-Profile.aspx
https://dspim.com/about-us/mandatory-disclosure/portfolio-disclosures
https://www.hdfcfund.com/statutory-disclosure/monthly-portfolio
https://www.principalindia.com/all-downloads/disclosures
http://www.quant-mutual.com/statutory-disclosures
https://www.jmfinancialmf.com/Downloads/FactSheets.aspx?SubReportID=A49C5853-C27A-42C5-9703-699AFEACE164
https://assetmanagement.kotak.com/portfolios
https://www.licmf.com/statutory-disclosure
https://www.icicipruamc.com/Downloads/MonthlyPortfolioDisclosure.aspx
https://www.reliancemutual.com/investor-service/downloads/factsheets
https://www.sbimf.com/en-us/portfolios
https://www.tatamutualfund.com/downloads/monthly-portfolio
https://www.taurusmutualfund.com/Download/portfolio.php
https://www.franklintempletonindia.com/investor/reports
https://www.utimf.com/about/statutory-disclosures/scheme-dashboard
https://www.canararobeco.com/statutory-disclosures/scheme-monthly-portfolio
https://www.sundarammutual.com/Monthly_Portfolio
http://www.saharamutual.com/downloads/MonthlyPortfolio.aspx
https://www.boiaxamf.com/investor-corner#t2
https://www.edelweissmf.com/statutory#Monthly-Portfolio-of-Schemes
https://www.idfcmf.com/download-centre.aspx?tab=disclosures
https://www.axismf.com/statutory-disclosures
https://www.motilaloswalmf.com/downloads/mutual-fund/Month-End-Portfolio
https://www.ltfs.com/companies/lnt-investment-management/statutory-disclosures.html
https://www.idbimutual.co.in/Downloads/Fund-Portfolios
http://www.dhflpramericamf.com/statutory-disclosure/monthlyportfolio
https://www.bnpparibasmf.in/downloads/monthly-portfolio-scheme
http://www.unionmf.com/downloads/others/monthlyportfolios.aspx
https://www.iiflmf.com/downloads/disclosures
http://www.indiabullsamc.com/portfolio-disclosure/
https://shriramamc.com/StatDis-MonthlyPort.aspx
https://www.mahindramutualfund.com/downloads#MANDATORY-DISCLOSURES
https://www.miraeassetmf.co.in/downloads/portfolios
https://www.yesamc.in/regulatory-disclosures/monthly-and-half-yearly-portfolio-disclosures
http://amc.ppfas.com/downloads/portfolio-disclosure/
http://www.itimf.com/statutory-disclosure/monthly-portfolios
https://www.invescomutualfund.com/literature-and-form?tab=Complete
"""

# need to figure out multiple things in this
# 1. how to download different excel sheets from diffrent mf providers
# 2. need some kind of error report if portfolio import fails
# 3. there are multiple funds like bharatcon serial1, 2, 3 etc need to see how to fix this
# 4. need to be able to find out if for certain funds portfolio was not import or for full house


def process_zip_file():
    # many mf have portfolio as zip files so first we need to extract them
    # move_files_from_folder_to_parent()
    generic_process_zip_file(mf_download_files_path)
    identify_amc()


def move_files_from_folder_to_parent():
    # this is temporary one time function i made to move all processed files from
    # amc directorys back to original path for testing purposes

    from amc.jobs.util import server_base_path

    print(os.path.join(server_base_path, "amfi", "data", "portfolio"))

    for (dirpath, dirnames, filenames) in os.walk(os.path.join(server_base_path, "amfi", "data", "portfolio")):
        for f in filenames:
            if "lock" in f:
                continue

            if "2019" in dirpath:
                # if ".xls" in f.lower() or ".xlsx" in f.lower():
                print(os.path.join(dirpath, f))
                shutil.copy(os.path.join(dirpath, f),
                            os.path.join(mf_download_files_path, f))

    pass


def identify_amc():
    # logic is to identiy amc from excel sheet.
    # logiic is simple loop through amc's and find the maximum occurance of a single amc name in all sheets

    amc_names = get_amc_common_names()
    print(amc_names)

    for (dirpath, dirnames, filenames) in os.walk(mf_download_files_path):
        for f in filenames:
            if "lock" in f:
                continue

            if ".xls" in f.lower() or ".xlsx" in f.lower():

                try:

                    amc_process = AMC_Portfolio_Process(
                        file_name=os.path.join(mf_download_files_path, f))
                    amc_process.save()

                    print("reading file ", os.path.join(
                        mf_download_files_path, f))

                    amc_process.addLog("reading file " +
                                       os.path.join(mf_download_files_path, f))

                    # xls = pd.ExcelFile(os.path.join(path, f))
                    xls = ExcelFile(os.path.join(mf_download_files_path, f))
                    try:
                        sheet_names = xls["sheet_names"]
                    except:
                        sheet_names = xls.sheet_names

                    amc_sheet_match = {}

                    # UTI mf has a totally different format
                    # we need to hard code for UTI MF no other way

                    if "Performance Data" in sheet_names and "Funds at Glance" in sheet_names and "Portfolio" in sheet_names:
                        # this is uti mf
                        max_amc = "UTI"
                    else:
                        print("trying to identify amc")
                        for sheet_name in sheet_names:
                            if sheet_name == "Index" or sheet_name == "Sheet1":
                                continue
                            print("checking for sheet name", sheet_name)
                            # df1 = pd.read_excel(xls, sheet_name)
                            df1 = read_excel(xls, sheet_name)

                            mask = df1.apply(lambda x: x.astype(
                                str).str.contains('ISIN', False))
                            df2 = df1[mask.any(axis=1)]

                            # print(df2)

                            indexes = df2.index.values

                            if len(indexes) > 0:
                                # df1 = df1.head(indexes[0])
                                # print(df1)
                                amc, score, cell = match_fund_name_from_sheet(
                                    amc_names, df1)

                                print(amc, "xxxx", score)

                                if score > 0:
                                    if amc in amc_sheet_match:
                                        amc_sheet_match[amc] += 1
                                    else:
                                        amc_sheet_match[amc] = 1
                            else:
                                amc_process.addLog(
                                    "isin not found! in sheet " + sheet_name)
                                # print(df1)
                                print("isin not found! in sheet " + sheet_name)
                                # pass

                        max_count = 0
                        max_amc = False

                        for amc in amc_sheet_match:
                            count = amc_sheet_match[amc]
                            if count > max_count:
                                max_count = count
                                max_amc = amc

                    amc_process.setAMC(max_amc)

                    amc_process.addLog("amc identified as " + str(max_amc))

                    if max_amc != False:
                        if len(sheet_names) > 2:
                            # will read data from sheet 2
                            df1 = read_excel(xls, 2)
                        else:
                            df1 = read_excel(xls, 0)

                        if max_amc == "UTI":
                            date = False
                            for year in ["2015", "2016", "2017", "2018", "2019"]:
                                if year in f:
                                    date = match_match_force_via_string(
                                        year, f)
                                    break

                        else:
                            date = find_date_from_sheet(df1, f)

                        if date is not False:

                            amc_process.addLog(
                                "date found " + date.strftime('%m/%d/%Y'))

                            m = date.strftime("%b")
                            y = date.strftime("%Y")

                            try:

                                if not os.path.exists(os.path.join(mf_download_files_path, max_amc)):
                                    os.mkdir(os.path.join(
                                        mf_download_files_path, max_amc))

                                if not os.path.exists(os.path.join(mf_download_files_path, max_amc, y)):
                                    os.mkdir(os.path.join(
                                        mf_download_files_path, max_amc, y))

                                if not os.path.exists(os.path.join(mf_download_files_path, max_amc, y, m)):
                                    os.mkdir(os.path.join(
                                        mf_download_files_path, max_amc, y, m))

                                # amc_process.addLog(os.path.join(
                                #     mf_download_files_path, f))
                                amc_process.addLog(os.path.join(
                                    os.path.join(mf_download_files_path, max_amc, y, m), f))

                                shutil.copy(os.path.join(mf_download_files_path, f),
                                            os.path.join(mf_download_files_path, max_amc, y, m, f))

                                amc_process.setFinalFilePath(os.path.join(
                                    mf_download_files_path, max_amc, y, m, f))

                                process_data(amc_process)

                                # os.rename(os.path.join(
                                #     mf_download_files_path, f), os.path.join(
                                #     mf_download_files_path, "processed", f))

                            except Exception as e:
                                traceback.print_exc(e)
                                amc_process.addCritical(e)
                                print(e)
                        else:
                            amc_process.addCritical("date not found! see data")
                            try:
                                os.mkdir(os.path.join(
                                    mf_download_files_path, "processed_files_data_missing"))
                            except FileExistsError:
                                pass
                            shutil.move(os.path.join(mf_download_files_path, f),
                                        os.path.join(mf_download_files_path, "processed_files_data_missing", f))
                            print(Fore.RED + "date not found! see data")
                    else:
                        try:
                            os.mkdir(os.path.join(
                                mf_download_files_path, "processed_files_amc_missing"))
                        except FileExistsError:
                            pass
                        amc_process.addCritical("amc not found! see data")
                        shutil.move(os.path.join(mf_download_files_path, f),
                                    os.path.join(mf_download_files_path, "processed_files_amc_missing", f))
                        print(Fore.RED + "amc not found! see data")
                        # break

                    print(amc_sheet_match)
                except Exception as e:
                    traceback.print_exc(e)
                    amc_process.addCritical(e)
                    print(Fore.RED + str(e))

                # break

        break

    pass


def process_data(amc_process):

    # to_process = AMC_Portfolio_Process.objects.get_portfolio_to_process(5)
    # for amc_process in to_process:
    file_path = getattr(amc_process, "final_path")
    amc_short_name = getattr(amc_process, "amc")

    # one time temporary code since we parsed files in local it has local path
    # if local_base_path in file_path:
    #     file_path = file_path.replace(local_base_path, server_base_path)

    amc = AMC.objects.match_amc_with_short_name(amc_short_name)

    if amc != False:
        try:
            process_portfolio(file_path, amc, getattr(
                amc_process, "date"), amc_process)
            amc_process.parsing_completed()
        except Exception as e:
            print(Fore.RED + str(e))
            amc_process.addCritical(e)
            amc_process.parsing_completed()
            traceback.print_exc(e)

        # break

    else:
        print(Fore.RED + "unable to match amc")
        amc_process.addCritical("Unable to match amc itself!")
        amc_process.parsing_completed()


def identify_funds(filename, amc, date, amc_process):

    print("identifyign funds")
    print("filename ", filename)
    print("amc ", amc.name)

    xls = ExcelFile(filename)

    schemes = Scheme.objects.filter(amc=amc)

    fund_names = {}

    fund_check_list = []
    for scheme in schemes:
        fund_name = scheme.get_clean_name()
        fund_names[fund_name] = scheme
        fund_check_list.append(fund_name)
        # print(fund_name)

    print(fund_check_list)

    fund_match_sheet = {}

    try:
        sheet_names = xls["sheet_names"]
    except:
        sheet_names = xls.sheet_names

    for sheet_name in sheet_names:
        if sheet_name == "Index":
            continue
        print("checking for sheet name", sheet_name)
        df1 = pd.read_excel(xls, sheet_name)

        fund, ratio, cell = match_fund_name_from_sheet(
            fund_names.keys(), df1, True, True)

        if fund in fund_match_sheet:
            amc_process.addCritical("conflict detected : fund : " + fund +
                                    " cell1: " + cell + " cell2: " + fund_match_sheet[fund]["cell"])
            print(Fore.RED + "conflict detected see what to do!")
            print(fund_match_sheet[fund], fund)
            print(fund, "===",  ratio, "===", sheet_name, " === ", cell)
            ratio1 = fuzz.ratio(fund, cell)
            ratio2 = fuzz.ratio(fund, fund_match_sheet[fund]["cell"])
            print(ratio1, ' ==== ', ratio2)

        if fund is not None:
            print("fund found : ", fund, "===",  ratio,
                  "===", sheet_name, " === ", cell)
            fund_match_sheet[sheet_name] = fund

        if fund in fund_check_list:
            fund_check_list.remove(fund)

    print(Fore.RED + "fund not found", fund_check_list)

    return fund_match_sheet


def process_portfolio(filename, amc, date, amc_process):

    if getattr(amc, "name") == "UTI Mutual Fund":
        xls = ExcelFile(filename)
        df1 = pd.read_excel(xls, "Portfolio")

        #df1 = df1.fillna("")

        schemes = Scheme.objects.filter(amc=amc)

        fund_names = {}

        for scheme in schemes:
            fund_name = getattr(scheme, "fund_name")
            fund_names[fund_name] = scheme
            # print(fund_name, getattr(scheme, "id"))

        # another problem of equity fund there are just two columns
        # Equity/Nav
        # for debt we have
        # Debt,Nav, Rating

        df1.loc[-1] = df1.columns
        df1.index = df1.index + 1
        df1 = df1.sort_index()

        mask = df1.apply(lambda x: x.astype(str).str.contains('UTI', False))
        df1 = df1[mask.any(axis=1)]
        indexes = df1.index.values
        index = indexes[0]

        fund_names_df = df1.loc[index].values

        print(fund_names_df)

        for index, row in enumerate(fund_names_df):
            print(row, "xxx", type(row), "yy", str(row))
            if isinstance(row, str) and "UTI" in str(row):
                row = str(row).strip()

                try:

                    fund, ratio, cell = match_fund_name_from_array(
                        fund_names.keys(), [row])
                    print(fund, "===",  ratio, " === ", cell)
                    start_index = index
                    end_index = index

                    if fund is not None:

                        # find next is not nan
                        for i, row2 in enumerate(fund_names_df):
                            if i > start_index:
                                print(row2)
                                if isinstance(row2, str) and "UTI" in str(row2):
                                    end_index = i
                                    break

                        end_index = end_index - 1

                        print(start_index, "====", end_index)

                        print(df1.iloc[:, start_index:end_index])

                        df3 = df1.iloc[:, start_index:end_index]
                        # df3 =
                        df3 = df3.rename(columns=df3.iloc[1, :])
                        df3 = df3.iloc[2:]

                        scheme_ports = Scheme_Portfolio_Data.objects.filter(
                            scheme=fund_names[fund], date__year=date.year, date__month=date.month)

                        for port in scheme_ports:
                            Scheme_Portfolio.objects.filter(
                                scheme=port).delete()
                            port.delete()

                        scheme_data = Scheme_Portfolio_Data(
                            scheme=fund_names[fund],
                            url=filename,
                            date=date
                        )
                        scheme_data.save()

                        print(df3)
                        if "Equity" in df3.columns.values:
                            for row in df3.iterrows():
                                name = row[0]
                                nav_per = row[1]

                                scheme_portfolio = Scheme_Portfolio(
                                    scheme=scheme_data,
                                    name=name,
                                    percent=nav_per
                                )
                                scheme_portfolio.save()
                        else:
                            for row in df3.iterrows():
                                name = row[0]
                                nav_per = row[1]
                                rating = row[2]

                                scheme_portfolio = Scheme_Portfolio(
                                    scheme=scheme_data,
                                    name=name,
                                    percent=nav_per,
                                    rating=rating
                                )
                                scheme_portfolio.save()

                        # df3.loc[-1] = df3.columns
                        # df3.index = df3.index + 1
                        # df3 = df3.sort_index()

                        # print(df3)

                        break

                except Exception as e:
                    print(Fore.RED + str(e))
                    pass
        return

    fund_match_sheet = identify_funds(filename, amc, date, amc_process)

    xls = ExcelFile(filename)

    schemes = Scheme.objects.filter(amc=amc)

    fund_names = {}

    for scheme in schemes:
        fund_name = scheme.get_clean_name()
        fund_names[fund_name] = scheme
        # print(fund_name)

    try:
        sheet_names = xls["sheet_names"]
    except:
        sheet_names = xls.sheet_names

    for sheet_name in sheet_names:
        if sheet_name == "Index":
            continue
        print("checking for sheet name", sheet_name)
        df1 = pd.read_excel(xls, sheet_name)

        if sheet_name not in fund_match_sheet:
            print("skipping sheet")
            continue

        fund = fund_match_sheet[sheet_name]

        print(fund, "===", sheet_name)

        if fund is not None:
            col_indexes = find_row_with_isin_heading(df1, fund_names[fund])

            scheme = fund_names[fund]

            try:
                print(scheme)
                print(date)

                scheme_ports = Scheme_Portfolio_Data.objects.filter(
                    scheme=scheme, date__year=date.year, date__month=date.month)

                for port in scheme_ports:
                    Scheme_Portfolio.objects.filter(scheme=port).delete()
                    port.delete()
            except Exception as e:
                print(Fore.RED + str(e))

            scheme_data = Scheme_Portfolio_Data(
                scheme=scheme,
                url=filename,
                date=date
            )
            scheme_data.save()

            print(scheme_data)

            if "ISIN" in col_indexes and "Name" in col_indexes and "Market" in col_indexes and "Quantity" in col_indexes and "Rating" in col_indexes:
                # df1.fillna(False)
                # df1.rename()

                columns = [""] * df1.shape[1]

                print(columns)
                for key in col_indexes:
                    if key != "row_index" and key != "indexes":
                        idx = col_indexes[key]
                        columns[idx] = key

                print(columns)

                df1.columns = columns

                print(df1.iloc[col_indexes["row_index"]
                      :, col_indexes["indexes"]])

                df2 = df1.iloc[(col_indexes["row_index"]+1)
                                :, col_indexes["indexes"]]
                df2 = df2.fillna(False)

                if "Coupon" not in df2.columns:
                    df2["Coupon"] = 0

                for row in df2.itertuples():
                    name = row.Name
                    isin = row.ISIN
                    quantity = row.Quantity
                    coupon = row.Coupon
                    rating = row.Rating
                    market = row.Market
                    nav_per = row.NAV

                    if name == False:
                        # simply skip data
                        continue

                    if isin != False:
                        # this is some kind of security either bond or stock

                        if coupon != False:
                            # this is debt fund

                            scheme_portfolio = Scheme_Portfolio(
                                scheme=scheme_data,
                                name=name,
                                isin=isin,
                                quantity=quantity,
                                coupon=coupon,
                                rating=rating,
                                market=market,
                                percent=nav_per
                            )
                            scheme_portfolio.save()

                        else:
                            # this is stock
                            scheme_portfolio = Scheme_Portfolio(
                                scheme=scheme_data,
                                name=name,
                                isin=isin,
                                quantity=quantity,
                                industry=rating,
                                market=market,
                                percent=nav_per
                            )
                            try:
                                scheme_portfolio.save()
                            except Exception as e:
                                # from django.db import connection
                                # print(connection.queries[-1])
                                traceback.print_exc()
                                print(Fore.RED, str(e))
                                print(scheme_data)
                                print(isin)
                                # traceback.print_exc(e)
                                pass

                    else:
                        if quantity != False and rating != False:
                            # looks like unlisted stock or bond
                            if coupon != False:
                                scheme_portfolio = Scheme_Portfolio(
                                    scheme=scheme_data,
                                    name=name,
                                    quantity=quantity,
                                    coupon=coupon,
                                    rating=rating,
                                    market=market,
                                    percent=nav_per
                                )
                                scheme_portfolio.save()
                            else:
                                scheme_portfolio = Scheme_Portfolio(
                                    scheme=scheme_data,
                                    name=name,
                                    quantity=quantity,
                                    industry=rating,
                                    market=market,
                                    percent=nav_per
                                )
                                scheme_portfolio.save()
                        else:
                            # this is general classification. not saving this for now
                            pass

                    # print(name)

                Scheme_Portfolio_Data.objects.filter(
                    id=scheme_data.id).update(parsed=False)
                print("columns present")
                #
            else:
                print(Fore.RED + "unable to read data key columns missing")
                # raise Exception("unable to read data key columns missing")
        else:
            print(Fore.RED + "fund itself not found")
            # amc_process.addLog("fund not found ", )
            # raise Exception("found itself not found")

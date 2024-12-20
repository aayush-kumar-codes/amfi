from todo.models import AMC, Scheme, Nav, MFDownload, NavSerializer
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, MFDownloadSerializer


import requests
import datetime

from todo.logs import addLogs, startLogs

amc_no_start = 1
amc_no_end = 75


# this function mainly check if any new amc is found
# if yes add it to db for processing its historical data
def download_mf_historical_data():
    print("Starting mf download")

    amc_no, amc_id, is_new_amc = find_amc_no_to_process()

    if amc_no == 999:
        print("all amcs completed!")

        # amc = AMC.objects.order_by("amc_no").first()
        # print(amc)
        # # return

        # # one time temporary to check if missed any amc

        # start = getattr(amc, "id")

        # if start < 100:
        #     amc_no = start + 1
        #     AMC.objects.get(pk=amc.id).update(next_amc_no=amc_no)
        #     if AMC.objects.filter(amc_no=amc_no).count() > 0:
        #         pass
        #     else:
        #         return

        # else:
        return

    print("checking for amc no ", amc_no)

    if amc_id != -1:
        # if amc_id is -1 this means this is a new amc. so nothing to update or check
        count = MFDownload.objects.filter(
            amc_id=amc_id, has_data=False).count()

        if(count > 2):
            # this means we didn't find data when parsing url to consicutive times
            # which means for sure amc data is finished
            print("data completed for amc ", amc_no)
            AMC.objects.filter(amc_no=amc_no).update(parsed=True)
            return

    days_gap = 90
    try:

        mfdownload = MFDownload.objects.filter(
            amc_id=amc_id).order_by('end_date').first()

        ser = MFDownloadSerializer(mfdownload)

        if ser.data["amc_id"] is None:
            raise MFDownload.DoesNotExist('Record does not exist.')

        start = datetime.datetime.today()
        end = (datetime.datetime.today() - datetime.timedelta(days=days_gap))
        ser.data["start_date"] = start.strftime("%Y-%m-%d")
        ser.data["end_date"] = end.strftime("%Y-%m-%d")

        if ser.data["end_time"] is None and False:
            # this means previous script didn't run properly. so parsing it again
            # it dangenours can go in infite loop. better not do this for now
            start = ser.data["start_date"]
            start = datetime.datetime.strptime(
                start, '%Y-%m-%d')
            end = (start -
                   datetime.timedelta(days=days_gap))
        else:

            if is_new_amc == True:
                # this means parsing is completed and we are trying new amc
                # then start/end date should be start from today not the old date
                pass
            else:
                start = ser.data["end_date"]
                start = datetime.datetime.strptime(
                    start, '%Y-%m-%d')
                end = (start -
                       datetime.timedelta(days=days_gap))

        # MFDownload.objects.filter(pk=mfdownload.id).update(start_date=start, end_date=end,
        #                   start_time=datetime.datetime.now(), end_time=None)

        mfdownload = MFDownload(
            amc_id=amc_id, start_date=start, end_date=end, start_time=datetime.datetime.now())
        mfdownload.save()

    except MFDownload.DoesNotExist:
        start = datetime.date.today()
        end = (start -
               datetime.timedelta(days=days_gap))
        mfdownload = MFDownload(
            amc_id=amc_id, start_date=start, end_date=end, start_time=datetime.datetime.now(), retry=0)
        mfdownload.save()

    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+str(amc_no)+'&tp=1&frmdt=' + \
        end.strftime("%d-%b-%Y")+'&todt='+start.strftime("%d-%b-%Y")

    print(start)
    print(end)

    log = startLogs("download_mf_historical_data", {
        "url": url
    })
    res = do_process_data(url, amc_no, log)

    if res is False:
        # data didn't come from amfi url which menas false
        MFDownload.objects.filter(pk=mfdownload.id).update(
            end_time=datetime.datetime.now(), has_data=False)
    else:
        # data came we are just update the end time
        MFDownload.objects.filter(pk=mfdownload.id).update(
            end_time=datetime.datetime.now())

    print("Completed mf download")


# this is mainly a command line function to download amc data for a specific dates
def download_mf_input(amc_id, start, end):
    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+str(amc_id)+'&tp=1&frmdt=' + \
        start.strftime("%d-%b-%Y")+'&todt='+end.strftime("%d-%b-%Y")
    do_process_data(url, amc_id)


# this is to download mutual fund daily nav. we download always for last 3 days
def schedule_daily_nav_download():
    date = datetime.date.today()
    # url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
    #     date.strftime("%Y-%m-%d")
    url = "https://www.amfiindia.com/spages/NAVAll.txt?t=" + \
        date.strftime("%Y%m%d000000")
    log = startLogs("schedule_daily_nav_download", {
        "url": url
    })
    do_process_data(url, -1, log)
    date = datetime.date.today() - datetime.timedelta(days=1)
    # url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
    #     date.strftime("%Y-%m-%d")
    url = "https://www.amfiindia.com/spages/NAVAll.txt?t=" + \
        date.strftime("%Y%m%d000000")
    log = startLogs("schedule_daily_nav_download", {
        "url": url
    })
    do_process_data(url, -1, log)
    date = datetime.date.today() - datetime.timedelta(days=2)
    # url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
    #     date.strftime("%Y-%m-%d")

    log = startLogs("schedule_daily_nav_download", {
        "url": url
    })
    url = "https://www.amfiindia.com/spages/NAVAll.txt?t=" + \
        date.strftime("%Y%m%d000000")
    do_process_data(url, -1, log)


# this is to process nave for a single date
def download_mf_input_date(date):
    # process mf data only for a single day for all mfs
    # url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
        # date.strftime("%Y-%m-%d")
    url = "https://www.amfiindia.com/spages/NAVAll.txt?t=" + \
        date.strftime("%Y%m%d000000")
    do_process_data(url, -1)


amc_list = {}
scheme_list = {}


def fetch_amc(amc_name):
    if amc_name in amc_list:
        return amc_list[amc_name]

    try:
        amc = AMC.objects.get(name=amc_name)
        amc_list[amc_name] = amc
        return amc
    except AMC.DoesNotExist:
        return False


def fetch_or_save_amc(amc_name, amc_no):
    # this will cache amc name and we don't need to alwways fire sql query
    if amc_name in amc_list:
        return amc_list[amc_name]
    try:
        amc = AMC.objects.get(name=amc_name)
    except AMC.DoesNotExist:
        if amc_no != -1:
            amc = AMC(name=amc_name, amc_no=amc_no)
            amc.save()

    amc_list[amc_name] = amc
    return amc


def fetch_or_save_scheme(fund_code, amc, scheme_category, scheme_type, scheme_sub_type, fund_name, fund_option, fund_type, amc_no, line):
    # this will cache scheme and we don't need to alwways fire sql query
    scheme_unique = fund_code
    if scheme_unique in scheme_list:
        return scheme_list[scheme_unique]
    try:
        scheme = Scheme.objects.get(
            fund_code=fund_code)

        if len(getattr(scheme, "line").strip()) == 0:
            Scheme.objects.filter(pk=scheme.id).update(line=line)

        if getattr(scheme, "fund_name") != fund_name:
            # this can be removed after sometime
            print("old fund name ", getattr(scheme, "fund_name"),
                  " new fund name ", fund_name)
            # Scheme.objects.filter(pk=scheme.id).update(fund_name=fund_name)

    except Scheme.DoesNotExist:
        # amc_no -1 means this is called from daily nav update process and we cannot save scheme from there at all
        if amc_no != -1:
            print(Scheme.objects.filter(
                fund_code=fund_code).query)

            print(scheme_category)

            try:
                scheme = Scheme(
                    scheme_category=scheme_category,
                    scheme_type=scheme_type,
                    scheme_sub_type=scheme_sub_type,
                    fund_code=fund_code,
                    fund_name=fund_name,
                    fund_option=fund_option,
                    fund_type=fund_type,
                    amc=amc,
                    line=line
                )
                scheme.save()
            except Exception as e:
                print(e)

        else:
            return None
    if scheme:
        scheme_list[scheme_unique] = scheme
    return scheme


def find_amc_no_to_process():
    # on amfi website all amc have different no and they are not in serial order.
    # so we need to keep checkin amc's until we get data and skip if data not found

    if AMC.objects.all().count() > 0:
        try:
            amc = AMC.objects.filter(parsed=False)
            # this wiered logic because initially code was written based on single amc always
            # now changed to multiple at a time
            if amc.count() == 0:
                amc = AMC.objects.get(parsed=False)
            else:
                amc = AMC.objects.filter(
                    parsed=False).order_by("amc_no").first()

            # this mean there is an amc which still has data being parsed
            # so simply continue with that
            ser = AMCSerializer(amc)
            amc_no = ser.data["amc_no"]
            amc_id = amc.id
            is_new_amc = False
        except AMC.DoesNotExist:
            # if there is no amc being parsed then need to find the
            # last amc i.e amc which max amc_no
            amc = AMC.objects.all().order_by("-amc_no").first()
            ser = AMCSerializer(amc)
            print(ser.data)
            if ser.data["next_amc_no"] == 0:
                amc_no = int(ser.data["amc_no"])+1
            else:
                amc_no = int(ser.data["next_amc_no"])+1

            # above if condition is due to a problem that all amc_no are not in sequence
            # e.g after amc no 5 there is no amc with no 6 rather to 7.
            # because our code works only incrementally and to solve this problem have added
            # another db column next_amc_no which stores these increments where amc no is missing

            AMC.objects.filter(pk=amc.id).update(next_amc_no=amc_no)
            amc_id = -1
            is_new_amc = True
            if amc_no > amc_no_end:
                print("all amcs completed")
                return 999, 999, False

    else:
        # this mean there is no amc is db.
        # db is fully empty so start from 1
        amc_no = amc_no_start

    return amc_no, amc_id, is_new_amc


def do_process_data(url, amc_no, log_id=False):
    print(url)
    response = requests.get(url)

    mf_nav_data = response.text.splitlines()

    scheme_code_index = 0
    scheme_name_index = 1
    nav_index = 4
    date_index = 7

    colums = mf_nav_data[0].split(";")

    try:
        scheme_code_index = colums.index("Scheme Code")
        scheme_name_index = colums.index("Scheme Name")
        nav_index = colums.index("Net Asset Value")
        date_index = colums.index("Date")
    except ValueError:
        print("no more data")
        print(url)
        if log_id is not False:
            addLogs({
                "type": "error",
                "message": "file response doesn't have valid data unable to find one of the columns from Scheme Code , Name, NAV, Date"
            }, log_id)
        return False

    amc_name = ""

    print("valid data found", len(mf_nav_data))

    if log_id is not False:
        addLogs({
            "type": "log",
            "message": "valid data found starting to process now " + str(len(mf_nav_data))
        }, log_id)

    scheme_category = ""
    scheme_type = ""
    scheme_sub_type = ""

    for line in mf_nav_data[1:]:
        if len(line.strip()) > 0:
            if log_id is not False:
                addLogs({
                    "type": "log",
                    "message": line
                }, log_id)

            # print(line)

            if line.find(";") != -1:
                # df = pd.DataFrame(line.split(';'), index=colums)
                # print(df)

                fund_types = ["direct", "regular", "growth",
                              "dividend", "bonus", "reinvestment"]

                mf_data = line.split(";")

                scheme_data = mf_data[scheme_name_index].split("-")

                # - is crticial but problem some fund names have - in build in this.
                # below logic skips this totally causing problem with scheme name
                # so we need identify fund type and option and rest of the part include - is part of schmeme name

                duplicate_scheme_date = [scheme_data[0]]

                for data_point in scheme_data[1:]:
                    found = False
                    for t in fund_types:
                        if t in data_point.lower():
                            found = True
                            break
                    if found == False:
                        duplicate_scheme_date.append(data_point)

                    # problem with this logic. there are funds like UTI Regular Savings Fund - Direct Plan
                    # not sure solution for this

                scheme_name_new = " ".join(duplicate_scheme_date)
                scheme_name_new = scheme_name_new.strip()

                scheme_name_new = scheme_name_new.replace("  ", " ")

                if len(mf_data[scheme_name_index].split("-")) == 3:
                    # fund_name = mf_data[scheme_name_index].split(
                        # "-")[0].strip()
                    fund_option = mf_data[scheme_name_index].split(
                        "-")[1].strip()
                    fund_type = mf_data[scheme_name_index].split(
                        "-")[2].strip()
                else:
                    if len(mf_data[scheme_name_index].split("-")) == 2:
                        # fund_name = mf_data[scheme_name_index].split(
                        #     "-")[0].strip()
                        fund_option = ""
                        fund_type = mf_data[scheme_name_index].split(
                            "-")[1].strip()
                    else:
                        # fund_name = mf_data[scheme_name_index].split(
                        #     "-")[0].strip()
                        fund_option = ""
                        fund_type = ""

                # print(fund_type)
                # print(fund_option)

                # print("Direct" in line)
                # print("Growth" in line)

                if "direct" in line.lower():
                    fund_type = "Direct"
                else:
                    fund_type = "Regular"

                if "unclaimed" in line.lower():
                    continue

                if "growth" in line.lower():
                    fund_option = "Growth"
                    if "bonus" in line.lower():
                        fund_option = "Growth Bonus"

                    # sometimes find its has growth in it. this is causing issue
                    if "dividend" in line.lower():
                        fund_option = "Dividend"

                    if "segregated" in line.lower():
                        # these are funds having segregated portfolio
                        fund_option = "Segregated"

                if fund_type == "Direct" and fund_option == "Growth":

                    # print("here")
                    if amc_no == -1:
                        amc = fetch_amc(amc_name)
                        if amc == False:
                            print("amc name doesn't exist ", amc_name)
                            if log_id is not False:
                                addLogs({
                                    "type": "alert",
                                    "message": "AMC not found " + amc_name
                                }, log_id)
                            continue
                    else:
                        amc = fetch_or_save_amc(amc_name, amc_no)

                    # print(mf_data[0])

                    # ser = AMCSerializer(amc)
                    # print(ser.data)

                    if scheme_type == "Balanced":
                        scheme_type = "Hybrid Scheme"

                    if scheme_type == "Liquid":
                        scheme_type = "Debt Scheme"

                    if "Closed" in scheme_category:
                        # we are skipping closed ended schemes
                        # print(scheme_category)
                        continue

                    # print(amc_no, "====" , mf_data[scheme_code_index])
                    scheme = fetch_or_save_scheme(
                        mf_data[scheme_code_index], amc, scheme_category, scheme_type, scheme_sub_type, scheme_name_new, fund_option, fund_type, amc_no, line)

                    if scheme is None:
                        continue



                    # continue  # temp code

                    # ser = SchemeSerializer(scheme)
                    # print(ser.data)

                    print("saving to db ", line)

                    if log_id is not False:
                        addLogs({
                            "type": "log",
                            "message": "saving to db " + line
                        }, log_id)

                    date_time_str = mf_data[date_index]
                    date_time_obj = datetime.datetime.strptime(
                        date_time_str, '%d-%b-%Y')

                    try:
                        nav = Nav.objects.get(
                            date=date_time_obj, scheme=scheme)

                        ser = NavSerializer(nav)

                        if ser.data["nav"] != mf_data[nav_index]:
                            Nav.objects.filter(
                                pk=nav.id).update(nav=mf_data[nav_index])

                    except Nav.DoesNotExist:
                        try:
                            nav = Nav(nav=mf_data[nav_index],
                                      date=date_time_obj, scheme=scheme)
                            nav.save()
                        except Exception as e:
                            print(e)
                            print(scheme)
                            if log_id is not False:
                                addLogs({
                                    "type": "error",
                                    "message": "error in saving nav " + str(e)
                                }, log_id)
                            pass

            else:
                if line.find(")") != -1:
                    x1 = line.find("(")
                    scheme_category = line[:x1].strip()
                    x1 = x1+1
                    scheme_type = line[x1:-1].split("-")[0].strip()
                    if len(line[x1:-1].split("-")) == 2:
                        scheme_sub_type = line[x1:-1].split("-")[1].strip()
                    else:
                        scheme_sub_type = ""

                    scheme_category = scheme_category
                    scheme_type = scheme_type
                    scheme_sub_type = scheme_sub_type
                else:
                    print("amc")
                    print(line.strip())
                    amc_name = line.strip()
                    pass

    return True

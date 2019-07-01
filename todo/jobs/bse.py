import requests
import logging
import json
import datetime
import urllib.parse


from todo.models import Index, IndexData

# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# https://www.nseindia.com/products/dynaContent/equities/indices/historical_pepb.jsp?indexName=NIFTY%20NEXT%2050&fromDate=02-04-2018&toDate=01-07-2018&yield1=undefined&yield2=undefined&yield3=undefined&yield4=all
# https://www.nseindia.com/products/dynaContent/equities/indices/historical_pepb.jsp?indexName=NIFTY%20NEXT%2050&fromDate=02-Apr-2018&toDate=01-Jul-2018&yield1=undefined&yield2=undefined&yield3=undefined&yield4=all
bse_indexes = [
    "SENSEX"
]


def process_bse_daily():
    for name in bse_indexes:
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today() - datetime.timedelta(days=7)
        latest_index = Index.objects.get(name=name, type="BSE")
        process_data(name, start_date, end_date, latest_index)


def process_bse_historial():
    days = 90
    index = 0

    try:
        latest_index = Index.objects.get(parsed=False, type="BSE")
        # latest_index = Index.objects.filter(
        #     parsed=False).all().order_by("-end_date").first()
        name = latest_index.name

        start_date = getattr(latest_index, "end_date")
        # start_date = datetime.datetime.strptime(
        #     start_date, '%Y-%m-%d')
        # start_end = latest_index.end_date
        print(start_date)
        end_date = start_date - datetime.timedelta(days=days)
    except Index.DoesNotExist:
        index = Index.objects.filter(type="BSE").all().count()
        name = urllib.parse.quote(bse_indexes[index])
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today() - datetime.timedelta(days=days)
        latest_index = Index(
            name=name,
            start_date=start_date,
            end_date=end_date,
            type="BSE"
        )
        latest_index.save()

    print(name)
    print(start_date)
    print(end_date)

    res = process_data(name, start_date, end_date, latest_index)

    if res:
        Index.objects.filter(pk=latest_index.id).update(
            start_date=start_date, end_date=end_date)
    else:
        Index.objects.filter(pk=latest_index.id).update(parsed=True)


def process_data(name, start_date, end_date, latest_index):
    url = "https://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex=SENSEX&dtFromDate=" + \
        start_date.strftime("%d-%m-%Y")+"&dtToDate=" + \
        end_date.strftime("%d-%m-%Y")

    response = requests.get(url)

    data = response.text

    data = response.text.splitlines()

    index_data = {}

    for row in data:
        cols = row.split(",")

        if (len(cols) > 5) & (cols[0] != "Date"):
            date = cols[0]
            open = cols[1]
            high = cols[2]
            low = cols[3]
            close = cols[4]
            index_data[date] = {
                "open": open,
                "high": high,
                "low": low,
                "close": close
            }

    if bool(index_data):
        for date in index_data:
            try:
                print(date)
                IndexData.objects.get(index=latest_index, date=datetime.datetime.strptime(
                    date, '%d-%b-%Y'))
                # data exists nothing to do
            except IndexData.DoesNotExist:
                index_data_obj = IndexData(
                    index=latest_index,
                    date=datetime.datetime.strptime(
                        date, '%d-%b-%Y'),
                    open=index_data[date]['open'],
                    close=index_data[date]['close'],
                    high=index_data[date]['high'],
                    low=index_data[date]['low'],
                    pe=index_data[date]['pe'] if 'pe' in index_data[date] else 0,
                    pb=index_data[date]['pb'] if 'pb' in index_data[date] else 0,
                    div=index_data[date]['div'] if 'div' in index_data[date] else 0
                )
                index_data_obj.save()

        return True
    else:
        return False
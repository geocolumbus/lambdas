from datetime import datetime
from datetime import timedelta
import urllib3

http = urllib3.PoolManager()

river_name = 'olentangy'
alum_creek_site_code = '03229000'
olentangy_site_code = '03226800'
scioto_site_code = '03230700'

if river_name == 'alum_creek':
    site_code = alum_creek_site_code
elif river_name == 'olentangy':
    site_code = olentangy_site_code
elif river_name == 'scioto':
    site_code = scioto_site_code
else:
    site_code = 0


def getCurrentDate():
    return f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-04:00"


def getPastDate():
    return f"{(datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S')}-04:00"


def getRiverUrl(site_code, data_code):
    url = f"https://waterservices.usgs.gov/nwis/iv/?sites={site_code}&parameterCd={data_code}"
    url += f"&startDT={getPastDate()}&endDT={getCurrentDate()}"
    url += "&siteStatus=all&format=rdb"
    # print(url)
    return url


def convertStringToInt(string):
    try:
        return int(string)
    except:
        return 0


def get_river_level_trend(river_level_data):
    river_level_rows = river_level_data.split("\n")
    river_level_rows = [row for row in river_level_rows if "USGS\t" in row]
    first_depth = float(river_level_rows[-8].split("\t")[4])
    last_depth = float(river_level_rows[-1].split("\t")[4])
    depth_change = round(last_depth - first_depth, 1)
    return depth_change


def river_level(site_code, river_name):
    response = http.request("GET", getRiverUrl(site_code=site_code, data_code="00065"))
    river_level_data = response.data.decode("utf-8")
    river_level_trend = get_river_level_trend(river_level_data)
    river_level_text = "increase"
    river_level_text = ""
    if river_level_trend != 0.0:
        if river_level_trend < 0:
            river_level_text = "decrease"
        river_level_text = f" with a {river_level_trend} feet {river_level_text} in the past " \
                           f"two hours."
    depth = "no data"
    try:
        depth = int(float(response.data.decode('utf-8').split("\n")[-2].split("\t")[4]))
    except:
        pass

    response = http.request("GET", getRiverUrl(site_code=site_code, data_code="00060"))
    flow = "no data"
    try:
        flow = int(float(response.data.decode('utf-8').split("\n")[-2].split("\t")[4]))
    except:
        pass

    return f"The Olentangy river is {depth} feet deep and flowing at {flow} cubic feet per second" \
           f"{river_level_text}"


def floatToInteger():
    return int(float(1.5))


def lambda_handler(event, context):
    return {'statusCode': 200,
            'body': {"message": river_level(site_code=site_code, river_name=river_name)}}


print(lambda_handler(None, None))

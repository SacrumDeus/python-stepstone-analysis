
import geopy
import pandas as pd
import re as regex
import unicodedata as unicode
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pymongo import MongoClient
from time import sleep
from types import NoneType

def transformLocation(loc, name):
    
    # variable definition
    location = dict.fromkeys(["longitude", "latitude", "country", "city", "postCode", "street", "streetNumber", "offCommunityKey"])
    zipCodesExclude = ["09107", "10888", "10889", "10900", "11010", "11011", "11012", "11013", "11014", "11015", "11016", "11017", 
                       "11018", "11019", "11512", "13342", "13343", "20533", "24932", "28107", "32750", "33333", "36028", "36029", 
                       "38436", "40192", "40206", "50427", "50600", "55100", "60256", "60308", "65473", "65926", "66100", "67056", 
                       "80313", "80788", "81363", "82030", "89516", "90318", "90319", "96435 ", "96444", "74167"]

    # init locator service
    geoLocator = Nominatim(user_agent="stepstone-preprocessing")

    # we need to wait 1 second to take account of Nominatim usage policy (using ratelimiter)
    reverse = RateLimiter(geoLocator.reverse, min_delay_seconds=1)
    geocode = RateLimiter(geoLocator.geocode, min_delay_seconds=1)

    try:

        # location can be type of string or dictionary -> proper handling
        if isinstance(loc, dict):

            ## check, if we got longitude and latitude
            if loc.get("latitude") and loc.get("longitude"):

                # we need to convert long+lat to string 0=lat 1=long
                geoString = f'{loc.get("latitude")}, {loc.get("longitude")}'.format(loc["latitude"], loc["longitude"])

                # verify, if requirements are satisfied
                if loc.get("country") and loc.get("city") and loc.get("postalCode") and loc.get("street") and loc.get("streetNumber"):

                    # we can fill structure from given data
                    location["longitude"] = loc.get("longitude")
                    location["latitude"] = loc.get("latitude")
                    location["country"] = loc.get("country")
                    location["city"] = loc.get("city")
                    location["postCode"] = loc.get("postalCode")
                    location["street"] = loc.get("street")
                    location["streetNumber"] = loc.get("streetNumber")

                else:

                    # fill long+lat in structure
                    location["longitude"] = loc.get("longitude")
                    location["latitude"] = loc.get("latitude")
                    
                    # process reverse geocoding
                    rawLocation = reverse(geoString, addressdetails=True ,timeout=5).raw

                    # extract details into location structure
                    location["longitude"] = rawLocation.get("lon")
                    location["latitude"] = rawLocation.get("lat")
                    location["country"] = rawLocation.get("address").get("country_code") if rawLocation.get("address").get("country_code") else ""
                    
                    if rawLocation.get("address").get("city"):
                        location["city"] = rawLocation.get("address").get("city") if rawLocation.get("address").get("city") else ""
                    elif rawLocation.get("address").get("town"):
                        location["city"] = rawLocation.get("address").get("town") if rawLocation.get("address").get("town") else ""
                    elif rawLocation.get("address").get("county"):
                        location["city"] = rawLocation.get("address").get("county") if rawLocation.get("address").get("county") else "" 
                    elif rawLocation.get("address").get("state"):
                        location["city"] = rawLocation.get("address").get("state") if rawLocation.get("address").get("state") else "" 
                    else:
                        print(rawLocation)
                        raise ValueError("There is no valid town/city/county for this address")

                    location["postCode"] = rawLocation.get("address").get("postcode") if rawLocation.get("address").get("postcode") else ""
                    location["street"] = rawLocation.get("address").get("road") if rawLocation.get("address").get("road") else ""
                    location["streetNumber"] = rawLocation.get("address").get("house_number") if rawLocation.get("address").get("house_number") else ""

            else:

                # get variables
                country = loc.get("country") if loc.get("country") else None
                city = loc.get("city") if loc.get("city") else None
                postcode = loc.get("postalCode") if loc.get("postalCode") else None
                street = loc.get("street") if loc.get("street") else None
                streetNumber = loc.get("streetNumber") if loc.get("streetNumber") else None

                # create seach string
                if street:

                    # create geoString with street
                    geoString = street

                    # street number is not that important
                    if streetNumber:
                        geoString = geoString + " " + streetNumber

                else:

                    # create geoString with company name
                    geoString = name

                # add postcode
                if postcode:

                    # check for exclude list
                    if postcode not in zipCodesExclude:
                        geoString = geoString + ", " + postcode
                    else:
                        geoString = geoString + ", "

                # add city
                if city:

                    # some city strings contains a location -> Norderstedt bei Hamburg
                    if regex.search("\sbei\s", city):
                        city = city.split(" bei ")[0]

                    geoString = geoString + " " + city
                
                # add country
                if country:
                    geoString = geoString + ", " + country

                # call geocoding service
                rawLocation = geocode(geoString, addressdetails=True ,timeout=5).raw

                # save data to location structure
                location["longitude"] = rawLocation.get("lon")
                location["latitude"] = rawLocation.get("lat")
                location["country"] = rawLocation.get("address").get("country_code") if rawLocation.get("address").get("country_code") else ""

                if rawLocation.get("address").get("city"):
                    location["city"] = rawLocation.get("address").get("city") if rawLocation.get("address").get("city") else ""
                elif rawLocation.get("address").get("town"):
                    location["city"] = rawLocation.get("address").get("town") if rawLocation.get("address").get("town") else ""
                elif rawLocation.get("address").get("county"):
                    location["city"] = rawLocation.get("address").get("county") if rawLocation.get("address").get("county") else "" 
                elif rawLocation.get("address").get("state"):
                    location["city"] = rawLocation.get("address").get("state") if rawLocation.get("address").get("state") else "" 
                else:
                    print(rawLocation)
                    raise ValueError("There is no valid town/city/county for this address")

                location["postCode"] = rawLocation.get("address").get("postcode") if rawLocation.get("address").get("postcode") else ""
                location["street"] = rawLocation.get("address").get("road") if rawLocation.get("address").get("road") else ""
                location["streetNumber"] = rawLocation.get("address").get("house_number") if rawLocation.get("address").get("house_number") else ""
            
        elif isinstance(loc, str):

            # we need to simplify name (use first word only (DHL Consulting GmbH => DHL, ...))
            simpleName = name.split(" ")[0]

            # we only got a string to decode
            geoString = simpleName + ", " + loc

            # geocode this string (if exception, use city only)
            try:
                rawLocation = geocode(geoString, addressdetails=True ,timeout=5).raw
            except:
                rawLocation = geocode(loc, addressdetails=True ,timeout=5).raw

            # extract details into location structure
            location["longitude"] = rawLocation.get("lon")
            location["latitude"] = rawLocation.get("lat")
            location["country"] = rawLocation.get("address").get("country_code") if rawLocation.get("address").get("country_code") else ""
            
            if rawLocation.get("address").get("city"):
                location["city"] = rawLocation.get("address").get("city") if rawLocation.get("address").get("city") else ""
            elif rawLocation.get("address").get("town"):
                location["city"] = rawLocation.get("address").get("town") if rawLocation.get("address").get("town") else ""
            elif rawLocation.get("address").get("county"):
                location["city"] = rawLocation.get("address").get("county") if rawLocation.get("address").get("county") else "" 
            elif rawLocation.get("address").get("state"):
                location["city"] = rawLocation.get("address").get("state") if rawLocation.get("address").get("state") else "" 
            else:
                print(rawLocation)
                raise ValueError("There is no valid town/city/county for this address")

            location["postCode"] = rawLocation.get("address").get("postcode") if rawLocation.get("address").get("postcode") else ""
            location["street"] = rawLocation.get("address").get("road") if rawLocation.get("address").get("road") else ""
            location["streetNumber"] = rawLocation.get("address").get("house_number") if rawLocation.get("address").get("house_number") else ""

        elif isinstance(loc, NoneType):

            # noneType = None -> there are no location information
            return location

        # load ARS mapping table
        ars = pd.read_csv("data/Postcode_ARS_mapping_table.csv", encoding="utf-8", sep=";", dtype=str)

        # validate country code (ARS is only working for germany)
        if location["country"].lower() == 'de':

            # map official community key (ARS) for Regionalstatistik
            if location["postCode"]:

                # check, if we found a location
                if not ars.loc[ars["postcode"] == location["postCode"]].empty:
                    arsVal = ars.loc[ars["postcode"] == location["postCode"]]
                else:
                    arsVal = ars.loc[ars["cityname"] == location["city"]]

            else:
                arsVal = ars.loc[ars["cityname"] == location["city"]]

            # convert offCommunityKey
            if not arsVal.empty:
                location["offCommunityKey"] = arsVal.iloc[0]["ARS_region"]+arsVal.iloc[0]["ARS_governorate"]+arsVal.iloc[0]["ARS_county"]+arsVal.iloc[0]["ARS_city"]
            else:
                print(f'[ERROR]: no mapping found for city {location.get("postcode")} {location.get("city")}')

        # return new location structure
        return location

    except Exception as err:

        # message
        print(f"[ERROR]: an error occured during process of location for company {name} -> empty object returned")
        print(err)

        # if a error occured -> return an empty object (for integrity)
        return location

def transformSectors(sec):

    # variable definition
    sectors = []

    # if sectors is empty none -> we can return an empty list
    if not sec:
        return sectors

    # sectors is type of list with dicts
    for sector in sec:
        sectors.append(sector["sectorId"])

    # return sectors
    return sectors

def transformText(text):

    # variable definition
    newText = ""

    # if text is empty -> we can return an empty value
    if text:
        newText = text
    else:
        return newText

    # convert unicode data to NFC
    newText = unicode.normalize("NFC", newText)

    # replace any non-word character
    newText = regex.sub("\W+", " ", newText)
    
    # convert camelcase to space separated words
    newText = regex.sub("([a-z])([A-Z])", "\g<1> \g<2>", newText)

    # string to lower
    newText = newText.lower()

    # strip the text
    newText = newText.strip()

    # return new text
    return newText

def transformRating(rat):

    # variable definition
    rating = dict.fromkeys(["stars", "total", "subrating"])

    # some of our definitions has a default value
    rating["stars"] = dict.fromkeys(["1", "2", "3", "4", "5"])
    rating["subrating"] = dict.fromkeys(["office", "culturePeople", "trainingDevelopment", "workLifeBalance", "career"])

    # set default values
    rating["stars"]["1"] = int(0)
    rating["stars"]["2"] = int(0)
    rating["stars"]["3"] = int(0)
    rating["stars"]["4"] = int(0)
    rating["stars"]["5"] = int(0)
    rating["total"] = int(0)
    rating["subrating"]["office"] = float(0)
    rating["subrating"]["culturePeople"] = float(0)
    rating["subrating"]["trainingDevelopment"] = float(0)
    rating["subrating"]["workLifeBalance"] = float(0)
    rating["subrating"]["career"] = float(0)

    # validate rat structure
    if not rat:
        return rating

    # map ratings
    rating["total"] = rat.get("overall") if rat.get("overall") else rating["total"]
    rating["stars"]["1"] = rat.get("participation").get("1") if rat.get("participation").get("1") else rating["stars"]["1"]
    rating["stars"]["2"] = rat.get("participation").get("2") if rat.get("participation").get("2") else rating["stars"]["2"]
    rating["stars"]["3"] = rat.get("participation").get("3") if rat.get("participation").get("3") else rating["stars"]["3"]
    rating["stars"]["4"] = rat.get("participation").get("4") if rat.get("participation").get("4") else rating["stars"]["4"]
    rating["stars"]["5"] = rat.get("participation").get("5") if rat.get("participation").get("5") else rating["stars"]["5"]
    rating["subrating"]["office"] = rat.get("subrating").get("office") if rat.get("subrating").get("office") else rating["subrating"]["office"]
    rating["subrating"]["culturePeople"] = rat.get("subrating").get("culturePeople") if rat.get("subrating").get("culturePeople") else rating["subrating"]["culturePeople"]
    rating["subrating"]["trainingDevelopment"] = rat.get("subrating").get("trainingDevelopment") if rat.get("subrating").get("trainingDevelopment") else rating["subrating"]["trainingDevelopment"]
    rating["subrating"]["workLifeBalance"] = rat.get("subrating").get("workLifeBalance") if rat.get("subrating").get("workLifeBalance") else rating["subrating"]["workLifeBalance"]
    rating["subrating"]["career"] = rat.get("subrating").get("career") if rat.get("subrating").get("career") else rating["subrating"]["career"]

    # return new rating
    return rating

def transformTurnover(to):

    # variable definition
    turnover = None

    # check, if turnover is empty
    if not to:
        return turnover
    else: 
        turnover = to

    # we need to convert special cases
    if regex.search("\d.*(mrd|milliarden|mio|millionen)", turnover, regex.IGNORECASE):

        # split at comma
        split = turnover.split(",")
        
        # handle length of split list
        if len(split) == 1:
            split.append("")

        # prepare items
        first =  regex.sub("\D", "", split[0])
        second = regex.sub("\D", "", split[1]) if split[1] else ""

        # handle billion (mrd|milliarden) -> add 0s
        if regex.search("\d.*(mrd|milliarden)", turnover, regex.IGNORECASE):
            second = f"{second:0<9}"

        # handle million (mio|millionen) -> add 0s
        if regex.search("\d.*(mio|millionen)", turnover, regex.IGNORECASE):
            second = f"{second:0<6}"

        # create turnover from first+second
        turnover = first+second

    else:

        # only digits are relevant
        turnover = regex.sub("\D", "", turnover)

    # convert turnover (str) to turnover (int)
    if turnover:
        turnover = int(turnover)
    else:
        turnover = None

    # return new turnover
    return turnover

def transformWorkers (wrks):

    # variable definition
    workers = [None, None]

    # there are several formats
    # "10.000+"               -> [10000, None]
    # "120 Mitarbeiter"       -> [120, None]
    # "1001-5000"             -> [1001, 5000]
    # "201 - 500 Mitarbeiter" -> [201, 500]
    # None                    -> [None, None]

    # handle empty workers
    if not wrks:
        return workers

    # split string at "-"
    split = wrks.split("-")

    # if split does have only 1 item
    if len(split) == 1:
        split.append(None)

    # handle splits
    split[0] = regex.sub("\D", "", split[0]) if split[0] else None
    split[1] = regex.sub("\D", "", split[1]) if split[1] else None

    # create return value
    workers[0] = int(split[0]) if split[0] else None
    workers[1] = int(split[1]) if split[1] else None

    # return new workers
    return workers

def determineCompanyId (companyName):

    # handle empty company name
    if not companyName:
        return None

    # connect to server
    client = MongoClient("mongodb://localhost:27017/")

    # load database
    companies = client["stepstone-data"]["pCompany"]

    # we are going to read the company name directly from MongoDb
    mongoData = companies.find_one({"companyName": companyName}, {"companyId": 1, "_id": 0})

    # extract id from id
    id = mongoData.get("companyId", None) if mongoData else None

    # return id
    return id
# Preprocessing

After loading data from our data sources

* Stepstone
* Regionalstatistik
* ...

we need to process the data. Those data are stored in MongoDb. The preprocesing have the task to structurize the data and merge them with other data. After all data have been processed, the data will be stored in MongoDb in seperate collections. This will guard, that we dont have to crawl the data again or modify them.




```python
# packages
import pandas as pd
from pymongo import MongoClient

# custom functions
import preprocessingFunctions as core
```


```python
# global variables
newCompanies = []
newJobs = []
```

There are many data crawled. Those data wont fetch a particular structure, so we need to process them.

This processing will include features like replacing special chars (äÄ/öÖ/üÜ) with their substitutes or removing special characters like `\r\n` with a simple space character. Those characters will disrupt further text processing.

We also need to structure data like locations. These data are stored with different structures. This is reasoned by different data sources (job offer, company profile) and advertisers themselves who don't provide specific data. We will enhance this data that all will match the same pattern.

Each preprocessing step is described in detail.

**Important Note:**

> We are processing only data like *company profiles* or *job offers*. Processing data like *benefits* or *sectors* are not relevant for further processing or already in desired structure.

## Load data from MongoDB

First, we need to load all data from our data store MongoDB. MongoDB is storing all data we are processing. After finishing the task "Preprocessing", data will be stored in MongoDB in separate collections. This architecture guards the status quo of each data. We will not overwrite data, because we will always store the data in new collections.

This provides us the opportunity to restart a complete process without changing previos data.


```python
# connect to server
client = MongoClient("mongodb://localhost:27017/")

# load database
database = client["stepstone-data"]

# load data -> cursors are returned
companies = database["companies"].find({})
jobs = database["jobs"].find({})
```

## Process company data

We read all data from collection `stepstone-data > companies`. These data will include values like *company name*, *turnover* or *workers*. The further processing of those data will update those data.

**Important note for location:**

> We are using location service Nominatim, which is free for limited usage. 
> This results in limited search results. For example, searching for *SPIEGEL-Verlag Rudolf Augstein GmbH & Co. KG* in *Hamburg* returns no results. For this reason, we are trying to simplify the company name by using only the first word *SPIEGEL-Verlag*. 
>
> Even with this solution, sometimes we will get no results. If this issue occures, we are searching only with the city string *Hamburg* which returns a location, but this is not that accurate - we wont get any detail information like street or postcode (*Hamburg* itself has a range of 104 postcodes (Quelle: [Onlinestreet, 04.02.2022](https://onlinestreet.de/plz/Hamburg.html))
>
> The reason, why we aren't using a professional geocoding service like *Google Geocode API* is the pricing model of each of those services. We've tried it and each of the company names could be resolved by this service. However, a large dataset and the stage of development (we are running the process multiple times) will cause costs.
> 
> Estimated costs for *Google Geocode API* by an estimated usage of <100.000 requests:
> 
> | number of requests | estimated costs |
> | :----------------: | :-------------: |
> | 1.000              | USD 5.00        |
> | 10.000             | USD 50.00       |
> | 20.000             | USD 100.00      |
> | ...                | ...             |
> 
> There is a further problem, which occured on testing this function. Sometimes, companies do have their own postcodes like BMW. The postcode given by company profile on *stepstone* is 80788 while the official postcode is 80809. This is issued by many mailings every day.
>
> Examples for this special post codes are listed below:
>
> `"09107", "10888", "10889", "10900", "11010", "11011", "11012", "11013", "11014", "11015", "11016", "11017", "11018", "11019", "11512", "13342", "13343", "20533", "24932", "28107", "32750", "33333", "36028", "36029", "38436", "40192", "40206", "50427", "50600", "55100", "60256", "60308", "65473", "65926", "66100", "67056", "80313", "80788", "81363", "82030", "89516", "90318", "90319", "96435 ", "96444", "74167"`
>
> By excluding these post codes, we prevent issues by locating the address

**Mapping with DESTATIS / official community code**

The cities and regions in Germany are identified by an official community code (ger: Amtlicher Gemeindeschlüssel, ARS). We only got post codes from stepstone and the Nominatim API. Those postcodes cannot be used to identify a city with ARS. For further processing, we need to map the postcode with the community code. Therefore we downloaded a file from DESTATIS, which contains all postcodes and the ARS ([File download](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugJ/31122020_Auszug_GV.html)). This file is type of XLSX and is malformatted. This file contains multiple pages and many useless data. This file was processed manually to map the data. It was saved as CSV for performance reasons (XLSX input is pretty slow).



```python
# process every document from database -> doc is returned from cursor
for document in companies: 

    # create empty structure
    data = dict.fromkeys(["_id", "companyId", "companyName", "companyDescription", "sectors", "workers", "location", "rating", "turnover"])

    # move _id (ObjectID for identifying document) and other values
    data["_id"] = document.get("_id")
    data["companyId"] = document.get("id")
    data["companyName"] = document.get("company")
    data["companyDescription"] = core.transformText(document.get("about"))
    data["sectors"] = core.transformSectors(document.get("sectors"))
    data["workers"] = core.transformWorkers(document.get("workers"))
    data["location"] = core.transformLocation(document.get("location"), document.get("company"))
    data["rating"] = core.transformRating(document.get("rating"))
    data["turnover"] = core.transformTurnover(document.get("turnover"))

    # append new structure to newCompanies list
    newCompanies.append(data)
```

    [ERROR]: an error occured during process of location for company Chefkoch GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Herz- und Diabeteszentrum NRW -> empty object returned
    'NoneType' object has no attribute 'raw'
    {'place_id': 282373118, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', 'osm_type': 'relation', 'osm_id': 51477, 'boundingbox': ['47.2701114', '55.099161', '5.8663153', '15.0419309'], 'lat': '51.0834196', 'lon': '10.4234469', 'display_name': 'Deutschland', 'class': 'boundary', 'type': 'administrative', 'importance': 0.9896814891722548, 'icon': 'https://nominatim.openstreetmap.org/ui/mapicons//poi_boundary_administrative.p.20.png', 'address': {'country': 'Deutschland', 'country_code': 'de'}}
    [ERROR]: an error occured during process of location for company EOS Deutscher Inkasso-Dienst -> empty object returned
    There is no valid town/city/county for this address
    [ERROR]: an error occured during process of location for company ProSiebenSat.1 Media SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company EOS Holding -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Peek & Cloppenburg KG, Düsseldorf -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Tecan Software Competence Center GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Hays – Recruiting Experts Worldwide -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Brunel GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Lufthansa Technik AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: no mapping found for city None Bad Homburg vor der Höhe
    [ERROR]: an error occured during process of location for company PVS holding GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company EOS Technology Solutions GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Voith Group -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company ZEIT Verlagsgruppe -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Dr. Josef Raabe Verlags-GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Arvato Financial Solutions -> empty object returned
    'NoneType' object has no attribute 'raw'
    

Unfortunatelly, there may occure some errors. This errors occure due processing of malformatted data.
Nominatim only accepts data in a specific format (e.g. *Street* *StreetNumber*, *PostCode* *City*, *Country*). Some of these variables are not necessary to fill, but malformatted data will cause an empty return.

Examples after investigating manually:

* Willy-Brandt-Platz 1-3, 68161 Mannheim, DE => no data because street number **1-3** contains a range/special characters
* Mülheim a.d.R. => no data because abbreviations are used (**a.d.R**)
* Stiftsbergstraße 1, 74167 Neckarsulm, DE => no data because postcode is not a valid postcode by definition (see above)
* Postfach 10 39 22, 70034 Stuttgart, DE => no data because **Postfach 10 39 22** is not street

These examples are representative for most of errors, occuring during selection. We've managed to filter many errors by extending code, but all errors cannot be found and replaced.

After processing company data, we are going to save them in a new collection.

All company data now will match the same structure. This is important for further processes and evaluations.


```python
# we are already connected to database stepstone-data -> create new collection
dbCompanies = database["pCompany"]

# delete data if collection has data
if dbCompanies.count_documents({}) > 0:
    dbCompanies.delete_many({})
    
# store data
dbCompanies.insert_many(newCompanies)
```




    <pymongo.results.InsertManyResult at 0x1c875511dc0>



## Process job offer data

We already processed data from collection *companies*. For further processing we need structured job offer data as well. This will include transform data like *location* or text fields like *tasks* or *applicantProfile*.

**Important note for location:**

> see **1.2 - Process company data**
> 
> We are using location service Nominatim, which is free for limited usage.
> For further information please jump to **2 - Process company data**

**Mapping with DESTATIS / official community code**

> see **1.2 - Process company data**

The routine to structure location data is the same as used in **1.2 - Process company data**. This function will include all features to transform different structures and types to a dictionary of same structure.




```python
# process every document from database -> doc is returned from cursor
for document in jobs:
    
    # create empty structure
    data = dict.fromkeys(["_id", "jobId", "company", "companyId", "title", "location", "contractType", 
                          "workType", "introduction", "tasks", "applicantProfile", "companyOffer", "benefits"])

    # move _id (ObjectID for identifying document) and other values
    data["_id"] = document.get("_id")
    data["jobId"] = document.get("id")
    data["company"] = document.get("company")
    data["companyId"] = core.determineCompanyId(document.get("company"))
    data["title"] = document.get("jobTitle")
    data["location"] = core.transformLocation(document.get("location"), document.get("company"))
    data["contractType"] = document.get("contractType")
    data["workType"] = document.get("workType")
    data["introduction"] = core.transformText(document.get("introduction"))
    data["tasks"] = core.transformText(document.get("tasks"))
    data["applicantProfile"] = core.transformText(document.get("applicantProfile"))
    data["companyOffer"] = core.transformText(document.get("companyOffer"))
    data["benefits"] = document.get("benefits")

    # append new structure to newJobs list
    newJobs.append(data)
```

    [ERROR]: an error occured during process of location for company Atruvia AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company ONE LOGIC GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company ONE LOGIC GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NETZSCH Process Intelligence GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NETZSCH Process Intelligence GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Thalia Bücher GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company GLS IT Services GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Zühlke Engineering GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Helios IT Service GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Computer Futures -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company top itservices AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company CURACON GmbH Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company 1&1 -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company SVELTE scientific GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company sonnen GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Olympus Deutschland GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Horn & Company Data Analytics GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company MT AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company ONE LOGIC GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BWI GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BWI GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deutsche Bahn AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Strabag AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Wipro Technologies GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NETZSCH Process Intelligence GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NETZSCH Process Intelligence GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NETZSCH Process Intelligence GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Novelis Deutschland GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NETZSCH Process Intelligence GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company real.digital -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company adesso SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company IAV GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Sartorius Corporate Administration GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company EOS Holding -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company real.digital -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Kienbaum Consultants International GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NTT DATA Deutschland GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Smart InsurTech AG - ein Tochterunternehmen der Hypoport SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Techem Energy Services GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Zühlke Engineering GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company ONE LOGIC GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Kienbaum Consultants International GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company IQVIA Commercial GmbH & Co. OHG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company conplement AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company SCOOP Software GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Dataport AöR -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company conplement AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company conplement AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Strabag AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Strabag AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Strabag AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company AKDB -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company TWT GmbH Science & Innovation  -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company SoftwareONE Deutschland GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Springer-Verlag GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company MID GmbH  -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company TELUS International -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Profil Institut für Stoffwechselforschung GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company adesso SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PPI AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Cintellic GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Cintellic GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company CBRE GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Thalia Bücher GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company UNICEPTA GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Aalberts Surface Technologies GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Vattenfall -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company 1&1 -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Avanade Deutschland GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Capgemini Invent -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company IQVIA Commercial Software GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company IU Internationale Hochschule -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company StepStone GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company NextPharma GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: no mapping found for city None Bad Homburg vor der Höhe
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Regnology Germany GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Finanz Informatik GmbH & Co. KG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Ströer Content Group GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company flaschenpost SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company integration-factory GmbH & Co.KG  -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company TenneT TSO GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Helios IT Service GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company EOS Technology Solutions GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deutsche Bundesbank -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: no mapping found for city None Dessau
    [ERROR]: an error occured during process of location for company IU Internationale Hochschule -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Finanz Informatik GmbH & Co. KG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Tele Columbus Vertriebs GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BearingPoint GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company IU Internationale Hochschule -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Capgemini Invent -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Generali Deutschland AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BearingPoint GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Dorsch Holding GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Geberit Verwaltungs GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Capgemini Invent -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company SNP Schneider-Neureither & Partner SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company 1&1 -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BearingPoint GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company top itservices AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BearingPoint GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Senacor Technologies AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Senacor Technologies AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BearingPoint GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Willis Towers Watson GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company BearingPoint GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company adesso SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Vattenfall -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company msg systems ag -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company mgm consulting partners GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Willis Towers Watson GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Materna Information & Communications SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company KPMG AG Wirtschaftsprüfungsgesellschaft -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company EXXETA AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Cintellic GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company msg industry advisors AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deutsche Bahn AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deutsche Bahn AG -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company StepStone GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company flaschenpost SE -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company RTL Deutschland GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Capco - The Capital Markets Company GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Kienbaum Consultants International GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Kienbaum Consultants International GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Deloitte -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company Windhoff Group -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company msg systems ag -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company msg systems ag -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PwC -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company PerkinElmer LAS (Germany) GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company VWR International GmbH, part of Avantor -> empty object returned
    'NoneType' object has no attribute 'raw'
    [ERROR]: an error occured during process of location for company cytena GmbH -> empty object returned
    'NoneType' object has no attribute 'raw'
    

As described above, there may occure errors, which are triggered by malformatted location data. An example of some errors, which occure more often within this data are job descriptions, which are located in multiple cities:

* Passau, Frankfurt am Main, München
* Karlsruhe, München

These data cannot extracted from each. Moreover we do not expect a job offer, which is located in multiple towns.

After processing job offer data, we are going to save them in a new collection.

All job offer data now will match the same structure. This is important for further processes and evaluations.


```python
# we are already connected to database stepstone-data -> create new collection
dbJobs = database["pJobs"]

# delete data if collection has data
if dbJobs.count_documents({}) > 0:
    dbJobs.delete_many({})
    
# store data
dbJobs.insert_many(newJobs)
```




    <pymongo.results.InsertManyResult at 0x1c87f43b640>




```python

```

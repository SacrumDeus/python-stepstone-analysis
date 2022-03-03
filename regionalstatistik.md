# Extraction of socioeconomic variables

This notebook contains the extraction of county-level socioeconomic variables. This data is made available on the website www.regionalstatistik.de.

This website is based on the information system **genesis**. This information system is also used by other statistical websites such as www.bildungsmonitoring.de or https://www.statistikdaten.bayern.de/.

Genesis includes a SOAP/XML and a RESTful/JSON API for automatic data retrieval. For the programming language `R`, there exists a package with the name `wiesbaden` which contains functions for extracting data from this API. There is no comparable package for the programming language `Python`. 

To due this lack, we created an own module for extracting data fom a genesis information system. We studied the [genesis API documentaion](https://www-genesis.destatis.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf) and named our module `wiesbaden`. This module contains a class named `Genesis`. This class has methods for searching and extracting the data. The functionality was leant on the R package `wiesbaden` (method names and output format).

## Preparatory activities

The first step is to import the packages/modules needed.


```python
import pandas as pd
from pymongo import MongoClient

# our own package
import wiesbaden
```

Then we instantiate a new object of the class `Genesis` and call it `regiostat`. The `__init__` method sets the instance variables and checks if the database and userdata are correct. If not, a value error is raised.


```python
regiostat = wiesbaden.Genesis(database = "REGIO", username = "username", password = "password")
```

> **Important note:**
>
> Both parameters (username, password) has been deleted. Please register at [Regionalstatistik](https://www.regionalstatistik.de/genesis/online/) to get access to the data.

## Relevant data cubes

Before we can query the data, it is important to know the name of the data cubes which contain the variables needed. There are two opportunities to do this.

The **first opportunity** is the method `search_datacube("Keyword")`. This method returns the code of datacubes whose contents contain a certain keyword in a pandas data frame. The following query returns all data cubes which contain the  gross domestic product (in german "BIP").


```python
regiostat.search_datacube("BIP")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Code</th>
      <th>Content</th>
      <th>State</th>
      <th>Time</th>
      <th>LatestUpdate</th>
      <th>Information</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>82111BJ008</td>
      <td>VGR der Länder: Entstehungsrechnung, Bruttoinlandsprodukt, Bruttoinlandsprodukt je Erwerbstätigen, Bruttoinlandsprodukt je Einwohner, Deutschland, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:12:31h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>1</th>
      <td>82111KJ008</td>
      <td>VGR der Länder: Entstehungsrechnung, Bruttoinlandsprodukt, Bruttoinlandsprodukt je Erwerbstätigen, Bruttoinlandsprodukt je Einwohner, Kreise und kreisfreie Städte, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:12:52h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>2</th>
      <td>82111LJ008</td>
      <td>VGR der Länder: Entstehungsrechnung, Bruttoinlandsprodukt, Bruttoinlandsprodukt je Erwerbstätigen, Bruttoinlandsprodukt je Einwohner, Bundesländer, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:13:06h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>3</th>
      <td>82111RJ008</td>
      <td>VGR der Länder: Entstehungsrechnung, Bruttoinlandsprodukt, Bruttoinlandsprodukt je Erwerbstätigen, Bruttoinlandsprodukt je Einwohner, Regierungsbezirke / Statistische Regionen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:13:21h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>4</th>
      <td>99910BJA17</td>
      <td>Regionalatlas Deutschland, BIP je Erwerbstätigen, Veränderung des BIP zum Vorjahr, BIP je EW, Deutschland, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>22.12.2021 16:40:21h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>5</th>
      <td>99910BJC17</td>
      <td>Regionalatlas Deutschland, BIP je Arbeitsstunde, Deutschland, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2017</td>
      <td>31.01.2020 13:41:11h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>6</th>
      <td>99910KJA17</td>
      <td>Regionalatlas Deutschland, BIP je Erwerbstätigen, Veränderung des BIP zum Vorjahr, BIP je EW, Kreise und kreisfreie Städte, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>22.12.2021 16:40:29h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>7</th>
      <td>99910KJC17</td>
      <td>Regionalatlas Deutschland, BIP je Arbeitsstunde, Kreise und kreisfreie Städte, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2017</td>
      <td>31.01.2020 13:41:13h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>8</th>
      <td>99910LJA17</td>
      <td>Regionalatlas Deutschland, BIP je Erwerbstätigen, Veränderung des BIP zum Vorjahr, BIP je EW, Bundesländer, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>22.12.2021 16:40:31h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>9</th>
      <td>99910LJC17</td>
      <td>Regionalatlas Deutschland, BIP je Arbeitsstunde, Bundesländer, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2017</td>
      <td>31.01.2020 13:41:14h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>10</th>
      <td>99910RJA17</td>
      <td>Regionalatlas Deutschland, BIP je Erwerbstätigen, Veränderung des BIP zum Vorjahr, BIP je EW, Regierungsbezirke / Statistische Regionen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>22.12.2021 16:40:32h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>11</th>
      <td>99910RJC17</td>
      <td>Regionalatlas Deutschland, BIP je Arbeitsstunde, Regierungsbezirke / Statistische Regionen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2017</td>
      <td>31.01.2020 13:41:15h</td>
      <td>false</td>
    </tr>
  </tbody>
</table>
</div>



The **second opportunity** is to go to the website http://www.regionalstatistik.de. On this website you need to find the **key** of the certain topic. Example: The keys of the **labour market** resources begin with the digits **13**.

![title](pictures/regiostat.png)

Then the obtained key can then be inserted in the method `retrieve_datalist("key")`. This method returns all data cubes whose codes contain a certain key.


```python
regiostat.retrieve_datalist("13*")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Code</th>
      <th>Content</th>
      <th>State</th>
      <th>Time</th>
      <th>LatestUpdate</th>
      <th>Information</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>13111BJ001</td>
      <td>Statistik der sozialversicherungspflichtig Beschäftigten, Sozialversicherungspfl. Beschäftigte (Arbeitsort), Sozialversicherungspfl. Beschäftigte (Wohnort), Deutschland, Geschlecht, Stichtag</td>
      <td>vollständig mit Werten</td>
      <td>30.06.2008-30.06.2020</td>
      <td>26.03.2021 15:15:15h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>1</th>
      <td>13111BJ002</td>
      <td>Statistik der sozialversicherungspflichtig Beschäftigten, Sozialversicherungspfl. Beschäftigte (Arbeitsort), Sozialversicherungspfl. Beschäftigte (Wohnort), Deutschland, Geschlecht, Nationalität, Stichtag</td>
      <td>vollständig mit Werten</td>
      <td>30.06.2008-30.06.2020</td>
      <td>26.03.2021 15:15:16h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>2</th>
      <td>13111BJ003</td>
      <td>Statistik der sozialversicherungspflichtig Beschäftigten, Sozialversicherungspfl. Beschäftigte (Arbeitsort), Sozialversicherungspfl. Beschäftigte (Wohnort), Deutschland, Geschlecht, Beschäftigungsumfang, Stichtag</td>
      <td>vollständig mit Werten</td>
      <td>30.06.2008-30.06.2020</td>
      <td>26.03.2021 15:15:18h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>3</th>
      <td>13111BJ004</td>
      <td>Statistik der sozialversicherungspflichtig Beschäftigten, Sozialversicherungspfl. Beschäftigte (Arbeitsort), Sozialversicherungspfl. Beschäftigte (Wohnort), Deutschland, Geschlecht, Nationalität, Beschäftigungsumfang, Stichtag</td>
      <td>vollständig mit Werten</td>
      <td>30.06.2008-30.06.2020</td>
      <td>26.03.2021 15:15:19h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>4</th>
      <td>13111BJ005</td>
      <td>Statistik der sozialversicherungspflichtig Beschäftigten, Sozialversicherungspfl. Beschäftigte (Arbeitsort), Sozialversicherungspfl. Beschäftigte (Wohnort), Deutschland, Geschlecht, Altersgruppen (unter 20 bis 65 u. m.), Stichtag</td>
      <td>vollständig mit Werten</td>
      <td>30.06.2008-30.06.2020</td>
      <td>26.03.2021 15:15:20h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>135</th>
      <td>13211RJ010</td>
      <td>Arbeitsmarktstatistik der Bundesagentur für Arbeit, Arbeitslosenquote bez. auf alle zivile Erwerbsp., Regierungsbezirke / Statistische Regionen, Arbeitslosenquote nach Schwerpunkten, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2009-2020</td>
      <td>01.04.2021 10:04:09h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>136</th>
      <td>13312BJ001</td>
      <td>Erwerbstätigenrechnung des Bundes und der Länder, Erwerbstätige im Jahresdurchschn. (Inlandskonzept), Arbeitnehmer im Jahresdurchschn. (Inlandskonzept), Deutschland, WZ 2008-Abschnitte und Zusammenfassungen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:39:08h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>137</th>
      <td>13312KJ001</td>
      <td>Erwerbstätigenrechnung des Bundes und der Länder, Erwerbstätige im Jahresdurchschn. (Inlandskonzept), Arbeitnehmer im Jahresdurchschn. (Inlandskonzept), Kreise und kreisfreie Städte, WZ 2008-Abschnitte und Zusammenfassungen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:15:04h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>138</th>
      <td>13312LJ001</td>
      <td>Erwerbstätigenrechnung des Bundes und der Länder, Erwerbstätige im Jahresdurchschn. (Inlandskonzept), Arbeitnehmer im Jahresdurchschn. (Inlandskonzept), Bundesländer, WZ 2008-Abschnitte und Zusammenfassungen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:15:19h</td>
      <td>false</td>
    </tr>
    <tr>
      <th>139</th>
      <td>13312RJ001</td>
      <td>Erwerbstätigenrechnung des Bundes und der Länder, Erwerbstätige im Jahresdurchschn. (Inlandskonzept), Arbeitnehmer im Jahresdurchschn. (Inlandskonzept), Regierungsbezirke / Statistische Regionen, WZ 2008-Abschnitte und Zusammenfassungen, Jahr</td>
      <td>vollständig mit Werten</td>
      <td>2000-2019</td>
      <td>25.01.2022 11:15:38h</td>
      <td>false</td>
    </tr>
  </tbody>
</table>
<p>140 rows × 6 columns</p>
</div>



We searched our resources with the two methods described.

We needed to query data from the following data cubes:

* Gross Domestic Product: `82111KJ008`
* Unemployment Rate: `12411KJ019`
* Population: `12411KJ009`
* Size/Area: `11111KJ001`

## Query Data

This section contains the extraction and transfomation of all data. The first subsection (gross domestic product) contains a detailed description of the data extraction process and the methods. The other subsections contain only the most nessecary topics.

### Gross domestic product (GDP)

This subsection contains the extraction of the gross domestic product (data cube `82111KJ008`).

The data of a data cube can be retrieved with the method `retrieve_data()`.


```python
# query data 
tmpGdp = regiostat.retrieve_data("82111KJ008")

# display top rows
tmpGdp.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id82111</th>
      <th>KREISE</th>
      <th>JAHR</th>
      <th>BIP802_val</th>
      <th>BIP802_qual</th>
      <th>BIP802_lock</th>
      <th>BIP802_err</th>
      <th>BIP803_val</th>
      <th>BIP803_qual</th>
      <th>BIP803_lock</th>
      <th>BIP803_err</th>
      <th>BIP804_val</th>
      <th>BIP804_qual</th>
      <th>BIP804_lock</th>
      <th>BIP804_err</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>D</td>
      <td>01001</td>
      <td>2000</td>
      <td>2487282</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>43250</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>30799</td>
      <td>e</td>
      <td></td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>D</td>
      <td>01001</td>
      <td>2001</td>
      <td>2465393</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>43390</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>30630</td>
      <td>e</td>
      <td></td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>D</td>
      <td>01001</td>
      <td>2002</td>
      <td>2635779</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>47762</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>32778</td>
      <td>e</td>
      <td></td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>D</td>
      <td>01001</td>
      <td>2003</td>
      <td>2705233</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>49998</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>33590</td>
      <td>e</td>
      <td></td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>D</td>
      <td>01001</td>
      <td>2004</td>
      <td>2867823</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>53461</td>
      <td>e</td>
      <td></td>
      <td>0</td>
      <td>35500</td>
      <td>e</td>
      <td></td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



The column names in the table are not informative. The description of the column names is retrieved with the method `retrieve_metadata()`.


```python
regiostat.retrieve_metadata("82111KJ008")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Code</th>
      <th>Content</th>
      <th>Type</th>
      <th>Updated</th>
      <th>Unit</th>
      <th>Values</th>
      <th>Timeslices</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>KREISE</td>
      <td>Kreise und kreisfreie Städte</td>
      <td>klassifizierend</td>
      <td>07.01.2020 09:19:56h</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>JAHR</td>
      <td>Jahr</td>
      <td>zeitidentifizierend</td>
      <td>24.04.2008 12:00:14h</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>BIP802</td>
      <td>Bruttoinlandsprodukt</td>
      <td>Ganzzahl</td>
      <td>05.04.2017 13:52:02h</td>
      <td>Tsd. EUR</td>
      <td></td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>BIP803</td>
      <td>Bruttoinlandsprodukt je Erwerbstätigen</td>
      <td>Ganzzahl</td>
      <td>05.04.2017 13:52:02h</td>
      <td>EUR</td>
      <td></td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>BIP804</td>
      <td>Bruttoinlandsprodukt je Einwohner</td>
      <td>Ganzzahl</td>
      <td>05.04.2017 13:52:02h</td>
      <td>EUR</td>
      <td></td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



The following transformation steps have to be performed after the data extraction :
* The variables `BIP802` (gdp) and `BIP804` (gdp per capita) are only relevant. All columns with the suffix `_val` contain the needed values.
* We take values from 2018 because it is the most recent non-corona year with no missing values.
* The remaining columns need to be renamed to more meaningful names.


```python
# only values for the year 2018
tmpGdp = tmpGdp.loc[tmpGdp.JAHR=="2018"]

# only countyId, GDP and GDP per capita
tmpGdp = tmpGdp[["KREISE","BIP802_val","BIP804_val"]]

# rename columns
tmpGdp = tmpGdp.rename(columns={"KREISE":"countyId",
                                "BIP802_val": "gdp", 
                                "BIP804_val":"gdpPerCapita"})
# display top rows
tmpGdp.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>gdp</th>
      <th>gdpPerCapita</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>18</th>
      <td>01001</td>
      <td>3733513</td>
      <td>41944</td>
    </tr>
    <tr>
      <th>38</th>
      <td>01002</td>
      <td>11823188</td>
      <td>47723</td>
    </tr>
  </tbody>
</table>
</div>



### Unemployment rate

This subsection contains the extraction of the unemployment rate (Data cube `82111KJ008`). We use the measure **unemployment rate as a percentage of all civilian employees** (column code `ERWP10`).


```python
# query data 
tmpUnempl = regiostat.retrieve_data("13211KJ009")

# only values for the year 2019
tmpUnempl = tmpUnempl.loc[tmpUnempl.JAHR=="2019"]

# only countyId and unemployment rate as a percentage of all civilian employees
tmpUnempl = tmpUnempl[["KREISE","ERWP10_val"]]

# rename columns
tmpUnempl = tmpUnempl.rename(columns={"KREISE":"countyId",
                                      "ERWP10_val": "unemploymentRate"})

# display top rows
tmpUnempl.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>unemploymentRate</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>18</th>
      <td>01001</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>38</th>
      <td>01002</td>
      <td>7.6</td>
    </tr>
    <tr>
      <th>58</th>
      <td>01003</td>
      <td>7.3</td>
    </tr>
    <tr>
      <th>78</th>
      <td>01004</td>
      <td>7.9</td>
    </tr>
    <tr>
      <th>98</th>
      <td>01051</td>
      <td>5.5</td>
    </tr>
  </tbody>
</table>
</div>



### Population

This subsection contains the extraction of the population (data cube `82111KJ008`). The data cube contains the population seperated by gender (2 rows per county - one with the female population and one with the male population). The total population is sufficient for our project. Therefore an aggregation is performed. 


```python
# query data 
tmpPop = regiostat.retrieve_data("12411KJ009")

# only values for the year 2019
tmpPop = tmpPop.loc[tmpPop.STAG=="31.12.2019"]

# aggregate (no differentiation between male and female)
tmpPop = tmpPop.groupby("KREISE", as_index=False).sum("BEVSTD_val")

# rename columns
tmpPop = tmpPop.rename(columns={"KREISE":"countyId",
                                "BEVSTD_val": "population"})

# display top rows
tmpPop.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>population</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01001</td>
      <td>90164</td>
    </tr>
    <tr>
      <th>1</th>
      <td>01002</td>
      <td>246794</td>
    </tr>
    <tr>
      <th>2</th>
      <td>01003</td>
      <td>216530</td>
    </tr>
    <tr>
      <th>3</th>
      <td>01004</td>
      <td>80196</td>
    </tr>
    <tr>
      <th>4</th>
      <td>01051</td>
      <td>133193</td>
    </tr>
  </tbody>
</table>
</div>



### Area size

This subsection contains the extraction of the area size (data cube `11111KJ001`). 


```python
# query data 
tmpArea = regiostat.retrieve_data("11111KJ001")

# only values for the year 2019
tmpArea = tmpArea.loc[tmpArea.STAG=="31.12.2019"]

# only countyId and area size
tmpArea = tmpArea[["KREISE","FLC006_val"]]

# rename columns
tmpArea = tmpArea.rename(columns={"KREISE":"countyId",
                                  "FLC006_val": "areaSize"})

# display top rows
tmpArea.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>areaSize</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24</th>
      <td>01001</td>
      <td>53.02</td>
    </tr>
    <tr>
      <th>50</th>
      <td>01002</td>
      <td>118.65</td>
    </tr>
    <tr>
      <th>76</th>
      <td>01003</td>
      <td>214.19</td>
    </tr>
    <tr>
      <th>102</th>
      <td>01004</td>
      <td>71.66</td>
    </tr>
    <tr>
      <th>128</th>
      <td>01051</td>
      <td>1428.17</td>
    </tr>
  </tbody>
</table>
</div>



### County names

In contrast to the previous subsections, the last subsection of the data extraction process contains the extraction of a nominal variable (variable **countyname**). The data of such variables can be queried with the method `retrieve_valuelabel()`.


```python
# query data 
tmpCountyNames = regiostat.retrieve_valuelabel("KREISE")

# only countyId and area size
tmpCountyNames = tmpCountyNames[["Code","Content"]]

# rename columns
tmpCountyNames = tmpCountyNames.rename(columns={"Code":"countyId",
                                                "Content": "countyName"})

# display top rows
tmpCountyNames.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>countyName</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01001</td>
      <td>Flensburg, kreisfreie Stadt</td>
    </tr>
    <tr>
      <th>1</th>
      <td>01002</td>
      <td>Kiel, Landeshauptstadt, kreisfreie Stadt</td>
    </tr>
    <tr>
      <th>2</th>
      <td>01003</td>
      <td>Lübeck, Hansestadt, kreisfreie Stadt</td>
    </tr>
    <tr>
      <th>3</th>
      <td>01004</td>
      <td>Neumünster, kreisfreie Stadt</td>
    </tr>
    <tr>
      <th>4</th>
      <td>01051</td>
      <td>Dithmarschen, Landkreis</td>
    </tr>
  </tbody>
</table>
</div>



## Join data

In this section, the queried sub data frames are merged together to one final data frame. Before merging, the number of rows in the sub-data frames is checked.


```python
print("Number of rows:")
print("---------------")
print("Gdp",tmpGdp.shape[0])
print("Unemployment",tmpUnempl.shape[0])
print("Population",tmpPop.shape[0])
print("Area",tmpArea.shape[0])
print("County Names",tmpCountyNames.shape[0])
```

    Number of rows:
    ---------------
    Gdp 416
    Unemployment 416
    Population 416
    Area 416
    County Names 489
    

There are more county names (489) than rows in the data frames with measures (416). The reason for this is that there are county names of old counties that have been merged into larger counties and that exist no longer. Only counties that exist in the year of the measurement are available in the data frames with the measures. Old counties are included in the  data frame with the county names. We only need the counties that existed in the years 2018 and 2019. In this case, other counties can be excluded by using inner joins.


```python
countyData = pd.merge(tmpCountyNames, tmpGdp, on="countyId", how="inner")
countyData = pd.merge(countyData, tmpUnempl, on="countyId", how="inner")
countyData = pd.merge(countyData, tmpPop, on="countyId", how="inner")
countyData = pd.merge(countyData, tmpArea, on="countyId", how="inner")
```


```python
countyData
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>countyName</th>
      <th>gdp</th>
      <th>gdpPerCapita</th>
      <th>unemploymentRate</th>
      <th>population</th>
      <th>areaSize</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01001</td>
      <td>Flensburg, kreisfreie Stadt</td>
      <td>3733513</td>
      <td>41944</td>
      <td>8.0</td>
      <td>90164</td>
      <td>53.02</td>
    </tr>
    <tr>
      <th>1</th>
      <td>01002</td>
      <td>Kiel, Landeshauptstadt, kreisfreie Stadt</td>
      <td>11823188</td>
      <td>47723</td>
      <td>7.6</td>
      <td>246794</td>
      <td>118.65</td>
    </tr>
    <tr>
      <th>2</th>
      <td>01003</td>
      <td>Lübeck, Hansestadt, kreisfreie Stadt</td>
      <td>9367966</td>
      <td>43219</td>
      <td>7.3</td>
      <td>216530</td>
      <td>214.19</td>
    </tr>
    <tr>
      <th>3</th>
      <td>01004</td>
      <td>Neumünster, kreisfreie Stadt</td>
      <td>3458069</td>
      <td>43546</td>
      <td>7.9</td>
      <td>80196</td>
      <td>71.66</td>
    </tr>
    <tr>
      <th>4</th>
      <td>01051</td>
      <td>Dithmarschen, Landkreis</td>
      <td>4606985</td>
      <td>34554</td>
      <td>5.5</td>
      <td>133193</td>
      <td>1428.17</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>411</th>
      <td>16073</td>
      <td>Saalfeld-Rudolstadt, Kreis</td>
      <td>2839645</td>
      <td>26573</td>
      <td>5.3</td>
      <td>103199</td>
      <td>1008.79</td>
    </tr>
    <tr>
      <th>412</th>
      <td>16074</td>
      <td>Saale-Holzland-Kreis</td>
      <td>1929064</td>
      <td>23236</td>
      <td>4.1</td>
      <td>82950</td>
      <td>815.24</td>
    </tr>
    <tr>
      <th>413</th>
      <td>16075</td>
      <td>Saale-Orla-Kreis</td>
      <td>2253787</td>
      <td>27761</td>
      <td>4.6</td>
      <td>80312</td>
      <td>1151.30</td>
    </tr>
    <tr>
      <th>414</th>
      <td>16076</td>
      <td>Greiz, Kreis</td>
      <td>2365566</td>
      <td>23963</td>
      <td>4.6</td>
      <td>97398</td>
      <td>845.98</td>
    </tr>
    <tr>
      <th>415</th>
      <td>16077</td>
      <td>Altenburger Land, Kreis</td>
      <td>1997382</td>
      <td>22099</td>
      <td>7.1</td>
      <td>89393</td>
      <td>569.39</td>
    </tr>
  </tbody>
</table>
<p>416 rows × 7 columns</p>
</div>



## Adding State and Region

In this section, the `state` and `region` (East or West Germany) columns are added to the data frame. The first two digits of the `countyId` represent the id of a state. Therefore, this column can be used for mapping.

Initially, a data frame is created with the names of all states and regions.


```python
# data list
stateListData = [['01', 'Schleswig-Holstein', 'West Germany'],
                ['02', 'Freie und Hansestadt Hamburg', 'West Germany'],
                ['03', 'Niedersachsen', 'West Germany'],
                ['04', 'Freie Hansestadt Bremen', 'West Germany'],
                ['05', 'Nordrhein-Westfalen', 'West Germany'],
                ['06', 'Hessen', 'West Germany'],
                ['07', 'Rheinland-Pfalz', 'West Germany'],
                ['08', 'Baden-Württemberg', 'West Germany'],
                ['09', 'Freistaat Bayern', 'West Germany'],
                ['10', 'Saarland', 'West Germany'],
                ['11', 'Berlin', 'East Germany'],
                ['12', 'Brandenburg', 'East Germany'],
                ['13', 'Mecklenburg-Vorpommern', 'East Germany'],
                ['14', 'Freistaat Sachsen', 'East Germany'],
                ['15', 'Sachsen-Anhalt', 'East Germany'],
                ['16', 'Freistaat Thüringen', 'East Germany']]


# list of column names
stateColumnNames = ["stateId", "state", "region"]

# create data frame
stateDf = pd.DataFrame(stateListData, columns=stateColumnNames)

# dispaly first two rows
stateDf.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>stateId</th>
      <th>state</th>
      <th>region</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01</td>
      <td>Schleswig-Holstein</td>
      <td>West Germany</td>
    </tr>
    <tr>
      <th>1</th>
      <td>02</td>
      <td>Freie und Hansestadt Hamburg</td>
      <td>West Germany</td>
    </tr>
  </tbody>
</table>
</div>



Subsequently, the names of the states and regions are inserted into the main data frame by using an inner join.


```python
# inner join
countyData = pd.merge(countyData, stateDf, left_on=countyData["countyId"].astype(str).str[0:2], right_on="stateId", how="inner")

# dispaly first two rows
countyData.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>countyId</th>
      <th>countyName</th>
      <th>gdp</th>
      <th>gdpPerCapita</th>
      <th>unemploymentRate</th>
      <th>population</th>
      <th>areaSize</th>
      <th>stateId</th>
      <th>state</th>
      <th>region</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01001</td>
      <td>Flensburg, kreisfreie Stadt</td>
      <td>3733513</td>
      <td>41944</td>
      <td>8.0</td>
      <td>90164</td>
      <td>53.02</td>
      <td>01</td>
      <td>Schleswig-Holstein</td>
      <td>West Germany</td>
    </tr>
    <tr>
      <th>1</th>
      <td>01002</td>
      <td>Kiel, Landeshauptstadt, kreisfreie Stadt</td>
      <td>11823188</td>
      <td>47723</td>
      <td>7.6</td>
      <td>246794</td>
      <td>118.65</td>
      <td>01</td>
      <td>Schleswig-Holstein</td>
      <td>West Germany</td>
    </tr>
  </tbody>
</table>
</div>



## Loading into Mongo DB

Finally, the data is loaded into the Mongo DB database.

The first step is to extract the data from the pandas data frame by using the method `to_dict()`. The result is a list with dictionaries as list elements. Each dictionary represents one county.


```python
countyDataMongo = countyData.to_dict(orient="records")
countyDataMongo
```




    [{'countyId': '01001',
      'countyName': 'Flensburg, kreisfreie Stadt',
      'gdp': 3733513,
      'gdpPerCapita': 41944,
      'unemploymentRate': 8.0,
      'population': 90164,
      'areaSize': 53.02,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01002',
      'countyName': 'Kiel, Landeshauptstadt, kreisfreie Stadt',
      'gdp': 11823188,
      'gdpPerCapita': 47723,
      'unemploymentRate': 7.6,
      'population': 246794,
      'areaSize': 118.65,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01003',
      'countyName': 'Lübeck, Hansestadt, kreisfreie Stadt',
      'gdp': 9367966,
      'gdpPerCapita': 43219,
      'unemploymentRate': 7.3,
      'population': 216530,
      'areaSize': 214.19,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01004',
      'countyName': 'Neumünster, kreisfreie Stadt',
      'gdp': 3458069,
      'gdpPerCapita': 43546,
      'unemploymentRate': 7.9,
      'population': 80196,
      'areaSize': 71.66,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01051',
      'countyName': 'Dithmarschen, Landkreis',
      'gdp': 4606985,
      'gdpPerCapita': 34554,
      'unemploymentRate': 5.5,
      'population': 133193,
      'areaSize': 1428.17,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01053',
      'countyName': 'Herzogtum Lauenburg, Landkreis',
      'gdp': 4598142,
      'gdpPerCapita': 23380,
      'unemploymentRate': 4.7,
      'population': 198019,
      'areaSize': 1263.07,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01054',
      'countyName': 'Nordfriesland, Landkreis',
      'gdp': 5640150,
      'gdpPerCapita': 34083,
      'unemploymentRate': 4.8,
      'population': 165951,
      'areaSize': 2083.55,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01055',
      'countyName': 'Ostholstein, Landkreis',
      'gdp': 5383375,
      'gdpPerCapita': 26839,
      'unemploymentRate': 5.0,
      'population': 200539,
      'areaSize': 1393.02,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01056',
      'countyName': 'Pinneberg, Landkreis',
      'gdp': 9367476,
      'gdpPerCapita': 29878,
      'unemploymentRate': 4.5,
      'population': 316103,
      'areaSize': 664.25,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01057',
      'countyName': 'Plön, Landkreis',
      'gdp': 2565226,
      'gdpPerCapita': 19925,
      'unemploymentRate': 4.0,
      'population': 128686,
      'areaSize': 1083.56,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01058',
      'countyName': 'Rendsburg-Eckernförde, Landkreis',
      'gdp': 7912868,
      'gdpPerCapita': 28996,
      'unemploymentRate': 3.9,
      'population': 274098,
      'areaSize': 2189.79,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01059',
      'countyName': 'Schleswig-Flensburg, Landkreis',
      'gdp': 5267075,
      'gdpPerCapita': 26366,
      'unemploymentRate': 4.3,
      'population': 201156,
      'areaSize': 2071.28,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01060',
      'countyName': 'Segeberg, Landkreis',
      'gdp': 8624302,
      'gdpPerCapita': 31358,
      'unemploymentRate': 4.0,
      'population': 277175,
      'areaSize': 1344.47,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01061',
      'countyName': 'Steinburg, Landkreis',
      'gdp': 4249895,
      'gdpPerCapita': 32324,
      'unemploymentRate': 5.1,
      'population': 131013,
      'areaSize': 1055.7,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '01062',
      'countyName': 'Stormarn, Landkreis',
      'gdp': 8270714,
      'gdpPerCapita': 34059,
      'unemploymentRate': 3.1,
      'population': 244156,
      'areaSize': 766.17,
      'stateId': '01',
      'state': 'Schleswig-Holstein',
      'region': 'West Germany'},
     {'countyId': '02000',
      'countyName': 'Hamburg',
      'gdp': 118483625,
      'gdpPerCapita': 64538,
      'unemploymentRate': 6.1,
      'population': 1847253,
      'areaSize': 755.09,
      'stateId': '02',
      'state': 'Freie und Hansestadt Hamburg',
      'region': 'West Germany'},
     {'countyId': '03101',
      'countyName': 'Braunschweig, kreisfreie Stadt',
      'gdp': 18671745,
      'gdpPerCapita': 75241,
      'unemploymentRate': 4.9,
      'population': 249406,
      'areaSize': 192.7,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03102',
      'countyName': 'Salzgitter, kreisfreie Stadt',
      'gdp': 5903410,
      'gdpPerCapita': 56358,
      'unemploymentRate': 8.8,
      'population': 104291,
      'areaSize': 224.49,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03103',
      'countyName': 'Wolfsburg, kreisfreie Stadt',
      'gdp': 22759834,
      'gdpPerCapita': 183498,
      'unemploymentRate': 4.5,
      'population': 124371,
      'areaSize': 204.61,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03151',
      'countyName': 'Gifhorn, Landkreis',
      'gdp': 3682310,
      'gdpPerCapita': 20982,
      'unemploymentRate': 4.0,
      'population': 176523,
      'areaSize': 1567.55,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03153',
      'countyName': 'Goslar, Landkreis',
      'gdp': 4094066,
      'gdpPerCapita': 29821,
      'unemploymentRate': 5.9,
      'population': 136292,
      'areaSize': 966.72,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03154',
      'countyName': 'Helmstedt, Landkreis',
      'gdp': 1880042,
      'gdpPerCapita': 20544,
      'unemploymentRate': 5.8,
      'population': 91297,
      'areaSize': 676.15,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03155',
      'countyName': 'Northeim, Landkreis',
      'gdp': 3800704,
      'gdpPerCapita': 28597,
      'unemploymentRate': 5.1,
      'population': 132285,
      'areaSize': 1268.76,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03157',
      'countyName': 'Peine, Landkreis',
      'gdp': 2957402,
      'gdpPerCapita': 22125,
      'unemploymentRate': 4.4,
      'population': 134801,
      'areaSize': 536.5,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03158',
      'countyName': 'Wolfenbüttel, Landkreis',
      'gdp': 2433316,
      'gdpPerCapita': 20244,
      'unemploymentRate': 4.4,
      'population': 119622,
      'areaSize': 724.3,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03159',
      'countyName': 'Göttingen, Landkreis',
      'gdp': 11681850,
      'gdpPerCapita': 35609,
      'unemploymentRate': 5.3,
      'population': 326041,
      'areaSize': 1755.42,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03241',
      'countyName': 'Region Hannover, Landkreis',
      'gdp': 52920006,
      'gdpPerCapita': 45812,
      'unemploymentRate': 6.4,
      'population': 1157115,
      'areaSize': 2297.13,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03241001',
      'countyName': 'Hannover, Landeshauptstadt',
      'gdp': 34655230,
      'gdpPerCapita': 64587,
      'unemploymentRate': 7.8,
      'population': 536925,
      'areaSize': 204.3,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03251',
      'countyName': 'Diepholz, Landkreis',
      'gdp': 6544717,
      'gdpPerCapita': 30237,
      'unemploymentRate': 3.9,
      'population': 217089,
      'areaSize': 1991.01,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03252',
      'countyName': 'Hameln-Pyrmont, Landkreis',
      'gdp': 5135514,
      'gdpPerCapita': 34599,
      'unemploymentRate': 6.1,
      'population': 148549,
      'areaSize': 797.54,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03254',
      'countyName': 'Hildesheim, Landkreis',
      'gdp': 7835193,
      'gdpPerCapita': 28325,
      'unemploymentRate': 5.7,
      'population': 275817,
      'areaSize': 1208.34,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03255',
      'countyName': 'Holzminden, Landkreis',
      'gdp': 2211248,
      'gdpPerCapita': 31118,
      'unemploymentRate': 6.3,
      'population': 70458,
      'areaSize': 694.27,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03256',
      'countyName': 'Nienburg (Weser), Landkreis',
      'gdp': 3705537,
      'gdpPerCapita': 30516,
      'unemploymentRate': 4.8,
      'population': 121390,
      'areaSize': 1400.82,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03257',
      'countyName': 'Schaumburg, Landkreis',
      'gdp': 4109194,
      'gdpPerCapita': 26035,
      'unemploymentRate': 5.3,
      'population': 157820,
      'areaSize': 675.67,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03351',
      'countyName': 'Celle, Landkreis',
      'gdp': 5358951,
      'gdpPerCapita': 29963,
      'unemploymentRate': 5.7,
      'population': 179011,
      'areaSize': 1550.82,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03352',
      'countyName': 'Cuxhaven, Landkreis',
      'gdp': 4629097,
      'gdpPerCapita': 23361,
      'unemploymentRate': 5.2,
      'population': 198038,
      'areaSize': 2058.96,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03353',
      'countyName': 'Harburg, Landkreis',
      'gdp': 6104139,
      'gdpPerCapita': 24209,
      'unemploymentRate': 3.7,
      'population': 254431,
      'areaSize': 1248.45,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03354',
      'countyName': 'Lüchow-Dannenberg, Landkreis',
      'gdp': 1258440,
      'gdpPerCapita': 26006,
      'unemploymentRate': 7.3,
      'population': 48412,
      'areaSize': 1227.33,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03355',
      'countyName': 'Lüneburg, Landkreis',
      'gdp': 5170249,
      'gdpPerCapita': 28229,
      'unemploymentRate': 5.3,
      'population': 184139,
      'areaSize': 1327.8,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03356',
      'countyName': 'Osterholz, Landkreis',
      'gdp': 2326775,
      'gdpPerCapita': 20534,
      'unemploymentRate': 3.3,
      'population': 113928,
      'areaSize': 652.67,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03357',
      'countyName': 'Rotenburg (Wümme), Landkreis',
      'gdp': 5222488,
      'gdpPerCapita': 31958,
      'unemploymentRate': 3.6,
      'population': 163782,
      'areaSize': 2074.78,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03358',
      'countyName': 'Heidekreis, Landkreis',
      'gdp': 4715730,
      'gdpPerCapita': 33822,
      'unemploymentRate': 5.3,
      'population': 140673,
      'areaSize': 1881.45,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03359',
      'countyName': 'Stade, Landkreis',
      'gdp': 6149007,
      'gdpPerCapita': 30366,
      'unemploymentRate': 5.0,
      'population': 204512,
      'areaSize': 1267.38,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03360',
      'countyName': 'Uelzen, Landkreis',
      'gdp': 2571417,
      'gdpPerCapita': 27752,
      'unemploymentRate': 5.0,
      'population': 92389,
      'areaSize': 1462.59,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03361',
      'countyName': 'Verden, Landkreis',
      'gdp': 4221004,
      'gdpPerCapita': 30880,
      'unemploymentRate': 4.0,
      'population': 137133,
      'areaSize': 789.33,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03401',
      'countyName': 'Delmenhorst, kreisfreie Stadt',
      'gdp': 1777721,
      'gdpPerCapita': 22919,
      'unemploymentRate': 9.4,
      'population': 77559,
      'areaSize': 62.45,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03402',
      'countyName': 'Emden, kreisfreie Stadt',
      'gdp': 3665773,
      'gdpPerCapita': 72732,
      'unemploymentRate': 8.2,
      'population': 49913,
      'areaSize': 112.34,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03403',
      'countyName': 'Oldenburg (Oldenburg), kreisfreie Stadt',
      'gdp': 7839513,
      'gdpPerCapita': 46762,
      'unemploymentRate': 6.1,
      'population': 169077,
      'areaSize': 103.09,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03404',
      'countyName': 'Osnabrück, kreisfreie Stadt',
      'gdp': 8199106,
      'gdpPerCapita': 49824,
      'unemploymentRate': 6.6,
      'population': 165251,
      'areaSize': 119.8,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03405',
      'countyName': 'Wilhelmshaven, kreisfreie Stadt',
      'gdp': 3210703,
      'gdpPerCapita': 42082,
      'unemploymentRate': 10.3,
      'population': 76089,
      'areaSize': 107.07,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03451',
      'countyName': 'Ammerland, Landkreis',
      'gdp': 3817827,
      'gdpPerCapita': 30858,
      'unemploymentRate': 3.6,
      'population': 124859,
      'areaSize': 730.64,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03452',
      'countyName': 'Aurich, Landkreis',
      'gdp': 5012374,
      'gdpPerCapita': 26395,
      'unemploymentRate': 6.3,
      'population': 189694,
      'areaSize': 1287.35,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03453',
      'countyName': 'Cloppenburg, Landkreis',
      'gdp': 5673163,
      'gdpPerCapita': 33641,
      'unemploymentRate': 3.9,
      'population': 170682,
      'areaSize': 1420.34,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03454',
      'countyName': 'Emsland, Landkreis',
      'gdp': 13513747,
      'gdpPerCapita': 41626,
      'unemploymentRate': 2.4,
      'population': 326954,
      'areaSize': 2883.67,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03455',
      'countyName': 'Friesland, Landkreis',
      'gdp': 2673845,
      'gdpPerCapita': 27150,
      'unemploymentRate': 4.3,
      'population': 98704,
      'areaSize': 609.53,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03456',
      'countyName': 'Grafschaft Bentheim, Landkreis',
      'gdp': 4309582,
      'gdpPerCapita': 31645,
      'unemploymentRate': 2.5,
      'population': 137162,
      'areaSize': 981.79,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03457',
      'countyName': 'Leer, Landkreis',
      'gdp': 4325823,
      'gdpPerCapita': 25539,
      'unemploymentRate': 5.2,
      'population': 170756,
      'areaSize': 1085.72,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03458',
      'countyName': 'Oldenburg, Landkreis',
      'gdp': 3188977,
      'gdpPerCapita': 24524,
      'unemploymentRate': 3.1,
      'population': 130890,
      'areaSize': 1064.83,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03459',
      'countyName': 'Osnabrück, Landkreis',
      'gdp': 10787785,
      'gdpPerCapita': 30240,
      'unemploymentRate': 2.9,
      'population': 358080,
      'areaSize': 2121.81,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03460',
      'countyName': 'Vechta, Landkreis',
      'gdp': 6296802,
      'gdpPerCapita': 44636,
      'unemploymentRate': 3.4,
      'population': 142814,
      'areaSize': 814.2,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03461',
      'countyName': 'Wesermarsch, Landkreis',
      'gdp': 2851061,
      'gdpPerCapita': 32098,
      'unemploymentRate': 5.8,
      'population': 88583,
      'areaSize': 824.78,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '03462',
      'countyName': 'Wittmund, Landkreis',
      'gdp': 1462850,
      'gdpPerCapita': 25751,
      'unemploymentRate': 5.4,
      'population': 56926,
      'areaSize': 656.86,
      'stateId': '03',
      'state': 'Niedersachsen',
      'region': 'West Germany'},
     {'countyId': '04011',
      'countyName': 'Bremen, kreisfreie Stadt',
      'gdp': 28793175,
      'gdpPerCapita': 50632,
      'unemploymentRate': 9.5,
      'population': 567559,
      'areaSize': 325.55,
      'stateId': '04',
      'state': 'Freie Hansestadt Bremen',
      'region': 'West Germany'},
     {'countyId': '04012',
      'countyName': 'Bremerhaven, kreisfreie Stadt',
      'gdp': 4053900,
      'gdpPerCapita': 35771,
      'unemploymentRate': 12.2,
      'population': 113643,
      'areaSize': 93.82,
      'stateId': '04',
      'state': 'Freie Hansestadt Bremen',
      'region': 'West Germany'},
     {'countyId': '05111',
      'countyName': 'Düsseldorf, kreisfreie Stadt',
      'gdp': 51216801,
      'gdpPerCapita': 82837,
      'unemploymentRate': 6.6,
      'population': 621877,
      'areaSize': 217.41,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05112',
      'countyName': 'Duisburg, kreisfreie Stadt',
      'gdp': 18145981,
      'gdpPerCapita': 36412,
      'unemploymentRate': 10.8,
      'population': 498686,
      'areaSize': 232.8,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05113',
      'countyName': 'Essen, kreisfreie Stadt',
      'gdp': 25883748,
      'gdpPerCapita': 44378,
      'unemploymentRate': 10.2,
      'population': 582760,
      'areaSize': 210.34,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05114',
      'countyName': 'Krefeld, kreisfreie Stadt',
      'gdp': 9391534,
      'gdpPerCapita': 41398,
      'unemploymentRate': 10.1,
      'population': 227417,
      'areaSize': 137.78,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05116',
      'countyName': 'Mönchengladbach, kreisfreie Stadt',
      'gdp': 8952874,
      'gdpPerCapita': 34195,
      'unemploymentRate': 9.0,
      'population': 261034,
      'areaSize': 170.47,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05117',
      'countyName': 'Mülheim an der Ruhr, kreisfreie Stadt',
      'gdp': 6038477,
      'gdpPerCapita': 35298,
      'unemploymentRate': 7.1,
      'population': 170632,
      'areaSize': 91.28,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05119',
      'countyName': 'Oberhausen, kreisfreie Stadt',
      'gdp': 5806527,
      'gdpPerCapita': 27503,
      'unemploymentRate': 9.8,
      'population': 210764,
      'areaSize': 77.09,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05120',
      'countyName': 'Remscheid, kreisfreie Stadt',
      'gdp': 4016901,
      'gdpPerCapita': 36257,
      'unemploymentRate': 7.0,
      'population': 111338,
      'areaSize': 74.52,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05122',
      'countyName': 'Solingen, kreisfreie Stadt',
      'gdp': 5075549,
      'gdpPerCapita': 31905,
      'unemploymentRate': 7.1,
      'population': 159245,
      'areaSize': 89.54,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05124',
      'countyName': 'Wuppertal, kreisfreie Stadt',
      'gdp': 13026297,
      'gdpPerCapita': 36799,
      'unemploymentRate': 8.1,
      'population': 355100,
      'areaSize': 168.39,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05154',
      'countyName': 'Kleve, Kreis',
      'gdp': 9519533,
      'gdpPerCapita': 30597,
      'unemploymentRate': 5.2,
      'population': 312465,
      'areaSize': 1232.99,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05158',
      'countyName': 'Mettmann, Kreis',
      'gdp': 19824638,
      'gdpPerCapita': 40829,
      'unemploymentRate': 5.6,
      'population': 485570,
      'areaSize': 407.22,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05162',
      'countyName': 'Rhein-Kreis Neuss',
      'gdp': 18349246,
      'gdpPerCapita': 40757,
      'unemploymentRate': 5.0,
      'population': 451730,
      'areaSize': 576.42,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05166',
      'countyName': 'Viersen, Kreis',
      'gdp': 8591129,
      'gdpPerCapita': 28749,
      'unemploymentRate': 5.3,
      'population': 298863,
      'areaSize': 563.28,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05170',
      'countyName': 'Wesel, Kreis',
      'gdp': 13217436,
      'gdpPerCapita': 28719,
      'unemploymentRate': 5.9,
      'population': 459976,
      'areaSize': 1042.79,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05314',
      'countyName': 'Bonn, kreisfreie Stadt',
      'gdp': 26382774,
      'gdpPerCapita': 80836,
      'unemploymentRate': 6.3,
      'population': 329673,
      'areaSize': 141.06,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05315',
      'countyName': 'Köln, kreisfreie Stadt',
      'gdp': 65321747,
      'gdpPerCapita': 60314,
      'unemploymentRate': 7.8,
      'population': 1087863,
      'areaSize': 405.01,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05316',
      'countyName': 'Leverkusen, kreisfreie Stadt',
      'gdp': 8507904,
      'gdpPerCapita': 51970,
      'unemploymentRate': 7.2,
      'population': 163729,
      'areaSize': 78.87,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05334',
      'countyName': 'Städteregion Aachen (einschl. Stadt Aachen)',
      'gdp': 21093698,
      'gdpPerCapita': 38023,
      'unemploymentRate': 6.9,
      'population': 557026,
      'areaSize': 706.91,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05334002',
      'countyName': 'Aachen, krfr. Stadt',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 7.4,
      'population': 248960,
      'areaSize': 160.85,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05358',
      'countyName': 'Düren, Kreis',
      'gdp': 7829272,
      'gdpPerCapita': 29734,
      'unemploymentRate': 6.3,
      'population': 264638,
      'areaSize': 941.49,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05362',
      'countyName': 'Rhein-Erft-Kreis',
      'gdp': 16742942,
      'gdpPerCapita': 35726,
      'unemploymentRate': 5.7,
      'population': 470615,
      'areaSize': 704.71,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05366',
      'countyName': 'Euskirchen, Kreis',
      'gdp': 5384029,
      'gdpPerCapita': 27971,
      'unemploymentRate': 4.9,
      'population': 193656,
      'areaSize': 1248.73,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05370',
      'countyName': 'Heinsberg, Kreis',
      'gdp': 6564465,
      'gdpPerCapita': 25873,
      'unemploymentRate': 5.0,
      'population': 255555,
      'areaSize': 627.91,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05374',
      'countyName': 'Oberbergischer Kreis',
      'gdp': 9825111,
      'gdpPerCapita': 36026,
      'unemploymentRate': 4.9,
      'population': 272057,
      'areaSize': 918.85,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05378',
      'countyName': 'Rheinisch-Bergischer Kreis',
      'gdp': 7942018,
      'gdpPerCapita': 28024,
      'unemploymentRate': 5.2,
      'population': 283271,
      'areaSize': 437.32,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05382',
      'countyName': 'Rhein-Sieg-Kreis',
      'gdp': 16890628,
      'gdpPerCapita': 28178,
      'unemploymentRate': 4.8,
      'population': 600764,
      'areaSize': 1153.21,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05512',
      'countyName': 'Bottrop, kreisfreie Stadt',
      'gdp': 2659966,
      'gdpPerCapita': 22662,
      'unemploymentRate': 7.0,
      'population': 117565,
      'areaSize': 100.61,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05513',
      'countyName': 'Gelsenkirchen, kreisfreie Stadt',
      'gdp': 8020785,
      'gdpPerCapita': 30792,
      'unemploymentRate': 12.8,
      'population': 259645,
      'areaSize': 104.94,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05515',
      'countyName': 'Münster, kreisfreie Stadt',
      'gdp': 17406025,
      'gdpPerCapita': 55444,
      'unemploymentRate': 4.6,
      'population': 315293,
      'areaSize': 303.28,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05554',
      'countyName': 'Borken, Kreis',
      'gdp': 13856160,
      'gdpPerCapita': 37429,
      'unemploymentRate': 3.4,
      'population': 371339,
      'areaSize': 1420.98,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05558',
      'countyName': 'Coesfeld, Kreis',
      'gdp': 6294037,
      'gdpPerCapita': 28655,
      'unemploymentRate': 2.7,
      'population': 220586,
      'areaSize': 1112.04,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05562',
      'countyName': 'Recklinghausen, Kreis',
      'gdp': 16137869,
      'gdpPerCapita': 26196,
      'unemploymentRate': 8.1,
      'population': 614137,
      'areaSize': 761.31,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05566',
      'countyName': 'Steinfurt, Kreis',
      'gdp': 14634265,
      'gdpPerCapita': 32732,
      'unemploymentRate': 4.0,
      'population': 448220,
      'areaSize': 1795.75,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05570',
      'countyName': 'Warendorf, Kreis',
      'gdp': 8608662,
      'gdpPerCapita': 31009,
      'unemploymentRate': 4.6,
      'population': 277840,
      'areaSize': 1319.42,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05711',
      'countyName': 'Bielefeld, kreisfreie Stadt',
      'gdp': 13745130,
      'gdpPerCapita': 41256,
      'unemploymentRate': 7.3,
      'population': 334195,
      'areaSize': 258.83,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05754',
      'countyName': 'Gütersloh, Kreis',
      'gdp': 17442407,
      'gdpPerCapita': 47976,
      'unemploymentRate': 4.0,
      'population': 364938,
      'areaSize': 969.21,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05758',
      'countyName': 'Herford, Kreis',
      'gdp': 8493023,
      'gdpPerCapita': 33815,
      'unemploymentRate': 5.1,
      'population': 250578,
      'areaSize': 450.4,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05762',
      'countyName': 'Höxter, Kreis',
      'gdp': 4004574,
      'gdpPerCapita': 28378,
      'unemploymentRate': 3.7,
      'population': 140251,
      'areaSize': 1201.42,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05766',
      'countyName': 'Lippe, Kreis',
      'gdp': 10677100,
      'gdpPerCapita': 30617,
      'unemploymentRate': 5.8,
      'population': 347514,
      'areaSize': 1246.22,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05770',
      'countyName': 'Minden-Lübbecke, Kreis',
      'gdp': 12966681,
      'gdpPerCapita': 41699,
      'unemploymentRate': 4.7,
      'population': 310409,
      'areaSize': 1152.41,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05774',
      'countyName': 'Paderborn, Kreis',
      'gdp': 11038291,
      'gdpPerCapita': 36058,
      'unemploymentRate': 5.0,
      'population': 307839,
      'areaSize': 1246.8,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05911',
      'countyName': 'Bochum, kreisfreie Stadt',
      'gdp': 12243729,
      'gdpPerCapita': 33537,
      'unemploymentRate': 8.5,
      'population': 365587,
      'areaSize': 145.66,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05913',
      'countyName': 'Dortmund, kreisfreie Stadt',
      'gdp': 23000307,
      'gdpPerCapita': 39196,
      'unemploymentRate': 10.1,
      'population': 588250,
      'areaSize': 280.71,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05914',
      'countyName': 'Hagen, kreisfreie Stadt',
      'gdp': 6579354,
      'gdpPerCapita': 34946,
      'unemploymentRate': 10.0,
      'population': 188686,
      'areaSize': 160.45,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05915',
      'countyName': 'Hamm, kreisfreie Stadt',
      'gdp': 5241091,
      'gdpPerCapita': 29256,
      'unemploymentRate': 8.1,
      'population': 179916,
      'areaSize': 226.44,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05916',
      'countyName': 'Herne, kreisfreie Stadt',
      'gdp': 3697366,
      'gdpPerCapita': 23636,
      'unemploymentRate': 10.3,
      'population': 156449,
      'areaSize': 51.42,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05954',
      'countyName': 'Ennepe-Ruhr-Kreis',
      'gdp': 9897026,
      'gdpPerCapita': 30501,
      'unemploymentRate': 5.5,
      'population': 324106,
      'areaSize': 409.64,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05958',
      'countyName': 'Hochsauerlandkreis',
      'gdp': 9577306,
      'gdpPerCapita': 36690,
      'unemploymentRate': 4.0,
      'population': 259777,
      'areaSize': 1960.17,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05962',
      'countyName': 'Märkischer Kreis',
      'gdp': 15293646,
      'gdpPerCapita': 37053,
      'unemploymentRate': 6.2,
      'population': 410222,
      'areaSize': 1061.07,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05966',
      'countyName': 'Olpe, Kreis',
      'gdp': 5540734,
      'gdpPerCapita': 41106,
      'unemploymentRate': 3.3,
      'population': 133955,
      'areaSize': 712.14,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05970',
      'countyName': 'Siegen-Wittgenstein, Kreis',
      'gdp': 11326403,
      'gdpPerCapita': 40729,
      'unemploymentRate': 4.5,
      'population': 276944,
      'areaSize': 1132.89,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05974',
      'countyName': 'Soest, Kreis',
      'gdp': 10869237,
      'gdpPerCapita': 36015,
      'unemploymentRate': 5.0,
      'population': 301785,
      'areaSize': 1328.63,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '05978',
      'countyName': 'Unna, Kreis',
      'gdp': 12315294,
      'gdpPerCapita': 31229,
      'unemploymentRate': 6.8,
      'population': 394891,
      'areaSize': 543.21,
      'stateId': '05',
      'state': 'Nordrhein-Westfalen',
      'region': 'West Germany'},
     {'countyId': '06411',
      'countyName': 'Darmstadt, kreisfreie Stadt',
      'gdp': 12475252,
      'gdpPerCapita': 78594,
      'unemploymentRate': 5.0,
      'population': 159878,
      'areaSize': 122.07,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06412',
      'countyName': 'Frankfurt am Main, kreisfreie Stadt',
      'gdp': 70639270,
      'gdpPerCapita': 94190,
      'unemploymentRate': 5.0,
      'population': 763380,
      'areaSize': 248.31,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06413',
      'countyName': 'Offenbach am Main, kreisfreie Stadt',
      'gdp': 4720396,
      'gdpPerCapita': 36964,
      'unemploymentRate': 8.6,
      'population': 130280,
      'areaSize': 44.88,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06414',
      'countyName': 'Wiesbaden, Landeshauptstadt, kreisfreie Stadt',
      'gdp': 17603732,
      'gdpPerCapita': 63210,
      'unemploymentRate': 6.3,
      'population': 278474,
      'areaSize': 203.87,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06431',
      'countyName': 'Bergstraße, Landkreis',
      'gdp': 7750914,
      'gdpPerCapita': 28788,
      'unemploymentRate': 3.5,
      'population': 270340,
      'areaSize': 719.47,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06432',
      'countyName': 'Darmstadt-Dieburg, Landkreis',
      'gdp': 8532278,
      'gdpPerCapita': 28755,
      'unemploymentRate': 4.3,
      'population': 297844,
      'areaSize': 658.64,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06433',
      'countyName': 'Groß-Gerau, Landkreis',
      'gdp': 12522473,
      'gdpPerCapita': 45876,
      'unemploymentRate': 4.7,
      'population': 275726,
      'areaSize': 453.03,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06434',
      'countyName': 'Hochtaunuskreis',
      'gdp': 11644023,
      'gdpPerCapita': 49281,
      'unemploymentRate': 3.4,
      'population': 236914,
      'areaSize': 481.84,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06435',
      'countyName': 'Main-Kinzig-Kreis',
      'gdp': 15346471,
      'gdpPerCapita': 36663,
      'unemploymentRate': 4.1,
      'population': 420552,
      'areaSize': 1397.32,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06436',
      'countyName': 'Main-Taunus-Kreis',
      'gdp': 13001531,
      'gdpPerCapita': 54777,
      'unemploymentRate': 3.3,
      'population': 238558,
      'areaSize': 222.53,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06437',
      'countyName': 'Odenwaldkreis',
      'gdp': 2565968,
      'gdpPerCapita': 26536,
      'unemploymentRate': 4.4,
      'population': 96703,
      'areaSize': 623.97,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06438',
      'countyName': 'Offenbach, Landkreis',
      'gdp': 14473363,
      'gdpPerCapita': 41014,
      'unemploymentRate': 4.0,
      'population': 355813,
      'areaSize': 356.24,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06439',
      'countyName': 'Rheingau-Taunus-Kreis',
      'gdp': 4705013,
      'gdpPerCapita': 25177,
      'unemploymentRate': 3.9,
      'population': 187160,
      'areaSize': 811.41,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06440',
      'countyName': 'Wetteraukreis',
      'gdp': 9084892,
      'gdpPerCapita': 29700,
      'unemploymentRate': 3.8,
      'population': 308339,
      'areaSize': 1100.66,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06531',
      'countyName': 'Gießen, Landkreis',
      'gdp': 9713363,
      'gdpPerCapita': 36248,
      'unemploymentRate': 5.3,
      'population': 270688,
      'areaSize': 854.56,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06532',
      'countyName': 'Lahn-Dill-Kreis',
      'gdp': 8719032,
      'gdpPerCapita': 34331,
      'unemploymentRate': 4.8,
      'population': 253319,
      'areaSize': 1066.3,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06533',
      'countyName': 'Limburg-Weilburg, Landkreis',
      'gdp': 5288818,
      'gdpPerCapita': 30744,
      'unemploymentRate': 4.0,
      'population': 171912,
      'areaSize': 738.44,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06534',
      'countyName': 'Marburg-Biedenkopf, Landkreis',
      'gdp': 9490872,
      'gdpPerCapita': 38517,
      'unemploymentRate': 3.7,
      'population': 247084,
      'areaSize': 1262.37,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06535',
      'countyName': 'Vogelsbergkreis',
      'gdp': 2897329,
      'gdpPerCapita': 27291,
      'unemploymentRate': 3.7,
      'population': 105643,
      'areaSize': 1458.91,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06611',
      'countyName': 'Kassel, kreisfreie Stadt',
      'gdp': 10403602,
      'gdpPerCapita': 51718,
      'unemploymentRate': 7.3,
      'population': 202137,
      'areaSize': 106.8,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06631',
      'countyName': 'Fulda, Landkreis',
      'gdp': 8365628,
      'gdpPerCapita': 37652,
      'unemploymentRate': 2.7,
      'population': 223145,
      'areaSize': 1380.41,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06632',
      'countyName': 'Hersfeld-Rotenburg, Landkreis',
      'gdp': 4418978,
      'gdpPerCapita': 36531,
      'unemploymentRate': 3.6,
      'population': 120719,
      'areaSize': 1097.75,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06633',
      'countyName': 'Kassel, Landkreis',
      'gdp': 7181513,
      'gdpPerCapita': 30346,
      'unemploymentRate': 3.6,
      'population': 236764,
      'areaSize': 1293.31,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06634',
      'countyName': 'Schwalm-Eder-Kreis',
      'gdp': 5586361,
      'gdpPerCapita': 30951,
      'unemploymentRate': 3.2,
      'population': 179673,
      'areaSize': 1539.01,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06635',
      'countyName': 'Waldeck-Frankenberg, Landkreis',
      'gdp': 5933875,
      'gdpPerCapita': 37770,
      'unemploymentRate': 3.4,
      'population': 156406,
      'areaSize': 1848.7,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '06636',
      'countyName': 'Werra-Meißner-Kreis',
      'gdp': 2524832,
      'gdpPerCapita': 24984,
      'unemploymentRate': 4.7,
      'population': 100629,
      'areaSize': 1024.83,
      'stateId': '06',
      'state': 'Hessen',
      'region': 'West Germany'},
     {'countyId': '07111',
      'countyName': 'Koblenz, kreisfreie Stadt',
      'gdp': 7759109,
      'gdpPerCapita': 68102,
      'unemploymentRate': 5.5,
      'population': 114052,
      'areaSize': 105.25,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07131',
      'countyName': 'Ahrweiler, Landkreis',
      'gdp': 3423961,
      'gdpPerCapita': 26477,
      'unemploymentRate': 3.4,
      'population': 130086,
      'areaSize': 787.02,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07132',
      'countyName': 'Altenkirchen (Westerwald), Landkreis',
      'gdp': 3506346,
      'gdpPerCapita': 27234,
      'unemploymentRate': 4.2,
      'population': 128805,
      'areaSize': 642.38,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07133',
      'countyName': 'Bad Kreuznach, Landkreis',
      'gdp': 4694795,
      'gdpPerCapita': 29749,
      'unemploymentRate': 5.5,
      'population': 158345,
      'areaSize': 863.89,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07134',
      'countyName': 'Birkenfeld, Landkreis',
      'gdp': 2367318,
      'gdpPerCapita': 29326,
      'unemploymentRate': 5.6,
      'population': 80951,
      'areaSize': 776.83,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07135',
      'countyName': 'Cochem-Zell, Landkreis',
      'gdp': 1890273,
      'gdpPerCapita': 30674,
      'unemploymentRate': 3.0,
      'population': 61375,
      'areaSize': 692.43,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07137',
      'countyName': 'Mayen-Koblenz, Landkreis',
      'gdp': 6668528,
      'gdpPerCapita': 31175,
      'unemploymentRate': 3.1,
      'population': 214434,
      'areaSize': 817.73,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07138',
      'countyName': 'Neuwied, Landkreis',
      'gdp': 5974356,
      'gdpPerCapita': 32863,
      'unemploymentRate': 4.6,
      'population': 182811,
      'areaSize': 627.05,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07140',
      'countyName': 'Rhein-Hunsrück-Kreis',
      'gdp': 3707797,
      'gdpPerCapita': 36020,
      'unemploymentRate': 3.2,
      'population': 103163,
      'areaSize': 991.06,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07141',
      'countyName': 'Rhein-Lahn-Kreis',
      'gdp': 3245990,
      'gdpPerCapita': 26532,
      'unemploymentRate': 2.8,
      'population': 122297,
      'areaSize': 782.24,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07143',
      'countyName': 'Westerwaldkreis',
      'gdp': 6768357,
      'gdpPerCapita': 33620,
      'unemploymentRate': 2.8,
      'population': 201904,
      'areaSize': 989.04,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07211',
      'countyName': 'Trier, kreisfreie Stadt',
      'gdp': 4876153,
      'gdpPerCapita': 44198,
      'unemploymentRate': 4.9,
      'population': 111528,
      'areaSize': 117.06,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07231',
      'countyName': 'Bernkastel-Wittlich, Landkreis',
      'gdp': 3501260,
      'gdpPerCapita': 31206,
      'unemploymentRate': 3.0,
      'population': 112483,
      'areaSize': 1167.92,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07232',
      'countyName': 'Eifelkreis Bitburg-Prüm',
      'gdp': 2764268,
      'gdpPerCapita': 28096,
      'unemploymentRate': 2.4,
      'population': 99058,
      'areaSize': 1626.95,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07233',
      'countyName': 'Vulkaneifel, Landkreis',
      'gdp': 2008240,
      'gdpPerCapita': 33110,
      'unemploymentRate': 3.7,
      'population': 60646,
      'areaSize': 911.64,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07235',
      'countyName': 'Trier-Saarburg, Landkreis',
      'gdp': 2985279,
      'gdpPerCapita': 20071,
      'unemploymentRate': 2.6,
      'population': 149398,
      'areaSize': 1102.26,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07311',
      'countyName': 'Frankenthal (Pfalz), kreisfreie Stadt',
      'gdp': 1647259,
      'gdpPerCapita': 33972,
      'unemploymentRate': 6.7,
      'population': 48762,
      'areaSize': 43.88,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07312',
      'countyName': 'Kaiserslautern, kreisfreie Stadt',
      'gdp': 4790792,
      'gdpPerCapita': 48021,
      'unemploymentRate': 8.6,
      'population': 100030,
      'areaSize': 139.7,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07313',
      'countyName': 'Landau in der Pfalz, kreisfreie Stadt',
      'gdp': 1971335,
      'gdpPerCapita': 42409,
      'unemploymentRate': 4.7,
      'population': 46881,
      'areaSize': 82.94,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07314',
      'countyName': 'Ludwigshafen am Rhein, kreisfreie Stadt',
      'gdp': 13715402,
      'gdpPerCapita': 80784,
      'unemploymentRate': 8.1,
      'population': 172253,
      'areaSize': 77.43,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07315',
      'countyName': 'Mainz, kreisfreie Stadt',
      'gdp': 12278107,
      'gdpPerCapita': 56813,
      'unemploymentRate': 5.3,
      'population': 218578,
      'areaSize': 97.73,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07316',
      'countyName': 'Neustadt an der Weinstraße, kreisfreie Stadt',
      'gdp': 1659520,
      'gdpPerCapita': 31165,
      'unemploymentRate': 5.1,
      'population': 53264,
      'areaSize': 117.09,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07317',
      'countyName': 'Pirmasens, kreisfreie Stadt',
      'gdp': 1519552,
      'gdpPerCapita': 37503,
      'unemploymentRate': 10.7,
      'population': 40231,
      'areaSize': 61.35,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07318',
      'countyName': 'Speyer, kreisfreie Stadt',
      'gdp': 2668172,
      'gdpPerCapita': 52674,
      'unemploymentRate': 5.7,
      'population': 50561,
      'areaSize': 42.71,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07319',
      'countyName': 'Worms, kreisfreie Stadt',
      'gdp': 3181229,
      'gdpPerCapita': 38233,
      'unemploymentRate': 6.6,
      'population': 83542,
      'areaSize': 108.73,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07320',
      'countyName': 'Zweibrücken, kreisfreie Stadt',
      'gdp': 1698332,
      'gdpPerCapita': 49601,
      'unemploymentRate': 5.9,
      'population': 34193,
      'areaSize': 70.64,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07331',
      'countyName': 'Alzey-Worms, Landkreis',
      'gdp': 3227415,
      'gdpPerCapita': 25042,
      'unemploymentRate': 3.6,
      'population': 129687,
      'areaSize': 588.07,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07332',
      'countyName': 'Bad Dürkheim, Landkreis',
      'gdp': 2951279,
      'gdpPerCapita': 22240,
      'unemploymentRate': 3.5,
      'population': 132671,
      'areaSize': 594.64,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07333',
      'countyName': 'Donnersbergkreis',
      'gdp': 2172668,
      'gdpPerCapita': 28930,
      'unemploymentRate': 4.6,
      'population': 75325,
      'areaSize': 645.41,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07334',
      'countyName': 'Germersheim, Landkreis',
      'gdp': 4786766,
      'gdpPerCapita': 37171,
      'unemploymentRate': 3.8,
      'population': 129013,
      'areaSize': 463.32,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07335',
      'countyName': 'Kaiserslautern, Landkreis',
      'gdp': 2185386,
      'gdpPerCapita': 20645,
      'unemploymentRate': 4.8,
      'population': 105979,
      'areaSize': 640.0,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07336',
      'countyName': 'Kusel, Landkreis',
      'gdp': 1248941,
      'gdpPerCapita': 17679,
      'unemploymentRate': 4.2,
      'population': 70219,
      'areaSize': 573.61,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07337',
      'countyName': 'Südliche Weinstraße, Landkreis',
      'gdp': 2991098,
      'gdpPerCapita': 27071,
      'unemploymentRate': 3.5,
      'population': 110521,
      'areaSize': 639.93,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07338',
      'countyName': 'Rhein-Pfalz-Kreis',
      'gdp': 3077376,
      'gdpPerCapita': 19994,
      'unemploymentRate': 3.4,
      'population': 154609,
      'areaSize': 304.99,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07339',
      'countyName': 'Mainz-Bingen, Landkreis',
      'gdp': 7556313,
      'gdpPerCapita': 35925,
      'unemploymentRate': 3.4,
      'population': 211417,
      'areaSize': 605.36,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '07340',
      'countyName': 'Südwestpfalz, Landkreis',
      'gdp': 1545905,
      'gdpPerCapita': 16222,
      'unemploymentRate': 3.7,
      'population': 94831,
      'areaSize': 953.53,
      'stateId': '07',
      'state': 'Rheinland-Pfalz',
      'region': 'West Germany'},
     {'countyId': '08111',
      'countyName': 'Stuttgart, Landeshauptstadt, Stadtkreis',
      'gdp': 57587318,
      'gdpPerCapita': 90862,
      'unemploymentRate': 4.1,
      'population': 635911,
      'areaSize': 207.33,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08115',
      'countyName': 'Böblingen, Landkreis',
      'gdp': 26001824,
      'gdpPerCapita': 66570,
      'unemploymentRate': 2.8,
      'population': 392807,
      'areaSize': 617.76,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08116',
      'countyName': 'Esslingen, Landkreis',
      'gdp': 22907177,
      'gdpPerCapita': 42965,
      'unemploymentRate': 3.2,
      'population': 535024,
      'areaSize': 641.28,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08117',
      'countyName': 'Göppingen, Landkreis',
      'gdp': 8613042,
      'gdpPerCapita': 33540,
      'unemploymentRate': 3.5,
      'population': 258145,
      'areaSize': 642.34,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08118',
      'countyName': 'Ludwigsburg, Landkreis',
      'gdp': 25598139,
      'gdpPerCapita': 47115,
      'unemploymentRate': 2.8,
      'population': 545423,
      'areaSize': 686.77,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08119',
      'countyName': 'Rems-Murr-Kreis, Landkreis',
      'gdp': 15103133,
      'gdpPerCapita': 35494,
      'unemploymentRate': 3.1,
      'population': 427248,
      'areaSize': 858.08,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08121',
      'countyName': 'Heilbronn, Universitätsstadt, Stadtkreis',
      'gdp': 7057202,
      'gdpPerCapita': 56216,
      'unemploymentRate': 4.7,
      'population': 126592,
      'areaSize': 99.9,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08125',
      'countyName': 'Heilbronn, Landkreis',
      'gdp': 19666035,
      'gdpPerCapita': 57516,
      'unemploymentRate': 2.8,
      'population': 344456,
      'areaSize': 1099.91,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08126',
      'countyName': 'Hohenlohekreis, Landkreis',
      'gdp': 5563124,
      'gdpPerCapita': 49804,
      'unemploymentRate': 2.4,
      'population': 112655,
      'areaSize': 776.76,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08127',
      'countyName': 'Schwäbisch Hall, Landkreis',
      'gdp': 8887817,
      'gdpPerCapita': 45571,
      'unemploymentRate': 2.7,
      'population': 196761,
      'areaSize': 1484.07,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08128',
      'countyName': 'Main-Tauber-Kreis, Landkreis',
      'gdp': 5226583,
      'gdpPerCapita': 39519,
      'unemploymentRate': 2.6,
      'population': 132399,
      'areaSize': 1304.12,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08135',
      'countyName': 'Heidenheim, Landkreis',
      'gdp': 4881819,
      'gdpPerCapita': 36917,
      'unemploymentRate': 3.8,
      'population': 132777,
      'areaSize': 627.13,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08136',
      'countyName': 'Ostalbkreis, Landkreis',
      'gdp': 14069653,
      'gdpPerCapita': 44921,
      'unemploymentRate': 2.8,
      'population': 314025,
      'areaSize': 1511.39,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08211',
      'countyName': 'Baden-Baden, Stadtkreis',
      'gdp': 3030937,
      'gdpPerCapita': 55187,
      'unemploymentRate': 4.3,
      'population': 55185,
      'areaSize': 140.19,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08212',
      'countyName': 'Karlsruhe, Stadtkreis',
      'gdp': 20677365,
      'gdpPerCapita': 66166,
      'unemploymentRate': 3.9,
      'population': 312060,
      'areaSize': 173.42,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08215',
      'countyName': 'Karlsruhe, Landkreis',
      'gdp': 16851311,
      'gdpPerCapita': 38000,
      'unemploymentRate': 2.8,
      'population': 445101,
      'areaSize': 1084.98,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08216',
      'countyName': 'Rastatt, Landkreis',
      'gdp': 10183907,
      'gdpPerCapita': 44159,
      'unemploymentRate': 2.9,
      'population': 231420,
      'areaSize': 738.43,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08221',
      'countyName': 'Heidelberg, Stadtkreis',
      'gdp': 9120232,
      'gdpPerCapita': 56832,
      'unemploymentRate': 4.0,
      'population': 161485,
      'areaSize': 108.83,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08222',
      'countyName': 'Mannheim, Stadtkreis',
      'gdp': 21006106,
      'gdpPerCapita': 68051,
      'unemploymentRate': 5.3,
      'population': 310658,
      'areaSize': 144.97,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08225',
      'countyName': 'Neckar-Odenwald-Kreis, Landkreis',
      'gdp': 4419891,
      'gdpPerCapita': 30810,
      'unemploymentRate': 3.0,
      'population': 143633,
      'areaSize': 1125.95,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08226',
      'countyName': 'Rhein-Neckar-Kreis, Landkreis',
      'gdp': 19005716,
      'gdpPerCapita': 34734,
      'unemploymentRate': 3.5,
      'population': 548355,
      'areaSize': 1061.55,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08231',
      'countyName': 'Pforzheim, Stadtkreis',
      'gdp': 5071132,
      'gdpPerCapita': 40596,
      'unemploymentRate': 5.6,
      'population': 125957,
      'areaSize': 97.99,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08235',
      'countyName': 'Calw, Landkreis',
      'gdp': 4593152,
      'gdpPerCapita': 29087,
      'unemploymentRate': 2.9,
      'population': 159201,
      'areaSize': 797.29,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08236',
      'countyName': 'Enzkreis, Landkreis',
      'gdp': 6140658,
      'gdpPerCapita': 30914,
      'unemploymentRate': 2.3,
      'population': 199556,
      'areaSize': 573.6,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08237',
      'countyName': 'Freudenstadt, Landkreis',
      'gdp': 4684886,
      'gdpPerCapita': 39805,
      'unemploymentRate': 2.8,
      'population': 118243,
      'areaSize': 870.4,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08311',
      'countyName': 'Freiburg im Breisgau, Stadtkreis',
      'gdp': 11961878,
      'gdpPerCapita': 52022,
      'unemploymentRate': 4.9,
      'population': 231195,
      'areaSize': 153.04,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08315',
      'countyName': 'Breisgau-Hochschwarzwald, Landkreis',
      'gdp': 7828233,
      'gdpPerCapita': 29810,
      'unemploymentRate': 2.7,
      'population': 263601,
      'areaSize': 1378.32,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08316',
      'countyName': 'Emmendingen, Landkreis',
      'gdp': 5383783,
      'gdpPerCapita': 32619,
      'unemploymentRate': 2.5,
      'population': 166408,
      'areaSize': 679.8,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08317',
      'countyName': 'Ortenaukreis, Landkreis',
      'gdp': 17648049,
      'gdpPerCapita': 41262,
      'unemploymentRate': 2.9,
      'population': 430953,
      'areaSize': 1850.35,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08325',
      'countyName': 'Rottweil, Landkreis',
      'gdp': 6157040,
      'gdpPerCapita': 44245,
      'unemploymentRate': 2.3,
      'population': 139878,
      'areaSize': 769.42,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08326',
      'countyName': 'Schwarzwald-Baar-Kreis, Landkreis',
      'gdp': 8365397,
      'gdpPerCapita': 39498,
      'unemploymentRate': 3.0,
      'population': 212506,
      'areaSize': 1025.34,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08327',
      'countyName': 'Tuttlingen, Landkreis',
      'gdp': 6907474,
      'gdpPerCapita': 49419,
      'unemploymentRate': 2.7,
      'population': 140766,
      'areaSize': 734.38,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08335',
      'countyName': 'Konstanz, Landkreis',
      'gdp': 9955746,
      'gdpPerCapita': 34973,
      'unemploymentRate': 3.1,
      'population': 286305,
      'areaSize': 817.98,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08336',
      'countyName': 'Lörrach, Landkreis',
      'gdp': 7754204,
      'gdpPerCapita': 33939,
      'unemploymentRate': 3.4,
      'population': 228736,
      'areaSize': 806.67,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08337',
      'countyName': 'Waldshut, Landkreis',
      'gdp': 5318193,
      'gdpPerCapita': 31208,
      'unemploymentRate': 2.9,
      'population': 171003,
      'areaSize': 1131.14,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08415',
      'countyName': 'Reutlingen, Landkreis',
      'gdp': 11591847,
      'gdpPerCapita': 40495,
      'unemploymentRate': 3.3,
      'population': 287034,
      'areaSize': 1027.84,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08416',
      'countyName': 'Tübingen, Landkreis',
      'gdp': 7674339,
      'gdpPerCapita': 33876,
      'unemploymentRate': 2.6,
      'population': 228678,
      'areaSize': 519.11,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08417',
      'countyName': 'Zollernalbkreis, Landkreis',
      'gdp': 6671583,
      'gdpPerCapita': 35383,
      'unemploymentRate': 3.2,
      'population': 189363,
      'areaSize': 917.58,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08421',
      'countyName': 'Ulm, Stadtkreis',
      'gdp': 9732311,
      'gdpPerCapita': 77263,
      'unemploymentRate': 3.3,
      'population': 126790,
      'areaSize': 118.68,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08425',
      'countyName': 'Alb-Donau-Kreis, Landkreis',
      'gdp': 6267656,
      'gdpPerCapita': 32086,
      'unemploymentRate': 2.3,
      'population': 197076,
      'areaSize': 1358.54,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08426',
      'countyName': 'Biberach, Landkreis',
      'gdp': 10495417,
      'gdpPerCapita': 52740,
      'unemploymentRate': 2.0,
      'population': 201282,
      'areaSize': 1409.52,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08435',
      'countyName': 'Bodenseekreis, Landkreis',
      'gdp': 10996310,
      'gdpPerCapita': 51041,
      'unemploymentRate': 2.3,
      'population': 217470,
      'areaSize': 664.77,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08436',
      'countyName': 'Ravensburg, Landkreis',
      'gdp': 12789587,
      'gdpPerCapita': 45069,
      'unemploymentRate': 2.4,
      'population': 285424,
      'areaSize': 1632.08,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '08437',
      'countyName': 'Sigmaringen, Landkreis',
      'gdp': 4985050,
      'gdpPerCapita': 38190,
      'unemploymentRate': 2.7,
      'population': 130849,
      'areaSize': 1204.23,
      'stateId': '08',
      'state': 'Baden-Württemberg',
      'region': 'West Germany'},
     {'countyId': '09161',
      'countyName': 'Ingolstadt',
      'gdp': 17320976,
      'gdpPerCapita': 127254,
      'unemploymentRate': 2.9,
      'population': 137392,
      'areaSize': 133.35,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09162',
      'countyName': 'München, Landeshauptstadt',
      'gdp': 117934001,
      'gdpPerCapita': 80568,
      'unemploymentRate': 3.5,
      'population': 1484226,
      'areaSize': 310.7,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09163',
      'countyName': 'Rosenheim',
      'gdp': 3304615,
      'gdpPerCapita': 52287,
      'unemploymentRate': 3.9,
      'population': 63551,
      'areaSize': 37.22,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09171',
      'countyName': 'Altötting, Landkreis',
      'gdp': 5491544,
      'gdpPerCapita': 49574,
      'unemploymentRate': 2.8,
      'population': 111516,
      'areaSize': 569.28,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09172',
      'countyName': 'Berchtesgadener Land, Landkreis',
      'gdp': 3517557,
      'gdpPerCapita': 33378,
      'unemploymentRate': 3.3,
      'population': 105929,
      'areaSize': 839.82,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09173',
      'countyName': 'Bad Tölz-Wolfratshausen, Landkreis',
      'gdp': 3805991,
      'gdpPerCapita': 29992,
      'unemploymentRate': 2.1,
      'population': 127917,
      'areaSize': 1110.67,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09174',
      'countyName': 'Dachau, Landkreis',
      'gdp': 4488958,
      'gdpPerCapita': 29283,
      'unemploymentRate': 1.8,
      'population': 154899,
      'areaSize': 579.16,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09175',
      'countyName': 'Ebersberg, Landkreis',
      'gdp': 4667290,
      'gdpPerCapita': 32991,
      'unemploymentRate': 1.8,
      'population': 143649,
      'areaSize': 549.39,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09176',
      'countyName': 'Eichstätt, Landkreis',
      'gdp': 4747623,
      'gdpPerCapita': 35968,
      'unemploymentRate': 1.3,
      'population': 132881,
      'areaSize': 1213.85,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09177',
      'countyName': 'Erding, Landkreis',
      'gdp': 4223592,
      'gdpPerCapita': 30768,
      'unemploymentRate': 1.8,
      'population': 138182,
      'areaSize': 870.74,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09178',
      'countyName': 'Freising, Landkreis',
      'gdp': 8929877,
      'gdpPerCapita': 50011,
      'unemploymentRate': 2.0,
      'population': 180007,
      'areaSize': 799.85,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09179',
      'countyName': 'Fürstenfeldbruck, Landkreis',
      'gdp': 5914981,
      'gdpPerCapita': 27061,
      'unemploymentRate': 2.5,
      'population': 219311,
      'areaSize': 434.8,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09180',
      'countyName': 'Garmisch-Partenkirchen, Landkreis',
      'gdp': 2673124,
      'gdpPerCapita': 30269,
      'unemploymentRate': 2.7,
      'population': 88424,
      'areaSize': 1012.17,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09181',
      'countyName': 'Landsberg am Lech, Landkreis',
      'gdp': 4152585,
      'gdpPerCapita': 34719,
      'unemploymentRate': 2.2,
      'population': 120302,
      'areaSize': 804.36,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09182',
      'countyName': 'Miesbach, Landkreis',
      'gdp': 3646437,
      'gdpPerCapita': 36663,
      'unemploymentRate': 2.2,
      'population': 100010,
      'areaSize': 866.21,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09183',
      'countyName': 'Mühldorf a.Inn, Landkreis',
      'gdp': 3961914,
      'gdpPerCapita': 34491,
      'unemploymentRate': 3.0,
      'population': 115872,
      'areaSize': 805.33,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09184',
      'countyName': 'München, Landkreis',
      'gdp': 38600416,
      'gdpPerCapita': 111032,
      'unemploymentRate': 2.2,
      'population': 350473,
      'areaSize': 664.25,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09185',
      'countyName': 'Neuburg-Schrobenhausen, Landkreis',
      'gdp': 3620271,
      'gdpPerCapita': 37546,
      'unemploymentRate': 1.9,
      'population': 97303,
      'areaSize': 739.71,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09186',
      'countyName': 'Pfaffenhofen a.d.Ilm, Landkreis',
      'gdp': 4644208,
      'gdpPerCapita': 36656,
      'unemploymentRate': 1.6,
      'population': 128227,
      'areaSize': 761.05,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09187',
      'countyName': 'Rosenheim, Landkreis',
      'gdp': 8554458,
      'gdpPerCapita': 32874,
      'unemploymentRate': 2.2,
      'population': 261330,
      'areaSize': 1439.44,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09188',
      'countyName': 'Starnberg, Landkreis',
      'gdp': 6171224,
      'gdpPerCapita': 45437,
      'unemploymentRate': 2.4,
      'population': 136667,
      'areaSize': 487.71,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09189',
      'countyName': 'Traunstein, Landkreis',
      'gdp': 7236142,
      'gdpPerCapita': 40954,
      'unemploymentRate': 2.6,
      'population': 177319,
      'areaSize': 1533.76,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09190',
      'countyName': 'Weilheim-Schongau, Landkreis',
      'gdp': 5556473,
      'gdpPerCapita': 41220,
      'unemploymentRate': 2.1,
      'population': 135478,
      'areaSize': 966.28,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09261',
      'countyName': 'Landshut',
      'gdp': 4227790,
      'gdpPerCapita': 58884,
      'unemploymentRate': 4.2,
      'population': 73411,
      'areaSize': 65.83,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09262',
      'countyName': 'Passau',
      'gdp': 3537929,
      'gdpPerCapita': 67874,
      'unemploymentRate': 4.2,
      'population': 52803,
      'areaSize': 69.56,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09263',
      'countyName': 'Straubing',
      'gdp': 2532869,
      'gdpPerCapita': 53111,
      'unemploymentRate': 4.5,
      'population': 47791,
      'areaSize': 67.59,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09271',
      'countyName': 'Deggendorf, Landkreis',
      'gdp': 4862067,
      'gdpPerCapita': 40846,
      'unemploymentRate': 2.6,
      'population': 119478,
      'areaSize': 861.17,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09272',
      'countyName': 'Freyung-Grafenau, Landkreis',
      'gdp': 2383683,
      'gdpPerCapita': 30424,
      'unemploymentRate': 2.5,
      'population': 78362,
      'areaSize': 983.85,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09273',
      'countyName': 'Kelheim, Landkreis',
      'gdp': 3894959,
      'gdpPerCapita': 32007,
      'unemploymentRate': 2.3,
      'population': 123058,
      'areaSize': 1065.13,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09274',
      'countyName': 'Landshut, Landkreis',
      'gdp': 5849423,
      'gdpPerCapita': 37029,
      'unemploymentRate': 2.5,
      'population': 159895,
      'areaSize': 1347.55,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09275',
      'countyName': 'Passau, Landkreis',
      'gdp': 5880883,
      'gdpPerCapita': 30746,
      'unemploymentRate': 2.8,
      'population': 192656,
      'areaSize': 1530.09,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09276',
      'countyName': 'Regen, Landkreis',
      'gdp': 2557604,
      'gdpPerCapita': 32970,
      'unemploymentRate': 3.1,
      'population': 77410,
      'areaSize': 974.78,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09277',
      'countyName': 'Rottal-Inn, Landkreis',
      'gdp': 4039387,
      'gdpPerCapita': 33518,
      'unemploymentRate': 3.0,
      'population': 121502,
      'areaSize': 1281.2,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09278',
      'countyName': 'Straubing-Bogen, Landkreis',
      'gdp': 2834488,
      'gdpPerCapita': 28276,
      'unemploymentRate': 2.4,
      'population': 101120,
      'areaSize': 1201.61,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09279',
      'countyName': 'Dingolfing-Landau, Landkreis',
      'gdp': 5807544,
      'gdpPerCapita': 60480,
      'unemploymentRate': 2.9,
      'population': 96683,
      'areaSize': 877.58,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09361',
      'countyName': 'Amberg',
      'gdp': 2588310,
      'gdpPerCapita': 61467,
      'unemploymentRate': 4.2,
      'population': 42207,
      'areaSize': 50.13,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09362',
      'countyName': 'Regensburg',
      'gdp': 13238776,
      'gdpPerCapita': 87240,
      'unemploymentRate': 3.4,
      'population': 153094,
      'areaSize': 80.86,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09363',
      'countyName': 'Weiden i.d.OPf.',
      'gdp': 2361687,
      'gdpPerCapita': 55527,
      'unemploymentRate': 5.2,
      'population': 42743,
      'areaSize': 70.57,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09371',
      'countyName': 'Amberg-Sulzbach, Landkreis',
      'gdp': 2862911,
      'gdpPerCapita': 27803,
      'unemploymentRate': 2.3,
      'population': 103049,
      'areaSize': 1255.86,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09372',
      'countyName': 'Cham, Landkreis',
      'gdp': 4799900,
      'gdpPerCapita': 37614,
      'unemploymentRate': 2.5,
      'population': 127998,
      'areaSize': 1526.82,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09373',
      'countyName': 'Neumarkt i.d.OPf., Landkreis',
      'gdp': 5192972,
      'gdpPerCapita': 39015,
      'unemploymentRate': 1.7,
      'population': 134573,
      'areaSize': 1343.96,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09374',
      'countyName': 'Neustadt a.d.Waldnaab, Landkreis',
      'gdp': 3034458,
      'gdpPerCapita': 32138,
      'unemploymentRate': 2.8,
      'population': 94450,
      'areaSize': 1427.69,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09375',
      'countyName': 'Regensburg, Landkreis',
      'gdp': 4929446,
      'gdpPerCapita': 25556,
      'unemploymentRate': 1.9,
      'population': 194070,
      'areaSize': 1391.65,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09376',
      'countyName': 'Schwandorf, Landkreis',
      'gdp': 5369314,
      'gdpPerCapita': 36566,
      'unemploymentRate': 2.8,
      'population': 147872,
      'areaSize': 1458.34,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09377',
      'countyName': 'Tirschenreuth, Landkreis',
      'gdp': 2646426,
      'gdpPerCapita': 36444,
      'unemploymentRate': 3.0,
      'population': 72046,
      'areaSize': 1084.25,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09461',
      'countyName': 'Bamberg',
      'gdp': 4958473,
      'gdpPerCapita': 64075,
      'unemploymentRate': 3.8,
      'population': 77373,
      'areaSize': 54.62,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09462',
      'countyName': 'Bayreuth',
      'gdp': 4809437,
      'gdpPerCapita': 64706,
      'unemploymentRate': 4.2,
      'population': 74783,
      'areaSize': 66.89,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09463',
      'countyName': 'Coburg',
      'gdp': 4017820,
      'gdpPerCapita': 97418,
      'unemploymentRate': 4.9,
      'population': 41072,
      'areaSize': 48.29,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09464',
      'countyName': 'Hof',
      'gdp': 1985619,
      'gdpPerCapita': 43222,
      'unemploymentRate': 5.6,
      'population': 45825,
      'areaSize': 58.02,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09471',
      'countyName': 'Bamberg, Landkreis',
      'gdp': 3845563,
      'gdpPerCapita': 26190,
      'unemploymentRate': 2.1,
      'population': 147163,
      'areaSize': 1167.79,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09472',
      'countyName': 'Bayreuth, Landkreis',
      'gdp': 2269592,
      'gdpPerCapita': 21880,
      'unemploymentRate': 2.6,
      'population': 103664,
      'areaSize': 1273.62,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09473',
      'countyName': 'Coburg, Landkreis',
      'gdp': 2376009,
      'gdpPerCapita': 27343,
      'unemploymentRate': 3.1,
      'population': 86747,
      'areaSize': 590.42,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09474',
      'countyName': 'Forchheim, Landkreis',
      'gdp': 3568791,
      'gdpPerCapita': 30795,
      'unemploymentRate': 2.4,
      'population': 116203,
      'areaSize': 642.82,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09475',
      'countyName': 'Hof, Landkreis',
      'gdp': 3360224,
      'gdpPerCapita': 35170,
      'unemploymentRate': 2.9,
      'population': 94801,
      'areaSize': 892.52,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09476',
      'countyName': 'Kronach, Landkreis',
      'gdp': 2204223,
      'gdpPerCapita': 32750,
      'unemploymentRate': 3.2,
      'population': 66743,
      'areaSize': 651.49,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09477',
      'countyName': 'Kulmbach, Landkreis',
      'gdp': 2535871,
      'gdpPerCapita': 35255,
      'unemploymentRate': 3.3,
      'population': 71566,
      'areaSize': 658.33,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09478',
      'countyName': 'Lichtenfels, Landkreis',
      'gdp': 2434620,
      'gdpPerCapita': 36442,
      'unemploymentRate': 3.4,
      'population': 66776,
      'areaSize': 519.94,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09479',
      'countyName': 'Wunsiedel i.Fichtelgebirge, Landkreis',
      'gdp': 2567914,
      'gdpPerCapita': 35018,
      'unemploymentRate': 4.3,
      'population': 72655,
      'areaSize': 606.37,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09561',
      'countyName': 'Ansbach',
      'gdp': 2432023,
      'gdpPerCapita': 58252,
      'unemploymentRate': 3.6,
      'population': 41798,
      'areaSize': 99.91,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09562',
      'countyName': 'Erlangen',
      'gdp': 10838267,
      'gdpPerCapita': 97222,
      'unemploymentRate': 3.5,
      'population': 112528,
      'areaSize': 76.96,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09563',
      'countyName': 'Fürth',
      'gdp': 4805398,
      'gdpPerCapita': 37797,
      'unemploymentRate': 4.8,
      'population': 128497,
      'areaSize': 63.35,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09564',
      'countyName': 'Nürnberg',
      'gdp': 31658858,
      'gdpPerCapita': 61261,
      'unemploymentRate': 5.2,
      'population': 518370,
      'areaSize': 186.45,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09565',
      'countyName': 'Schwabach',
      'gdp': 1492550,
      'gdpPerCapita': 36594,
      'unemploymentRate': 3.2,
      'population': 40981,
      'areaSize': 40.8,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09571',
      'countyName': 'Ansbach, Landkreis',
      'gdp': 5747819,
      'gdpPerCapita': 31306,
      'unemploymentRate': 2.2,
      'population': 184591,
      'areaSize': 1971.33,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09572',
      'countyName': 'Erlangen-Höchstadt, Landkreis',
      'gdp': 5245235,
      'gdpPerCapita': 38624,
      'unemploymentRate': 1.8,
      'population': 137262,
      'areaSize': 564.55,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09573',
      'countyName': 'Fürth, Landkreis',
      'gdp': 2744336,
      'gdpPerCapita': 23498,
      'unemploymentRate': 2.5,
      'population': 117853,
      'areaSize': 307.44,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09574',
      'countyName': 'Nürnberger Land, Landkreis',
      'gdp': 5408118,
      'gdpPerCapita': 31801,
      'unemploymentRate': 2.3,
      'population': 170792,
      'areaSize': 799.52,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09575',
      'countyName': 'Neustadt a.d.Aisch-Bad Windsheim, Landkreis',
      'gdp': 3004902,
      'gdpPerCapita': 30048,
      'unemploymentRate': 1.8,
      'population': 101014,
      'areaSize': 1267.44,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09576',
      'countyName': 'Roth, Landkreis',
      'gdp': 3755622,
      'gdpPerCapita': 29682,
      'unemploymentRate': 2.0,
      'population': 126749,
      'areaSize': 895.16,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09577',
      'countyName': 'Weißenburg-Gunzenhausen, Landkreis',
      'gdp': 2994690,
      'gdpPerCapita': 31757,
      'unemploymentRate': 2.9,
      'population': 94734,
      'areaSize': 970.78,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09661',
      'countyName': 'Aschaffenburg',
      'gdp': 5093031,
      'gdpPerCapita': 72521,
      'unemploymentRate': 4.9,
      'population': 71002,
      'areaSize': 62.45,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09662',
      'countyName': 'Schweinfurt',
      'gdp': 5638799,
      'gdpPerCapita': 104937,
      'unemploymentRate': 6.1,
      'population': 53426,
      'areaSize': 35.7,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09663',
      'countyName': 'Würzburg',
      'gdp': 8185077,
      'gdpPerCapita': 64319,
      'unemploymentRate': 3.4,
      'population': 127934,
      'areaSize': 87.6,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09671',
      'countyName': 'Aschaffenburg, Landkreis',
      'gdp': 5869444,
      'gdpPerCapita': 33715,
      'unemploymentRate': 2.6,
      'population': 174200,
      'areaSize': 698.9,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09672',
      'countyName': 'Bad Kissingen, Landkreis',
      'gdp': 3349398,
      'gdpPerCapita': 32442,
      'unemploymentRate': 3.0,
      'population': 103235,
      'areaSize': 1136.9,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09673',
      'countyName': 'Rhön-Grabfeld, Landkreis',
      'gdp': 3233425,
      'gdpPerCapita': 40548,
      'unemploymentRate': 2.5,
      'population': 79635,
      'areaSize': 1021.68,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09674',
      'countyName': 'Haßberge, Landkreis',
      'gdp': 2722371,
      'gdpPerCapita': 32205,
      'unemploymentRate': 2.6,
      'population': 84384,
      'areaSize': 956.19,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09675',
      'countyName': 'Kitzingen, Landkreis',
      'gdp': 3190039,
      'gdpPerCapita': 35183,
      'unemploymentRate': 2.1,
      'population': 91155,
      'areaSize': 684.14,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09676',
      'countyName': 'Miltenberg, Landkreis',
      'gdp': 4437070,
      'gdpPerCapita': 34498,
      'unemploymentRate': 2.8,
      'population': 128743,
      'areaSize': 715.58,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09677',
      'countyName': 'Main-Spessart, Landkreis',
      'gdp': 4659027,
      'gdpPerCapita': 36847,
      'unemploymentRate': 1.8,
      'population': 126158,
      'areaSize': 1321.2,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09678',
      'countyName': 'Schweinfurt, Landkreis',
      'gdp': 2575838,
      'gdpPerCapita': 22378,
      'unemploymentRate': 2.3,
      'population': 115445,
      'areaSize': 841.39,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09679',
      'countyName': 'Würzburg, Landkreis',
      'gdp': 4672288,
      'gdpPerCapita': 28915,
      'unemploymentRate': 1.9,
      'population': 162302,
      'areaSize': 968.35,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09761',
      'countyName': 'Augsburg',
      'gdp': 14481223,
      'gdpPerCapita': 49257,
      'unemploymentRate': 4.9,
      'population': 296582,
      'areaSize': 146.86,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09762',
      'countyName': 'Kaufbeuren',
      'gdp': 1708073,
      'gdpPerCapita': 39099,
      'unemploymentRate': 3.9,
      'population': 44398,
      'areaSize': 40.02,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09763',
      'countyName': 'Kempten (Allgäu)',
      'gdp': 3630732,
      'gdpPerCapita': 52911,
      'unemploymentRate': 3.2,
      'population': 69151,
      'areaSize': 63.28,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09764',
      'countyName': 'Memmingen',
      'gdp': 2650981,
      'gdpPerCapita': 60727,
      'unemploymentRate': 3.2,
      'population': 44100,
      'areaSize': 70.11,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09771',
      'countyName': 'Aichach-Friedberg, Landkreis',
      'gdp': 3704704,
      'gdpPerCapita': 27835,
      'unemploymentRate': 2.1,
      'population': 134655,
      'areaSize': 780.23,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09772',
      'countyName': 'Augsburg, Landkreis',
      'gdp': 7717496,
      'gdpPerCapita': 30786,
      'unemploymentRate': 2.4,
      'population': 253468,
      'areaSize': 1070.63,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09773',
      'countyName': 'Dillingen a.d.Donau, Landkreis',
      'gdp': 3411579,
      'gdpPerCapita': 35690,
      'unemploymentRate': 1.8,
      'population': 96562,
      'areaSize': 792.23,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09774',
      'countyName': 'Günzburg, Landkreis',
      'gdp': 5717632,
      'gdpPerCapita': 45692,
      'unemploymentRate': 1.9,
      'population': 127027,
      'areaSize': 762.4,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09775',
      'countyName': 'Neu-Ulm, Landkreis',
      'gdp': 6815799,
      'gdpPerCapita': 39313,
      'unemploymentRate': 2.2,
      'population': 175204,
      'areaSize': 515.84,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09776',
      'countyName': 'Lindau (Bodensee), Landkreis',
      'gdp': 3101468,
      'gdpPerCapita': 38097,
      'unemploymentRate': 2.3,
      'population': 81981,
      'areaSize': 323.39,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09777',
      'countyName': 'Ostallgäu, Landkreis',
      'gdp': 5049729,
      'gdpPerCapita': 36122,
      'unemploymentRate': 2.2,
      'population': 141182,
      'areaSize': 1394.43,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09778',
      'countyName': 'Unterallgäu, Landkreis',
      'gdp': 5458014,
      'gdpPerCapita': 38090,
      'unemploymentRate': 1.8,
      'population': 145341,
      'areaSize': 1229.57,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09779',
      'countyName': 'Donau-Ries, Landkreis',
      'gdp': 6605024,
      'gdpPerCapita': 49561,
      'unemploymentRate': 1.6,
      'population': 133783,
      'areaSize': 1274.58,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '09780',
      'countyName': 'Oberallgäu, Landkreis',
      'gdp': 5094400,
      'gdpPerCapita': 32875,
      'unemploymentRate': 2.2,
      'population': 156008,
      'areaSize': 1527.96,
      'stateId': '09',
      'state': 'Freistaat Bayern',
      'region': 'West Germany'},
     {'countyId': '10041',
      'countyName': 'Saarbrücken, Regionalverband',
      'gdp': 14761481,
      'gdpPerCapita': 44741,
      'unemploymentRate': 8.8,
      'population': 328714,
      'areaSize': 410.95,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '10041100',
      'countyName': 'Saarbrücken, Landeshauptstadt',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 10.5,
      'population': 180374,
      'areaSize': 167.52,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '10042',
      'countyName': 'Merzig-Wadern, Landkreis',
      'gdp': 2791689,
      'gdpPerCapita': 26970,
      'unemploymentRate': 4.2,
      'population': 103243,
      'areaSize': 556.66,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '10043',
      'countyName': 'Neunkirchen, Landkreis',
      'gdp': 3408492,
      'gdpPerCapita': 25676,
      'unemploymentRate': 6.7,
      'population': 131408,
      'areaSize': 249.8,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '10044',
      'countyName': 'Saarlouis, Landkreis',
      'gdp': 6416109,
      'gdpPerCapita': 32818,
      'unemploymentRate': 4.8,
      'population': 194319,
      'areaSize': 459.35,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '10045',
      'countyName': 'Saarpfalz-Kreis',
      'gdp': 5701085,
      'gdpPerCapita': 39863,
      'unemploymentRate': 4.8,
      'population': 142196,
      'areaSize': 418.27,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '10046',
      'countyName': 'St. Wendel, Landkreis',
      'gdp': 2664948,
      'gdpPerCapita': 30411,
      'unemploymentRate': 3.3,
      'population': 87007,
      'areaSize': 476.07,
      'stateId': '10',
      'state': 'Saarland',
      'region': 'West Germany'},
     {'countyId': '11000',
      'countyName': 'Berlin',
      'gdp': 149365483,
      'gdpPerCapita': 41157,
      'unemploymentRate': 7.8,
      'population': 3669491,
      'areaSize': 891.12,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11001001',
      'countyName': 'Berlin-Mitte',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 39.4,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11002002',
      'countyName': 'Berlin-Friedrichshain-Kreuzberg',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 20.4,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11003003',
      'countyName': 'Berlin-Pankow',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 103.22,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11004004',
      'countyName': 'Berlin-Charlottenburg-Wilmersdorf',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 64.69,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11005005',
      'countyName': 'Berlin-Spandau',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 91.88,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11006006',
      'countyName': 'Berlin-Steglitz-Zehlendorf',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 102.56,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11007007',
      'countyName': 'Berlin-Tempelhof-Schöneberg',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 53.05,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11008008',
      'countyName': 'Berlin-Neukölln',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 44.93,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11009009',
      'countyName': 'Berlin-Treptow-Köpenick',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 167.73,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11010010',
      'countyName': 'Berlin-Marzahn-Hellersdorf',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 61.82,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11011011',
      'countyName': 'Berlin-Lichtenberg',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 52.12,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '11012012',
      'countyName': 'Berlin-Reinickendorf',
      'gdp': 0,
      'gdpPerCapita': 0,
      'unemploymentRate': 0.0,
      'population': 0,
      'areaSize': 89.32,
      'stateId': '11',
      'state': 'Berlin',
      'region': 'East Germany'},
     {'countyId': '12051',
      'countyName': 'Brandenburg an der Havel, kreisfreie Stadt',
      'gdp': 2317748,
      'gdpPerCapita': 32189,
      'unemploymentRate': 8.1,
      'population': 72184,
      'areaSize': 229.72,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12052',
      'countyName': 'Cottbus, kreisfreie Stadt',
      'gdp': 3541363,
      'gdpPerCapita': 35193,
      'unemploymentRate': 7.6,
      'population': 99678,
      'areaSize': 165.62,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12053',
      'countyName': 'Frankfurt (Oder), kreisfreie Stadt',
      'gdp': 2169030,
      'gdpPerCapita': 37362,
      'unemploymentRate': 7.9,
      'population': 57751,
      'areaSize': 147.85,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12054',
      'countyName': 'Potsdam, kreisfreie Stadt',
      'gdp': 7590551,
      'gdpPerCapita': 42909,
      'unemploymentRate': 5.4,
      'population': 180334,
      'areaSize': 188.24,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12060',
      'countyName': 'Barnim, Landkreis',
      'gdp': 4049693,
      'gdpPerCapita': 22274,
      'unemploymentRate': 5.1,
      'population': 185244,
      'areaSize': 1479.58,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12061',
      'countyName': 'Dahme-Spreewald, Landkreis',
      'gdp': 5606761,
      'gdpPerCapita': 33335,
      'unemploymentRate': 3.7,
      'population': 170791,
      'areaSize': 2274.5,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12062',
      'countyName': 'Elbe-Elster, Landkreis',
      'gdp': 2539826,
      'gdpPerCapita': 24647,
      'unemploymentRate': 6.0,
      'population': 101827,
      'areaSize': 1899.19,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12063',
      'countyName': 'Havelland, Landkreis',
      'gdp': 3405652,
      'gdpPerCapita': 21112,
      'unemploymentRate': 5.2,
      'population': 162996,
      'areaSize': 1727.31,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12064',
      'countyName': 'Märkisch-Oderland, Landkreis',
      'gdp': 4160433,
      'gdpPerCapita': 21487,
      'unemploymentRate': 5.4,
      'population': 195751,
      'areaSize': 2158.65,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12065',
      'countyName': 'Oberhavel, Landkreis',
      'gdp': 5517892,
      'gdpPerCapita': 26204,
      'unemploymentRate': 4.9,
      'population': 212914,
      'areaSize': 1808.18,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12066',
      'countyName': 'Oberspreewald-Lausitz, Landkreis',
      'gdp': 3140592,
      'gdpPerCapita': 28345,
      'unemploymentRate': 7.5,
      'population': 109371,
      'areaSize': 1223.48,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12067',
      'countyName': 'Oder-Spree, Landkreis',
      'gdp': 4728423,
      'gdpPerCapita': 26489,
      'unemploymentRate': 6.1,
      'population': 178803,
      'areaSize': 2256.75,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12068',
      'countyName': 'Ostprignitz-Ruppin, Landkreis',
      'gdp': 2641627,
      'gdpPerCapita': 26623,
      'unemploymentRate': 6.2,
      'population': 98861,
      'areaSize': 2526.56,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12069',
      'countyName': 'Potsdam-Mittelmark, Landkreis',
      'gdp': 5508342,
      'gdpPerCapita': 25748,
      'unemploymentRate': 4.0,
      'population': 216566,
      'areaSize': 2592.02,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12070',
      'countyName': 'Prignitz, Landkreis',
      'gdp': 2035734,
      'gdpPerCapita': 26477,
      'unemploymentRate': 7.3,
      'population': 76158,
      'areaSize': 2138.54,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12071',
      'countyName': 'Spree-Neiße, Landkreis',
      'gdp': 4091277,
      'gdpPerCapita': 35594,
      'unemploymentRate': 6.3,
      'population': 113720,
      'areaSize': 1656.98,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12072',
      'countyName': 'Teltow-Fläming, Landkreis',
      'gdp': 5953419,
      'gdpPerCapita': 35523,
      'unemploymentRate': 4.3,
      'population': 169997,
      'areaSize': 2104.21,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '12073',
      'countyName': 'Uckermark, Landkreis',
      'gdp': 3568416,
      'gdpPerCapita': 29749,
      'unemploymentRate': 10.8,
      'population': 118947,
      'areaSize': 3077.03,
      'stateId': '12',
      'state': 'Brandenburg',
      'region': 'East Germany'},
     {'countyId': '13003',
      'countyName': 'Rostock, Hanse- und Universitätsstadt, Kreisfreie Stadt',
      'gdp': 7484717,
      'gdpPerCapita': 35872,
      'unemploymentRate': 6.8,
      'population': 209191,
      'areaSize': 181.36,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13004',
      'countyName': 'Schwerin, Landeshauptstadt, kreisfreie Stadtk',
      'gdp': 3785563,
      'gdpPerCapita': 39512,
      'unemploymentRate': 8.6,
      'population': 95653,
      'areaSize': 130.52,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13071',
      'countyName': 'Landkreis Mecklenburgische Seenplatte',
      'gdp': 7099185,
      'gdpPerCapita': 27320,
      'unemploymentRate': 8.7,
      'population': 258074,
      'areaSize': 5495.6,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13072',
      'countyName': 'Landkreis Rostock',
      'gdp': 5453342,
      'gdpPerCapita': 25379,
      'unemploymentRate': 5.3,
      'population': 215794,
      'areaSize': 3431.29,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13073',
      'countyName': 'Landkreis Vorpommern-Rügen',
      'gdp': 5579030,
      'gdpPerCapita': 24806,
      'unemploymentRate': 8.1,
      'population': 224702,
      'areaSize': 3216.02,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13074',
      'countyName': 'Landkreis Nordwestmecklenburg',
      'gdp': 3755500,
      'gdpPerCapita': 23942,
      'unemploymentRate': 5.8,
      'population': 157322,
      'areaSize': 2127.08,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13075',
      'countyName': 'Landkreis Vorpommern-Greifswald',
      'gdp': 5913217,
      'gdpPerCapita': 24963,
      'unemploymentRate': 8.6,
      'population': 235623,
      'areaSize': 3945.56,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '13076',
      'countyName': 'Landkreis Ludwigslust-Parchim',
      'gdp': 5182716,
      'gdpPerCapita': 24381,
      'unemploymentRate': 5.3,
      'population': 211779,
      'areaSize': 4766.78,
      'stateId': '13',
      'state': 'Mecklenburg-Vorpommern',
      'region': 'East Germany'},
     {'countyId': '14511',
      'countyName': 'Chemnitz, Stadt',
      'gdp': 8977947,
      'gdpPerCapita': 36341,
      'unemploymentRate': 6.5,
      'population': 246334,
      'areaSize': 221.05,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14521',
      'countyName': 'Erzgebirgskreis',
      'gdp': 8044381,
      'gdpPerCapita': 23727,
      'unemploymentRate': 4.4,
      'population': 334948,
      'areaSize': 1827.91,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14522',
      'countyName': 'Mittelsachsen, Landkreis',
      'gdp': 8348124,
      'gdpPerCapita': 27178,
      'unemploymentRate': 4.8,
      'population': 304099,
      'areaSize': 2116.85,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14523',
      'countyName': 'Vogtlandkreis',
      'gdp': 5838003,
      'gdpPerCapita': 25528,
      'unemploymentRate': 4.8,
      'population': 225997,
      'areaSize': 1412.42,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14524',
      'countyName': 'Zwickau, Landkreis',
      'gdp': 9852391,
      'gdpPerCapita': 30908,
      'unemploymentRate': 4.5,
      'population': 315002,
      'areaSize': 949.78,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14612',
      'countyName': 'Dresden, Stadt',
      'gdp': 22497044,
      'gdpPerCapita': 40692,
      'unemploymentRate': 5.6,
      'population': 556780,
      'areaSize': 328.48,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14625',
      'countyName': 'Bautzen, Landkreis',
      'gdp': 7910647,
      'gdpPerCapita': 26215,
      'unemploymentRate': 5.0,
      'population': 299758,
      'areaSize': 2395.6,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14626',
      'countyName': 'Görlitz, Landkreis',
      'gdp': 6960633,
      'gdpPerCapita': 27218,
      'unemploymentRate': 7.8,
      'population': 252725,
      'areaSize': 2111.41,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14627',
      'countyName': 'Meißen, Landkreis',
      'gdp': 6792993,
      'gdpPerCapita': 28011,
      'unemploymentRate': 5.3,
      'population': 241717,
      'areaSize': 1454.59,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14628',
      'countyName': 'Sächsische Schweiz-Osterzgebirge, Landkreis',
      'gdp': 5760202,
      'gdpPerCapita': 23462,
      'unemploymentRate': 4.5,
      'population': 245586,
      'areaSize': 1654.19,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14713',
      'countyName': 'Leipzig, Stadt',
      'gdp': 21722326,
      'gdpPerCapita': 37137,
      'unemploymentRate': 6.3,
      'population': 593145,
      'areaSize': 297.8,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14729',
      'countyName': 'Leipzig, Landkreis',
      'gdp': 6787587,
      'gdpPerCapita': 26320,
      'unemploymentRate': 5.0,
      'population': 258139,
      'areaSize': 1651.28,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '14730',
      'countyName': 'Nordsachsen, Landkreis',
      'gdp': 5418135,
      'gdpPerCapita': 27401,
      'unemploymentRate': 6.2,
      'population': 197741,
      'areaSize': 2028.56,
      'stateId': '14',
      'state': 'Freistaat Sachsen',
      'region': 'East Germany'},
     {'countyId': '15001',
      'countyName': 'Dessau-Roßlau, kreisfreie Stadt',
      'gdp': 2412521,
      'gdpPerCapita': 29538,
      'unemploymentRate': 7.7,
      'population': 80103,
      'areaSize': 244.71,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15002',
      'countyName': 'Halle (Saale), kreisfreie Stadt',
      'gdp': 7443991,
      'gdpPerCapita': 31118,
      'unemploymentRate': 8.2,
      'population': 238762,
      'areaSize': 135.03,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15003',
      'countyName': 'Magdeburg, kreisfreie Stadt',
      'gdp': 8314865,
      'gdpPerCapita': 34850,
      'unemploymentRate': 8.3,
      'population': 237565,
      'areaSize': 201.01,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15081',
      'countyName': 'Altmarkkreis Salzwedel',
      'gdp': 2002288,
      'gdpPerCapita': 23805,
      'unemploymentRate': 6.4,
      'population': 83173,
      'areaSize': 2293.74,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15082',
      'countyName': 'Anhalt-Bitterfeld, Landkreis',
      'gdp': 4681675,
      'gdpPerCapita': 29159,
      'unemploymentRate': 7.1,
      'population': 158486,
      'areaSize': 1453.84,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15083',
      'countyName': 'Börde, Landkreis',
      'gdp': 4820829,
      'gdpPerCapita': 27999,
      'unemploymentRate': 5.1,
      'population': 170923,
      'areaSize': 2366.99,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15084',
      'countyName': 'Burgenlandkreis',
      'gdp': 4539701,
      'gdpPerCapita': 25070,
      'unemploymentRate': 6.5,
      'population': 178846,
      'areaSize': 1413.95,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15085',
      'countyName': 'Harz, Landkreis',
      'gdp': 5172731,
      'gdpPerCapita': 24018,
      'unemploymentRate': 5.3,
      'population': 213310,
      'areaSize': 2104.75,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15086',
      'countyName': 'Jerichower Land, Landkreis',
      'gdp': 2318015,
      'gdpPerCapita': 25700,
      'unemploymentRate': 6.9,
      'population': 89589,
      'areaSize': 1577.08,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15087',
      'countyName': 'Mansfeld-Südharz, Landkreis',
      'gdp': 2848308,
      'gdpPerCapita': 20771,
      'unemploymentRate': 9.4,
      'population': 134942,
      'areaSize': 1449.01,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15088',
      'countyName': 'Saalekreis',
      'gdp': 6581941,
      'gdpPerCapita': 35571,
      'unemploymentRate': 6.3,
      'population': 183815,
      'areaSize': 1434.01,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15089',
      'countyName': 'Salzlandkreis',
      'gdp': 4783110,
      'gdpPerCapita': 24958,
      'unemploymentRate': 8.3,
      'population': 189125,
      'areaSize': 1427.5,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15090',
      'countyName': 'Stendal, Landkreis',
      'gdp': 2958930,
      'gdpPerCapita': 26282,
      'unemploymentRate': 8.7,
      'population': 111190,
      'areaSize': 2424.11,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '15091',
      'countyName': 'Wittenberg, Landkreis',
      'gdp': 3153967,
      'gdpPerCapita': 24967,
      'unemploymentRate': 6.2,
      'population': 124953,
      'areaSize': 1930.78,
      'stateId': '15',
      'state': 'Sachsen-Anhalt',
      'region': 'East Germany'},
     {'countyId': '16051',
      'countyName': 'Erfurt, kreisfreie Stadt',
      'gdp': 8535062,
      'gdpPerCapita': 40007,
      'unemploymentRate': 5.7,
      'population': 213981,
      'areaSize': 269.91,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16052',
      'countyName': 'Gera, kreisfreie Stadt',
      'gdp': 2706081,
      'gdpPerCapita': 28634,
      'unemploymentRate': 8.1,
      'population': 93125,
      'areaSize': 152.18,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16053',
      'countyName': 'Jena, kreisfreie Stadt',
      'gdp': 4990390,
      'gdpPerCapita': 44856,
      'unemploymentRate': 5.2,
      'population': 111343,
      'areaSize': 114.77,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16054',
      'countyName': 'Suhl, kreisfreie Stadt',
      'gdp': 1201794,
      'gdpPerCapita': 34336,
      'unemploymentRate': 5.0,
      'population': 36789,
      'areaSize': 141.62,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16055',
      'countyName': 'Weimar, kreisfreie Stadt',
      'gdp': 1971119,
      'gdpPerCapita': 30438,
      'unemploymentRate': 5.6,
      'population': 65228,
      'areaSize': 84.48,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16056',
      'countyName': 'Eisenach, kreisfreie Stadt',
      'gdp': 1679981,
      'gdpPerCapita': 39492,
      'unemploymentRate': 6.4,
      'population': 42250,
      'areaSize': 104.17,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16061',
      'countyName': 'Eichsfeld, Kreis',
      'gdp': 2620900,
      'gdpPerCapita': 26075,
      'unemploymentRate': 3.9,
      'population': 100006,
      'areaSize': 943.07,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16062',
      'countyName': 'Nordhausen, Kreis',
      'gdp': 2199544,
      'gdpPerCapita': 26104,
      'unemploymentRate': 7.0,
      'population': 83416,
      'areaSize': 713.9,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16063',
      'countyName': 'Wartburgkreis',
      'gdp': 3301139,
      'gdpPerCapita': 26753,
      'unemploymentRate': 3.9,
      'population': 118974,
      'areaSize': 1266.96,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16064',
      'countyName': 'Unstrut-Hainich-Kreis',
      'gdp': 2572705,
      'gdpPerCapita': 24927,
      'unemploymentRate': 6.8,
      'population': 102232,
      'areaSize': 979.68,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16065',
      'countyName': 'Kyffhäuserkreis',
      'gdp': 1683790,
      'gdpPerCapita': 22327,
      'unemploymentRate': 7.9,
      'population': 74212,
      'areaSize': 1037.91,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16066',
      'countyName': 'Schmalkalden-Meiningen, Kreis',
      'gdp': 3395053,
      'gdpPerCapita': 27681,
      'unemploymentRate': 4.0,
      'population': 124916,
      'areaSize': 1251.21,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16067',
      'countyName': 'Gotha, Kreis',
      'gdp': 3825664,
      'gdpPerCapita': 28236,
      'unemploymentRate': 5.1,
      'population': 134908,
      'areaSize': 936.08,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16068',
      'countyName': 'Sömmerda, Kreis',
      'gdp': 1763885,
      'gdpPerCapita': 25256,
      'unemploymentRate': 5.5,
      'population': 69427,
      'areaSize': 806.85,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16069',
      'countyName': 'Hildburghausen, Kreis',
      'gdp': 1458162,
      'gdpPerCapita': 22877,
      'unemploymentRate': 3.4,
      'population': 63197,
      'areaSize': 938.42,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16070',
      'countyName': 'Ilm-Kreis',
      'gdp': 3154704,
      'gdpPerCapita': 28999,
      'unemploymentRate': 4.9,
      'population': 106249,
      'areaSize': 805.12,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16071',
      'countyName': 'Weimarer Land, Kreis',
      'gdp': 2015735,
      'gdpPerCapita': 24570,
      'unemploymentRate': 4.0,
      'population': 82156,
      'areaSize': 804.48,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16072',
      'countyName': 'Sonneberg, Kreis',
      'gdp': 1640195,
      'gdpPerCapita': 29144,
      'unemploymentRate': 3.8,
      'population': 57717,
      'areaSize': 460.85,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16073',
      'countyName': 'Saalfeld-Rudolstadt, Kreis',
      'gdp': 2839645,
      'gdpPerCapita': 26573,
      'unemploymentRate': 5.3,
      'population': 103199,
      'areaSize': 1008.79,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16074',
      'countyName': 'Saale-Holzland-Kreis',
      'gdp': 1929064,
      'gdpPerCapita': 23236,
      'unemploymentRate': 4.1,
      'population': 82950,
      'areaSize': 815.24,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16075',
      'countyName': 'Saale-Orla-Kreis',
      'gdp': 2253787,
      'gdpPerCapita': 27761,
      'unemploymentRate': 4.6,
      'population': 80312,
      'areaSize': 1151.3,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16076',
      'countyName': 'Greiz, Kreis',
      'gdp': 2365566,
      'gdpPerCapita': 23963,
      'unemploymentRate': 4.6,
      'population': 97398,
      'areaSize': 845.98,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'},
     {'countyId': '16077',
      'countyName': 'Altenburger Land, Kreis',
      'gdp': 1997382,
      'gdpPerCapita': 22099,
      'unemploymentRate': 7.1,
      'population': 89393,
      'areaSize': 569.39,
      'stateId': '16',
      'state': 'Freistaat Thüringen',
      'region': 'East Germany'}]



The next step is to establish a connection to the database server and to select the database `stepstone-data`.


```python
# connect to database server
client = MongoClient('mongodb://localhost:27017/')

# select database
db = client["stepstone-data"]
```

The last step is to insert the data into the `counties` collection. Beforehand, existing data must be removed in order to avoid duplicates.


```python
# delete old data
db.counties.delete_many({})

# insert new data
db.counties.insert_many(countyDataMongo)
```




    <pymongo.results.InsertManyResult at 0x20cdc37d380>



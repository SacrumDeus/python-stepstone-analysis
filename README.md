# Stepstone analysis in Python

The goal of this project is to analyze the characteristics of Data Science jobs in Germany. To achieve this, data from different sources (e.g. Stepstone, Regionalstatistik, ...) are collected, prepared and analysed.

In the following sections you can see a project overview. Please note, that every process has it own detailed description, which is provided as *HTML file* or *Jupyter Notebook*.

This project is created by 

* Engelbert Ehret (GitHub: [ehrete](https://github.com/Ehrete))
* Adrian Weiss (GitHub: [SacrumDeus](https://github.com/SacrumDeus))

## Project schedule

The following figure shows the structure of the project.

![project schedule](pictures/project-description.png)

### Data extraction

The first step is to select and extract data from our sources. We used two data sources in our project.

The first data sourcce is the side [Stepstone](https://www.stepstone.de), from which we crawl the following 3 data sets:

* Results for a given job title (e.g. Data Scientist)
* Job offers (links from results page)
* Company profiles (links from results page)

The detailed description for this is available under:

* HTML file: [Webscraping](/webscraping.html)
* ipynb file (Jupyter notebook): [Webscraping](/webscraping.ipynb)


The second data source is the site [Regionalstatistik](https://www.regionalstatistik.de/genesis/online/) from which we extract socioeconomic data on german counties. Unfortunatelly, there is no comparable package like *[Wiesbaden for R](https://cran.r-project.org/web/packages/wiesbaden/wiesbaden.pdf)* which extracts the data automatically. Therefore we wrote the package on our own. This helped us to extract the required data efficiently. 

A detailed documentation is available at:

* HTML file: [Regionalstatistik](/regionalstatistik.html)
* ipynb file (Jupyter notebook): [Regionalstatistik](/regionalstatistik.ipynb)

### Data preparation

Data preparation affects only data from stepstone, because these data don't have the same structure. Socioeconomic data, which are provided via our *Wiesbaden* module are already structurized. There is no data preparation requiered.

For example, if we extract data from stepstone, there are several structures for the field `Location` available. 

- The first option is, that the field `Location` only provides a string like `Hamburg`. There are no more information provided which helps us to locate either the company or the job. 
- A further option is, that location is populated by `Longitude/Latitude` and an `address string` (for example: `{ longitude: "8.6255502700806", latitude: "50.07878112793", address: "Lyoner Str. 23, 60528 Frankfurt am Main, Deutschland" }`). This format will not work either, because we need the post code to map data with socioeconomic data. Typically it is used within job offers.
- As third format, there is an object of address data (`street, streetnumber, postcode, city,`) but no GPS data. However, these data are required for data exploration and data analysis.

It don't have to be said, that those data are sometimes malformatted. There are postcodes in Germany, which are not official. Those postcodes are distributed by *Deutsche Post*/*DHL* for companies, which receive many mailings every day. To avoid issues later in data exploration and data analysis we need to get rid of this malformatted data.

All of required data preparation steps to structure the data and prepare data for text mining are handled by *preprocessing*. For further information, see:

* HTML file: [Preprocessing](/preprocessing.html)
* ipynb file (Jupyter notebook): [Preprocessing](/preprocessing.ipynb)

After the data are processed, we start the text-mining process. This process extracts the relevant words from the text fields applicantProfile and jobDescription. A detailed description is available at:

* HTML file: [TextMining](/textMining.html)
* ipynb file (Jupyter notebook): [TextMining](/textMining.ipynb)

### Data exploration

After we prepared all data, we want to explore the data to answer some questions:

- What are the requirements for a Data Scientist (based on job offer)?
- What are the characteristics for a Data Scientist?
- Which companies do offer jobs as Data Scientist?
- Are there geografical discrepancies?
- Is there a correlation between job/company location and socioeconomic data?

To see the answers for this questions, forward with:

* HTML file: [Data Exploration](/data-exploration.html)
* ipynb file (Jupyter notebook): [Data Exploration](/data-exploration.ipynb)

> There may be issues, when viewing this modules on GitHub. Plotly charts cannot be displayed on GitHub. Please download the HTML-File or the Jupyter Notebook to view it locally.

> A further data exploration (small example) is also available as interactive Dash app. Please follow the instructions linked [here](/dash/start_dash.md) or head to `/dash/start_dash.md`.

## Used packages

In this project, several packages were used. These are listed below.

* beautifulsoup4 (4.10.0)
* bs4 (0.0.1)
* dash (2.2.0)
* dash-bootstrap-components (1.0.3)
* geopandas (0.10.2)
* geopy (2.2.0)
* HanTa (0.2.0)
* langdetect
* matplotlib (3.5.1)
* nltk (3.7)
* numpy (1.22.2)
* pandas (1.4.0)
* plotly (5.6.0)
* pymongo (4.0.1)
* wordcloud (1.8.1)

Not included in this list are packages, which are required by these packages.
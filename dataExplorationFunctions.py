import pandas as pd
import geopandas as gp
from wordcloud import WordCloud

def transformLocation(df: pd.DataFrame) -> gp.GeoDataFrame:

    # convert dict to columns (column location)
    location = pd.concat([df, df["location"].apply(pd.Series)], axis=1).drop(columns="location")

    # use only german data
    location = location.loc[location["country"] == 'de']

    # drop lon, lat, offCommunityKey == NaN
    location = location.dropna(subset=["longitude", "latitude", "offCommunityKey"])

    # we need a 5-digit value from 'offCommunityKey'
    location['AGS'] = location["offCommunityKey"].str[:5]

    # convert lon/lat to float
    location = location.astype({'longitude': 'float64', 'latitude': 'float64'})

    # convert lon/lat to GeoDataframe
    gdf = gp.GeoDataFrame(location, crs=4326, geometry=gp.points_from_xy(location.longitude, location.latitude))

    # convert gdf crs to epsg=31467    
    gdf = gdf.to_crs(epsg=31467)

    # return gdf
    return gdf

def expandState(gdf: gp.GeoDataFrame) -> gp.GeoDataFrame:

    # we need to create further colums: federal state (Berlin, Sachsen, ...), region (east/west)
    federalStates = { "01": "Schleswig-Holstein",
                      "02": "Freie und Hansestadt Hamburg",
                      "03": "Niedersachsen",
                      "04": "Freie Hansestadt Bremen",
                      "05": "Nordrhein-Westfalen",
                      "06": "Hessen",
                      "07": "Rheinland-Pfalz",
                      "08": "Baden-Württemberg",
                      "09": "Freistaat Bayern",
                      "10": "Saarland",
                      "11": "Berlin",
                      "12": "Brandenburg",
                      "13": "Mecklenburg-Vorpommern",
                      "14": "Freistaat Sachsen",
                      "15": "Sachsen-Anhalt",
                      "16": "Freistaat Thüringen" }

    federalRegion = { "01": "West Germany",
                      "02": "West Germany",
                      "03": "West Germany",
                      "04": "West Germany",
                      "05": "West Germany",
                      "06": "West Germany",
                      "07": "West Germany",
                      "08": "West Germany",
                      "09": "West Germany",
                      "10": "West Germany",
                      "11": "East Germany", 
                      "12": "East Germany",
                      "13": "East Germany",
                      "14": "East Germany",
                      "15": "East Germany",
                      "16": "East Germany" }

    # map data
    gdf["federalState"] = gdf["SN_L"].map(federalStates)
    gdf["region"] = gdf["SN_L"].map(federalRegion)

    # return dataframe
    return gdf

def createWordCloud(df, column):
    '''This function creates and returns a word cloud object for a column with tokens or token combinations.'''

    # store tokens in a token list
    tokenList = list()

    for cell in df[column]:

        # replace ' ' with '_' in token combinations
        for i in range(len(cell)):
            cell[i] = cell[i].replace(" ","_")
            
        tokenList.extend(cell)
        

    # convert tokens to a token string 
    tokenString = ' '.join(tokenList)


    # generate wordcloud object
    wordcloudObject = WordCloud(
                        width=800, #500
                        height=800, #500
                        random_state=2, 
                        max_font_size=100,
                        background_color = "white",
                        stopwords = [], # stopword removal already done in preprocessing
                        normalize_plurals = False, # see text mining
                        collocations=False
                        ).generate(tokenString)

    # return wordloud object
    return wordcloudObject
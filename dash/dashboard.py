


# =============================
# A) PREPARATORY ACTIVITIES
# =============================



# Loading modules
# =============================

import pandas as pd
from pymongo import MongoClient
import json

import plotly.express as px
from dash import Dash, dash_table, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# module contains custom wordcloud function
import customWordcloud as cw


# Establish database connection
# =============================

# load db Connection data
with open('dash\dbConnection.json') as f:
    dbCon = json.load(f)


# establish connection
client = MongoClient(dbCon['uri'])
db = client[dbCon['database']]



# Loading data from Mongo DB
# =============================

# get sector data
sectorDf = pd.DataFrame(list(db.sectors.find({},{"_id":0})))

# get company data
companyDf = pd.DataFrame(list(db.pCompany.find({},{"_id":0})))

# get job data
jobDf = pd.DataFrame(list(db.pJobs.find({},{"_id":0})))

# get job tokens
jobTokens = pd.DataFrame(list(db.tmJobs.find({},{"_id":0})))

# get county data
countyData = pd.DataFrame(list(db.counties.find({},{"_id":0})))




# Add county id to Job df
# =============================

jobDf['countyId'] = jobDf['location'].apply(lambda x: x["offCommunityKey"][:5] if x["offCommunityKey"] is not None else None)




# Create Data Frame for Job List
# =============================

'''In this section the data for the job list on the bottom of the dashboard is prepared.'''

jobList = jobDf.copy()

jobList = pd.merge(jobList, companyDf[['companyId','workers','turnover']], on='companyId', how='left') 

# process workers (format from - to)
jobList["workers"] = jobList["workers"].apply(lambda x: '{}-{}'.format(x[0], x[1]) if isinstance(x,list) else None)
   
# extract city from location object
jobList['city'] = jobList['location'].apply(lambda x: x['city'])

# keep only relevant columns
jobList = jobList[['countyId','jobId','company','title','city','workers', 'turnover']]





# =============================
# B) CREATE DASH APP
# =============================



#  Instantiate Dash Object 
# =============================

app = Dash(__name__)




# Create Map Plot
# =============================

'''The plotly map in the left column of the dashboard is created in this section.'''


# create data frame with jobId and countyId

jobCountyList = []

for index, row in jobDf.iterrows():
    
    if row["location"]["country"] == 'de' and row["location"]["offCommunityKey"] is not None:
        
        job = []
        
        # job Id
        job.append(row["jobId"])
        
        # append county id (first 5 digits)
        job.append(row["location"]["offCommunityKey"][:5])
        
        # append to job list
        jobCountyList.append(job)
  
countyAnalysis = pd.DataFrame(data = jobCountyList, columns=["jobId","countyId"])


# calculate number of jobs per county 
countyAnalysis = countyAnalysis.groupby("countyId", as_index=False).count().rename(columns={"jobId": "numberOfJobs"})

# join county data (get countynames)
countyAnalysis = pd.merge(countyAnalysis, countyData, how="right")

# replace missing values with 0
countyAnalysis = countyAnalysis.fillna(value={"numberOfJobs": 0})


# read geojson file
with open('dash\georef-germany-kreis.geojson') as f:
    geodata = json.load(f)

    
# create plotly map
figMap = px.choropleth_mapbox(countyAnalysis, 
                           geojson=geodata, 
                           locations='countyId',
                           color='numberOfJobs',
                           featureidkey="properties.krs_code",
                           color_continuous_scale=["#ffffff", "#0c2577"],
                           mapbox_style="white-bg",
                           zoom=4.6, 
                           center = {"lat": 51.1657, "lon": 10.4515},
                           hover_name='countyName',
                           hover_data={'numberOfJobs':True,
                                        'countyId':False},
                           labels={'numberOfJobs':'Data Science Jobs'})
figMap.update_layout(coloraxis_showscale=True)
figMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})




# Create App Structure
# =============================

'''The layout of the dashboard is created in this section.'''

app.layout = html.Div([

    # header row
    dbc.Row(
        dbc.Col(
            html.H1(
                html.B("Data Science Jobs in Germany")
            ), 
            style={'textAlign': 'center'}
        )
    ),

    # middle row
    dbc.Row([

        # germany map
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div(html.H3("County Selection")),
                    html.Div([html.P("Please select a county for which the information should be displayed."),
                    dcc.Graph(id="germanyMap", figure=figMap)])
                ]),
                style={"height": "100%"}
            ),
            width=12,md=12, lg=4,
            style={"padding": "10px"}
        ),

        # detailed graphs
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        html.H3("Detailed Information", id="detailGraphHeader"),
                        style={"width": "100%"}
                    ),
                    dbc.Row([

                        # graph 1
                        dbc.Col(
                            html.Div([
                                html.Label("Choose Variable for Graph 1"),
                                dcc.Dropdown(['sectors','benefits','tasks tokens','applicant profile tokens'], 'sectors', id="variableGraph1"),
                                html.Div(id="detailGraph1")]
                            ), 
                            width=12,md=6,lg=6
                        ),

                        # graph 2
                        dbc.Col(
                            html.Div([
                                html.Label("Choose Variable for Graph 2"),
                                dcc.Dropdown(['sectors','benefits','tasks tokens','applicant profile tokens'], 'benefits', id="variableGraph2"),
                                html.Div(id="detailGraph2")]
                            ), 
                            width=12,md=6,lg=6
                        )
                    ])
                ]),
                style={"height": "100%"}
            )],
            width=12, md=12, lg=8,
            style={"padding": "10px"}
        )]
    ),

    # job list row (bottom)
    dbc.Row(
        dbc.Card(
            dbc.CardBody([
                html.H3("Job List", id="jobListHeader"),
                html.Div(id="jobList")
            ]),
            style={"margin":"10px"}
        )
    )
],
style={"padding": "10px"})


# =========================================
# C) CALLBACKS
# =========================================

'''The callbacks update the dashboard if the user makes selections.'''




# Callback 1 and 2:  Update graphs in detailed information box on the middle right in the dashboard
# =========================================


# Helper function used in both callbacks
#----------------------------------------

def createDetailGraph(clickData, variable):
    '''This function creates detailed charts based on the selected county and the selected variable'''

    # extract countyId from clickData
    countyId = clickData["points"][0]["location"]


    # SECTORS - BAR CHART
    if variable == 'sectors':

         # data prepataion
        sectorAnalysis = companyDf.explode("sectors")[["companyId","sectors"]].rename(columns={"sectors":"sectorId"})
        sectorAnalysis = pd.merge(sectorAnalysis, sectorDf, how="inner").rename(columns={"name":"sectorName"})
        sectorAnalysis = pd.merge(sectorAnalysis, jobDf, how="inner")
        sectorAnalysis = sectorAnalysis[sectorAnalysis["countyId"]==countyId]
        sectorAnalysis = sectorAnalysis.groupby("sectorName")["jobId"].count().rename("numberOfJobs")
        sectorAnalysis = sectorAnalysis.sort_values(ascending=False).head(10)

        # create message if no sector data is available for the county
        if sectorAnalysis.count() == 0:
            returnObject = html.P("No sector data available for this county.")

        # create graph object if sector data is available for the county
        else:
            fig = px.bar(sectorAnalysis.sort_values(),x="numberOfJobs",text="numberOfJobs",template="simple_white",
                        title="Top 10 sectors", orientation="h")
            fig.update_traces(marker_color="#0c2577", hoverinfo="skip", hovertemplate=None)
            fig.update_yaxes(title=None)
            fig.update_xaxes(title=None, tickangle = 0)
            fig.update_layout(barmode='stack',margin={"r":0,"l":0,"b":0})
            returnObject = dcc.Graph(figure=fig)

    
    # BENEFITS - BAR CHART
    if variable == 'benefits':

        # data prepataion
        benefitAnalysis = jobDf[jobDf["countyId"]==countyId]
        benefitAnalysis = (benefitAnalysis
                            .explode("benefits")
                            .groupby("benefits", as_index=False)["jobId"]
                            .count().rename(columns={"jobId":"absolute"})
                            .sort_values(by="absolute", ascending=False)
                            .head(10))


        # create message if no benefit data is available for the county
        if benefitAnalysis.count()['benefits'] == 0:
            returnObject = html.P("No benefit data available for this county.")

        # create graph object if benefit data is available for the county
        else:
            fig = px.bar(benefitAnalysis.sort_values(by="absolute"),y="benefits", x="absolute",text="absolute",template="simple_white",
                        title="Top 10 benefits", orientation="h")
            fig.update_traces(marker_color="#0c2577", hoverinfo="skip", hovertemplate=None)
            fig.update_yaxes(title=None)
            fig.update_xaxes(title=None, tickangle = 0)
            fig.update_layout(barmode='stack', margin={"r":0,"l":0,"b":0})
            returnObject = dcc.Graph(figure=fig)



    # TASKS OR APPLICANT PROFILE - WORD CLOUD
    if variable == 'tasks tokens' or variable == 'applicant profile tokens': 

        try:
            # create dataframe
            tokens = jobDf[jobDf["countyId"]==countyId]
            tokens = tokens[["jobId","countyId"]]
            tokens = pd.merge(tokens, jobTokens, how="inner")

            # determine data frame column with tokens
            tokenColumn = ('tasks' if variable == 'tasks tokens' else 'applicantProfile')

            # create word cloud image
            image = cw.createWordCloud(tokens,tokenColumn)

            # create graph object
            fig = px.imshow(image)
            fig.update_xaxes(showticklabels=False) # remove axis
            fig.update_yaxes(showticklabels=False)
            fig.update_layout(margin={"r":0,"t":10,"l":0,"b":0})
            returnObject = dcc.Graph(figure=fig)

        except:
            returnObject = html.P("No tokens are available.") 
 
    # return final object
    return returnObject
    
  


# Callback 1 - Graph 1
#---------------------------

@app.callback(Output('detailGraph1','children'),
              Input('germanyMap', 'clickData'),
              Input('variableGraph1', 'value'))

def getHoverData(clickData, variable):

    # create graph if an county is selected
    if clickData:
        return createDetailGraph(clickData, variable)
    
    # return message if no county is selected
    else:
        return html.P("Please select a county to display the detail Graph 1.")



# Callback 2 - Graph 2
#---------------------------

@app.callback(Output('detailGraph2','children'),
              Input('germanyMap', 'clickData'),
              Input('variableGraph2', 'value'))

def getHoverData(clickData, variable):

    # create graph if an county is selected
    if clickData:
        return createDetailGraph(clickData, variable)
    
    # return message if no county is selected
    else:
        return html.P("Please select a county to display the detail Graph 2.")





# Callback 3:  Update Job List in the bottom of the dashboard
# =========================================

@app.callback(Output('jobList','children'),
              Input('germanyMap', 'clickData'))

def printTable(clickData):

    # create table if an county is selected
    if clickData:

        # extract countyId from clickData
        countyId = clickData["points"][0]["location"]
 
        # filter jobList data frame
        dff = jobList[jobList["countyId"]==countyId]
    

        # create dash data table object
        detailTable = dash_table.DataTable(
                            data = dff.to_dict('records'), 
                            columns = [{"name": i, "id": i} for i in dff.columns],
                            page_size=5,
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                                'whiteSpace': 'normal'},
                            # hide id columns
                            style_data_conditional=[
                                {'if': {'column_id': ['countyId','jobId'],},
                                    'display': 'None',}],
                            style_header_conditional=[
                                {'if': {'column_id': ['countyId','jobId'],},
                                    'display': 'None',}],)
        
        return detailTable

    # return message if no county is selected
    else:
        return html.P("Please select a county to display the job List")





# Callback 4:  Update Subtitle
# =========================================


# Helper function
#---------------------------
def getCountyName(countyId):
    '''The function returns the countyName of a countyId'''
    return(countyData[countyData["countyId"]==countyId]['countyName'].values[0])



# Callback
#---------------------------
@app.callback(Output('jobListHeader','children'),
              Output('detailGraphHeader','children'),
              Input('germanyMap', 'clickData'))

def updateHeaders(clickData):

    # get county name if a county is selected
    if clickData is not None:
        countyId = clickData["points"][0]["location"]
        countyName = ' - '+getCountyName(countyId)
    else:
        countyName = ''


    # return titles
    titleJobList = 'Job List'+countyName
    titleDetailedInformation = 'Detailed Information'+countyName
    return(titleJobList, titleDetailedInformation)




# =========================================
# D) START DASH APP
# =========================================

if __name__ == '__main__':    
    app.run_server(debug=False)
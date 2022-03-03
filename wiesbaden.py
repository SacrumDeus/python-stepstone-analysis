
import requests;
import pandas as pd;
import csv;


class Genesis:
    
    # dictionary with all sites that uses the genesis system
    databases = {
       "REGIO":"https://www.regionalstatistik.de/genesisws/"
       ,"DESTATIS":"https://www-genesis.destatis.de/genesisWS/"
    }
    
    
    def __init__(self, database, username, password):

        # assign variales
        self.__auth = "username={0}&password={1}".format(username, password)
        self.database = database
        
        # check if database exists
        if database not in Genesis.databases:
            raise ValueError("database is not availables")
  

        # check userdata
        ## specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/helloworld/logincheck?"
        additionalParameters = "&language=de"   
        
        ## generate request uri
        uri = databaseLink + method + self.__auth + additionalParameters
        
        ## query data
        response = requests.get(uri)
        
        ## check result
        if 'Fehler' in response.json()["Status"]:
            raise ValueError("the username and/or password is incorrect")
        

        # set pandas print options (the whole text have to be visible)
        pd.set_option("display.max_colwidth", None)
     
       
        
    def search_datacube(self, term):
        """search_datalist searches cubes with terms"""
        
        # specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/find/find?"
        searchObject = "&term=" + term
        additionalParameters = "&category=cubes&pagelength=2500"
        
        # generate request uri
        uri = databaseLink + method + self.__auth + searchObject + additionalParameters
        
        # query data
        response = requests.get(uri)
        
        # convert to data frame
        df =  pd.DataFrame(response.json()["Cubes"])

        # return data frame
        return df


    
    
    def retrieve_datalist(self, tableseries):
        """retrieve_datalist retrieves a list of available data tables in a series"""
        
        # specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/catalogue/cubes?"
        searchObject = "&selection=" + tableseries
        additionalParameters = "&pagelength=2500"
        
        # generate request uri
        uri = databaseLink + method + self.__auth + searchObject + additionalParameters
        
        # query data
        response = requests.get(uri)
        
        # convert to data frame
        df =  pd.DataFrame(response.json()["List"])
   
        # return data frame
        return df   
    


    
    def retrieve_valuelabel(self, variablename):
        """retrieve_valuelabel retrieves value labels for variable"""
        
        # specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/catalogue/values2variable?"
        searchObject = "&name=" + variablename
        additionalParameters = "&pagelength=25000"
        
        # generate request uri
        uri = databaseLink + method + self.__auth + searchObject + additionalParameters
        
        # query data
        response = requests.get(uri)
        
        # convert to data frame
        df = pd.DataFrame(response.json()["List"])

        # return data frame
        return df      
    
    
    def retrieve_metadata(self, tableseries):     
        """retrieve_metadata retrieves meta data"""
        
        # specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/metadata/cube?"
        searchObject = "&name=" + tableseries
        additionalParameters = "&pagelength=2500"
        
        # generate request uri
        uri = databaseLink + method + self.__auth + searchObject + additionalParameters
        
        # query data
        response = requests.get(uri)
        
        # extract dimension and save result in list objects
        objects = response.json()["Object"]["Structure"]["Axis"]
        
        # extract measures and extend list objects
        objects.extend(response.json()["Object"]["Structure"]["Contents"])   
        
        # convert objects to data frame
        df =  pd.DataFrame(objects)       
        
        # return data frame
        return df      
           
        
    
    def retrieve_data(self, tableseries):
        """retrieve_data retrieves a single data cube"""
        
        # ===============================
        # Part 1 - retrieve column names
        # ===============================
        
        # specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/metadata/cube?"
        searchObject = "&name=" + tableseries
        additionalParameters = "&pagelength=2500"
        
        # generate request uri
        uri = databaseLink + method + self.__auth + searchObject + additionalParameters
        
        # query metadata
        response = requests.get(uri)        
        
        # list with all column names
        columns = []
        
        # list with numeric columns --> for type conversion needed
        numericColumns = []

        # first column = dummy column --> set cube id as name
        columns.append('id'+response.json()["Object"]["Statistic"]["Code"])

        # extract dimension column names and extend column list
        for axis_object in response.json()["Object"]["Structure"]["Axis"]:
            columns.append(axis_object["Code"])
    
        # extract measure names and extend column list
        for conent_object in response.json()["Object"]["Structure"]["Contents"]:
            # the data output contains 4 columns per measure --> column _val is relevant
            for var in ["_val","_qual","_lock","_err"]:
                columns.append(conent_object["Code"]+var)
                if var == "_val":
                    numericColumns.append(conent_object["Code"]+var)                

                    
                    
        # ===============================
        # Part 2 - retrieve data values
        # ===============================      
        
        # specifcy request components
        databaseLink = Genesis.databases[self.database]
        method = "rest/2020/data/cube?"
        searchObject = "&name=" + tableseries
        
        # generate request uri
        uri = databaseLink + method + self.__auth + searchObject
        
        # query metadata
        response = requests.get(uri)          
        
        # convert content in nested lists
        str = response.json()["Object"]["Content"]
        content = list(csv.reader(response.json()["Object"]["Content"].splitlines(),delimiter=';'))
        
        # delete header rows with metadata
        # the last header row contains the word 'QEI'
        firstRowData = 0

        for row in content:
            firstRowData+=1
            if 'QEI' in row:
                break

        del content[:firstRowData]
        
           
        # ===============================
        # Part 3 - generate data frame
        # ===============================  
        
        # convert objects to data frame and return result
        df = pd.DataFrame(content, columns=columns)

        # convert numeric columns to appropriate data type
        for col in numericColumns:
            df[col]=pd.to_numeric(df[col])        
        
        # return result
        return df        
    
# ==================================
# Loading required packages
# ==================================

import pandas as pd


# text mining modules
import nltk
from HanTa import HanoverTagger as ht
import langdetect

# graphic modules
from matplotlib import pyplot as plt

# mathematic functions
import math


# ==================================
# Transformation functions
# ==================================


def detectLanguage(str):
    '''This function detects the language of a string.'''
    try:
        return langdetect.detect(str)
    except:
        return "error"


def normalizeText(df, textColumn):
    '''This function normalizes a text. All digits are converted to lower case.'''
    df[textColumn] = df[textColumn].astype(str).str.lower()



def tokenizeText(df, textColumn):
    '''This function tokenizes a text.'''
    regexp = nltk.tokenize.RegexpTokenizer('\w+')
    df[textColumn] = df[textColumn].apply(regexp.tokenize)



def removeStopwords(df, textColumn, langColumn):
    '''This function removes stopwords.'''

    # load german stopwords
    stopwordsGerman = nltk.corpus.stopwords.words("german")
    
    # normalize german stopwords
    stopwordsGerman = [item.lower() for item in stopwordsGerman]

    # load english stopwords
    stopwordsEnglish = nltk.corpus.stopwords.words("english")
    
    # normalize english stopwords
    topwordsEnglish = [item.lower() for item in stopwordsEnglish]
    
    # editList function --> returns list without stopwords
    def editList(tokens, language):
        
        # action depends on the language
        if language == "en":
            return [item for item in tokens if item not in stopwordsEnglish]
        else:
            return [item for item in tokens if item not in stopwordsGerman]
        
    # modify text column
    df[textColumn] = [editList(df.iloc[idx][textColumn], df.iloc[idx][langColumn]) for idx in list(range(len(df)))]




def TagLem(df, textColumn, langColumn):
    '''This function performs an pos tagging and lemmatization. All tokens except nouns are removed.'''

    # german tagger
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    
    # english lemmatizer
    lemmatizer = nltk.stem.WordNetLemmatizer() 
    
    # editList function --> returns list without stopwords
    def editList(tokens, language):
        # action depends on the language
        if language == "en":
            # process english tokens
            taggedTokens = nltk.pos_tag(tokens)
            # only nouns and the token r (programming language) remain in the data frame
            taggedTokens = [word for word in taggedTokens if (word[1] in ('NN','NNP','NNS', 'NNPS') or word[0]=='r')]
            return [lemmatizer.lemmatize(item[0], 'n') for item in taggedTokens]
        else:
            # process german tokens
            taggedTokens = tagger.tag_sent(tokens)
            # only nouns and the token r (programming language) remain in the data frame
            return [word[1].lower() for word in taggedTokens if (word[2] in ('FM','NN','NE') or word[0]=='r')]
        
    # modify text column
    df[textColumn] = [editList(df.iloc[idx][textColumn], df.iloc[idx][langColumn]) for idx in list(range(len(df)))]




def createTokenCombinations(df, column):
    '''This function creates token combination (bigrams). The token combinations are stored in a separate column with the suffix Comb.'''
    df[column+"Comb"] = df[column].apply(lambda x: [' '.join(item) for item in nltk.bigrams(x)])



def removeDuplicates(df,column):
    '''This function ensures that each token occurs only once in each document (removing duplicates).'''
    df[column] = df[column].apply(lambda x: list(set(x)))



def removeInfrequentObjects(df,column,minOccurence):
    '''This function removes tokens with an occurence less than a minimum treshold.'''
    
    # list of all token (combinations)
    tokenList = []

    for item in df[column]:
        tokenList.extend(list(set(item))) # only distinct tokens with set()

    # calculate token occurence
    fd = nltk.probability.FreqDist(tokenList)

    # frequentTokens
    frequentTokens = [token[0] for token in fd.most_common() if token[1] >= minOccurence]

    # keep only remaining tokens
    df[column] = df[column].apply(lambda x: [item for item in x if item in frequentTokens])



def removeCustomStopwords(df, textColumn, stopwordList):
    '''This function removes custom stopwords provided by a stopword list.'''
      
    # modify text column
    df[textColumn] = df[textColumn].apply(lambda x: [item for item in x if item not in stopwordList])



# ==================================
# Result Functions
# ==================================

# This block contains functions that return descriptive statistics about token (combinations).


def countDistinctObjects(df,column):
    '''This function returns the number distinct tokens in a column of a data frame.'''
    
    # store all objects in a list
    objectList = []

    for item in df[column]:
        objectList.extend(item)

    # distinct objects (using python datatype set())
    distinctObjectList = list(set(objectList))

    # return length of list
    return(len(distinctObjectList))


def getFrequencyDistributionPlots(df,columnlist,limitAxisX):
    '''This function returns the cumulative distribution of a token (combination).'''

    # shape of the combined plots
    numberOfColumns = 2
    numberOfRows = math.ceil(len(columnlist) / numberOfColumns)
       
    # size of the combined plots
    plt.figure(figsize=(18,numberOfRows*6))


    # calculate distribution an generate subplot
    for count, column in enumerate(columnlist):

        plotNumber = count + 1

        # calculate frequency of distinct objects
        objectList = []
        for item in df[column]:
            distinctObjects = list(set(item)) # only distinct tokens with set()
            objectList.extend(distinctObjects)

        fd = nltk.probability.FreqDist(objectList)

        # convert into data frame
        freqObject = pd.DataFrame(fd.most_common(), columns=['object', 'nrOfDocuments'])

        # aggregate 
        freqDat = freqObject.groupby("nrOfDocuments", as_index=False).count()

        # accumulate     
        freqDat["cum"] = freqDat["object"].cumsum()

        # number of objects
        numberOfObjects = freqDat["object"].sum().item()

        # accumlate percentage
        freqDat["cumPerc"] = round(freqDat["cum"] / numberOfObjects * 100, 2)

        # delete columns
        delColumnNames = ['object', 'cum']
        freqDat.drop(delColumnNames, inplace=True, axis=1)
        
        # calculate number of ducments at 80 percent quantile
        tmpMax = freqDat[freqDat["cumPerc"] <= 80]["cumPerc"].max()
        nrDoc80 = freqDat[freqDat["cumPerc"]==tmpMax]["nrOfDocuments"].values[0]

        # generate subplot
        plt.subplot(numberOfRows,numberOfColumns,plotNumber)
        plt.plot(freqDat["nrOfDocuments"],freqDat["cumPerc"], lw=4)
        plt.title(column)
        plt.xlabel("number of documents")
        plt.ylabel("cumulative percentage")
        plt.plot([0,max(freqDat["nrOfDocuments"])],[80,80],label="Mean Value", color="r", lw=3, ls=":")
        plt.plot([nrDoc80,nrDoc80],[0,80],label="Mean Value", color="r", lw=3, ls=":")
        plt.text(nrDoc80-0.5,85,"{}".format(nrDoc80))
        plt.xlim(left = 0, right = limitAxisX)     # limit x axis
        plt.grid(True)



def getObjectFrequency(df,column):
    '''This function returns a list with the remaining token (combinations) in a column and their frequency.'''
    tokenList = []

    for item in df[column]:
        tokenList.extend(item)

    fd = nltk.probability.FreqDist(tokenList)
    
    return fd.most_common()
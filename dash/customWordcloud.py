from wordcloud import WordCloud


def createWordCloud(df, column):
    
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

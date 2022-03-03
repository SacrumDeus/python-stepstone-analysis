import json
import urllib.parse
import requests
import re as regex
from bs4 import BeautifulSoup
from time import sleep

def initJobSearch(jobTitle):

    # general variable definition
    itemsPerPage = 25  # this is defined by stepstone itself
    jobList = []
    offset = 25
    url = "https://www.stepstone.de/5/ergebnisliste.html?what={0}"

    # we need to encode jobTitle (space -> %20, ...)
    jobTitleEncoded = urllib.parse.quote(jobTitle)

    # lets get the first page
    soup = getRequestData(url.format(jobTitleEncoded))

    # get number of results
    numberOfResults = getNumberOfResults(soup)

    # set a message
    print("[INFO] there are "+str(numberOfResults)+" results for job: "+jobTitle)

    # get result data (link, description, etc.) (appending)
    # first page
    jobList.extend(getResultData(soup))

    # to retrieve to other data, we iterate above entries until end
    # second page + more
    while offset < numberOfResults:

        # create new link structure
        url = "https://www.stepstone.de/5/ergebnisliste.html?what={0}&of={1}"

        # get data
        soup = getRequestData(url.format(jobTitleEncoded, offset))

        # parse data
        jobList.extend(getResultData(soup))

        # increase offset (by 25)
        offset += itemsPerPage

    # return jobList (type of list)
    return jobList

def getRequestData(uri):

    # create header (because script is not running in browser)
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

    # get data for request
    r = requests.get(uri, timeout=30, headers=header)
    

     # we need to wait 0.5 sec (to prevent spam ban)
    sleep(0.5)

    # return data as soup
    return BeautifulSoup(r.text, "html.parser")


def getNumberOfResults(soup: BeautifulSoup):

    # retrieve string for number of results
    count = soup.find(attrs={"class": "at-facet-header-total-results"}).text

    # convert it to integer
    count = int(count.replace(".", ""))

    # return number of results
    return count


def getResultData(soup: BeautifulSoup):

    # variables
    jobs = []

    # identifiers where to find data
    cssResultList = regex.compile("ResultsSectionContainer.*")

    # get results list
    resultList = soup.find(attrs={"class": cssResultList})

    # extract any link
    for item in resultList.findAll('article'):

        # dictionary to hold the data
        job = dict.fromkeys(["id", "title", "jobLink", "company", "companyLink"])

        # extract job title
        job["id"] = item["id"].replace("job-item-", "")
        job["title"] = item.find(attrs={"data-at": "job-item-title"}).text
        job["jobLink"] = "https://www.stepstone.de"+item.find(attrs={"data-at": "job-item-title"})["href"]
        job["company"] = item.find(attrs={"data-at": "job-item-company-name"}).text
        job["companyLink"] = item.find(attrs={"data-at": "company-logo"})["href"]

        # append data to list
        jobs.append(job)
    
    # return jobs (list)
    return jobs

def getCompanyData(companyDict): 
    
    # variables
    company = dict.fromkeys(["company", "linkJobs", "linkProfile", "id", "sectors", "workers", "homepage", "about"])
    company["location"] = {}
    company["rating"] = {}
    company["json"] = {}

    # set data data
    company["company"] = companyDict["company"]
    company["linkJobs"] = companyDict["companyLink"]

    # first get request
    soup = getRequestData(companyDict["companyLink"])

    # some companies dont have a menu
    if soup.find(id="header-menu"):

        # validate company profile
        try:
            if soup.find(id="header-menu").find(attrs={"class": "tab-thisCompany" }):
                company["linkProfile"] = "https://www.stepstone.de"+soup.find(id="header-menu").find(attrs={"class":"tab-thisCompany"}).findChild()["href"]

        except:
            company["linkProfile"] = None

    # handle link profile
    if company["linkProfile"] != None:

        # get profile soup
        soupProfile = getRequestData(company["linkProfile"])

        # get company id
        company["id"] = soupProfile.find(attrs={"data-block": "app-headerV2"})["data-companyid"]       

        # extract data areas (attribute data-initialdata)
        companyHeader = (soupProfile.find(attrs={"data-block": "app-headerV2"})["data-initialdata"] if soupProfile.find(attrs={"data-block": "app-headerV2"}) else None)
        companyRating = (soupProfile.find(attrs={"data-block": "app-reviews"})["data-initialdata"] if soupProfile.find(attrs={"data-block": "app-reviews"}) else None)
        companyFacts = (soupProfile.find(attrs={"data-block": "app-inShort"})["data-initialdata"] if soupProfile.find(attrs={"data-block": "app-inShort"}) else None)
        companyAbout = (soupProfile.find(attrs={"data-block": "app-aboutUs"}) if soupProfile.find(attrs={"data-block": "app-aboutUs"}) else None)

        if companyHeader:

            # extracted data are type of json -> parse
            companyHeaderJson = json.loads(companyHeader)

            # extract data from header
            company["sectors"] = (companyHeaderJson['sectors'] if companyHeaderJson['sectors'] else None)
            company["workers"] = (companyHeaderJson['metaData']['people'] if companyHeaderJson['metaData']['people'] else None)
            company["homepage"] = (companyHeaderJson['metaData']['page'] if companyHeaderJson['metaData']['page'] else None)

            # save json data to distinct element
            company["json"]["Header"] = companyHeaderJson

        if companyRating:

            # extracted data are type of json -> parse
            companyRatingJson = json.loads(companyRating)

            # extract ratings
            company["rating"]["overall"] = (companyRatingJson['ratingSummary']['surveysCount'] if companyRatingJson['ratingSummary']['surveysCount']  else None)
            company["rating"]["avgRating"] = (companyRatingJson['ratingSummary']['overallRatingAvg'] if companyRatingJson['ratingSummary']['overallRatingAvg']  else None)
            company["rating"]["participation"] = (companyRatingJson["overallRatingRepartitionByRating"] if companyRatingJson["overallRatingRepartitionByRating"] else None)
            company["rating"]["subrating"] = (companyRatingJson["subRatings"] if companyRatingJson["subRatings"] else None)

            # save json data to distinct element
            company["json"]["Rating"] = companyRatingJson

        if companyFacts:
            
            # extracted data are type of json -> parse
            companyFactsJson = json.loads(companyFacts)

            # extract facts (may overwrite some fields)
            company["location"]["street"] = (companyFactsJson['street'] if companyFactsJson['street'] else None)
            company["location"]["streetNumber"] = (companyFactsJson['streetNumber'] if companyFactsJson['streetNumber'] else None)
            company["location"]["postalCode"] = (companyFactsJson['postalCode'] if companyFactsJson['postalCode'] else None)
            company["location"]["city"] = (companyFactsJson['city'] if companyFactsJson['city'] else None)
            company["location"]["country"] = (companyFactsJson['country'] if companyFactsJson['country'] else None)
            company["turnover"] = (companyFactsJson['turnover'] if companyFactsJson['turnover'] else None)

            # save json data to distinct element
            company["json"]["Facts"] = companyFactsJson

        if companyAbout:

            # extract about us (as string with linebreaks)
            company["about"] = "\r\n".join([p.text for p in companyAbout.findAll("p")])

    else:

        # get company id
        company["id"] = soup.find(attrs={"data-block": "app-header"})["data-companyid"]

        # extract data (attribute data-initialdata)
        companyHeader = soup.find(attrs={"data-block": "app-header"})["data-initialdata"]

        if companyHeader:

            # extracted data are type of json -> parse
            companyHeaderJson = json.loads(companyHeader)

            # extract data from header
            company["sectors"] = (companyHeaderJson['sectors'] if companyHeaderJson['sectors'] else None)
            company["workers"] = (companyHeaderJson['metaData']['people'] if companyHeaderJson['metaData']['people'] else None)
            company["homepage"] = (companyHeaderJson['metaData']['page'] if companyHeaderJson['metaData']['page'] else None)
            company["location"] = (companyHeaderJson['metaData']['location'] if companyHeaderJson['metaData']['location'] else None)

            # save json data to distinct element
            company["json"]["Header"] = companyHeaderJson   

    # return company dictionary
    return company
    
def getJobData(jobLink, jobId): 

    # variables
    job = dict.fromkeys(["id", "link", "company", "jobTitle", "location", "contractType", "workType", "introduction", "tasks", "applicantProfile", "companyOffer", "benefits"])
    job["store"] = {}

    # define extractable tag types
    tagTypes = ["p", "li"]

    # set id + link
    job["id"] = jobId
    job["link"] = jobLink

    # get request
    soup = getRequestData(jobLink)
    
    # extract data areas from soup
    jobHeader = soup.find("div", attrs={"class":"js-listing-header"})
    jobIntroduction = soup.find("div", attrs={"class":"at-section-text-introduction-content"})
    jobTaskDescription = soup.find("div", attrs={"class": "at-section-text-description-content"})
    jobYourProfile = soup.find("div", attrs={"class": "at-section-text-profile-content"})
    jobCompanyOffer = soup.find("div", attrs={"class": "at-section-text-weoffer-content"})
    jobLocation = (regex.split("\s\=\s(?=\{.*)", soup.find(id="js-section-preloaded-LocationWithCommuteTimeBlock").string)[1] if soup.find(id="js-section-preloaded-LocationWithCommuteTimeBlock") else None)
    jobBenefits = (soup.find("div", attrs={"data-block": "app-benefitsForListing"})["data-initialdata"] if soup.find("div", attrs={"data-block": "app-benefitsForListing"}) else None)

    # extract header data
    if jobHeader:

        # extracted data are type of soup
        job["company"] = (jobHeader.find(attrs={"class": "at-header-company-name"}).text if jobHeader.find(attrs={"class": "at-header-company-name"}) else None)
        job["jobTitle"] = (jobHeader.find(attrs={"class": "at-header-company-jobTitle"}).text if jobHeader.find(attrs={"class": "at-header-company-jobTitle"}) else None)
        job["location"] = (jobHeader.find(attrs={"class": "at-listing__list-icons_location"}).text if jobHeader.find(attrs={"class": "at-listing__list-icons_location"}) else None)
        job["contractType"] = (jobHeader.find(attrs={"class": "at-listing__list-icons_contract-type"}).text if jobHeader.find(attrs={"class": "at-listing__list-icons_contract-type"}) else None)
        job["workType"] = (jobHeader.find(attrs={"class": "at-listing__list-icons_work-type"}).text if jobHeader.find(attrs={"class": "at-listing__list-icons_work-type"}) else None)

        # store data
        job["store"]["header"] = str(jobHeader)

    # extract job introduction
    if jobIntroduction:

        # extracted data are type of soup
        job["introduction"] = ("\r\n".join([tag.text for tag in jobIntroduction.findAll(tagTypes)]) if jobIntroduction.findAll(tagTypes) else None)

        # store data
        job["store"]["introduction"] = str(jobIntroduction)

    # extract job tasks
    if jobTaskDescription:

        # extracted data are type of soup
        job["tasks"] = ("\r\n".join([tag.text for tag in jobTaskDescription.findAll(tagTypes)]) if jobTaskDescription.findAll(tagTypes) else None)

        # store data
        job["store"]["tasks"] = str(jobTaskDescription)

    # extract applicant profile
    if jobYourProfile:

        # extracted data are type of soup
        job["applicantProfile"] = ("\r\n".join([tag.text for tag in jobYourProfile.findAll(tagTypes)]) if jobYourProfile.findAll(tagTypes) else None)

        # store data
        job["store"]["applicantProfile"] = str(jobYourProfile)

    # extract job offering
    if jobCompanyOffer:

        # extracted data are type of soup
        job["companyOffer"] = ("\r\n".join([tag.text for tag in jobCompanyOffer.findAll(tagTypes)]) if jobCompanyOffer.findAll(tagTypes) else None)

        # store data
        job["store"]["companyOffer"] = str(jobCompanyOffer)

    # extract job location
    if jobLocation:

        # we are going to overwrite location in job dict
        location = {}

        # init json
        jsonLoc = json.loads(jobLocation.replace(";", ""))

        # extracted are type of json
        location["longitude"] = (jsonLoc['longitude'] if jsonLoc['longitude'] else None)
        location["latitude"] = (jsonLoc['latitude'] if jsonLoc['latitude'] else None)
        location["address"] = (jsonLoc['addressText'] if jsonLoc['addressText'] else None)

        job["location"] = location

        # store data
        job["store"]["location"] = jobLocation

    # extract job benefits
    if jobBenefits:

        # init json
        jsonBenefits = json.loads(jobBenefits)

        # extracted data are type of json
        job["benefits"] = ([benefit['benefitName'] for benefit in jsonBenefits] if jsonBenefits else None)
        
        # store data
        job["store"]["benefits"] = jobBenefits

    # return job dictionary
    return job
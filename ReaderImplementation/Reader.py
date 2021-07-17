#!/usr/bin/env python
from bs4 import BeautifulSoup
import json
import importlib
from ReaderInterfaces.IReader import IReader
from ReaderImplementation.Constants.LinkedInReaderConstants import *
import pandas as pd

class DOMNotFoundException(Exception):
    """
    Temporary exception: When the DOM element is not found
    """
    pass

class TagException(Exception):
    """
    Exception for raising if the tags are not defined in the constants
    """
    pass

class Reader(IReader):
    """
    An attempt to generalize Job post retrieving, according to the user requests.
    By default, we are using LinkedIn as a Job Scraping website.
    To decide from which website to scrape, you need to declare constants, as the
    reader is totally dependent on the constants. If classes are not known or they are empty,
    you can put them as None.+
    For reference, you can see ./Constants/LinkedInReaderConstants.py
    """
    def __init__(self, Platform=None):
        # Dynamic module loading:
        # This is where constants defined are loaded and helpful for searching the 
        # required data from the pages
        if Platform is not None:
            self.Constants = importlib.import_module('ReaderImplementation.Constants.{}ReaderConstants'.format(Platform))
        else:
            self.Constants = importlib.import_module('ReaderImplementation.Constants.LinkedInReaderConstants')

        self.ToDisplay = set(['CompanyName', 'JobTitle', 'JobLocation', 'TimePosted'])

        self.DomainName = self.Constants.DOMAIN_NAME
        self.SearchURL = self.Constants.JOB_SEARCH_URL
        self.QueryParams = {
                            'SearchQuery':     self.Constants.JOB_SEARCH_QUERY, 
                            "JobLocation":     self.Constants.JOB_SEARCH_LOCATION,
                            "ExperienceLevel": self.Constants.JOB_SEARCH_EXP, 
                            "DatePosted":      self.Constants.JOB_SEARCH_TIME_POSTED, 
                            "NumberOfPages":   self.Constants.JOB_SEARCH_PAGE_KEY
                            }
        self.QueryKeyLen = len(self.QueryParams)
        self.PageMultiplier = self.Constants.JOB_SEARCH_PAGE_MULTIPLIER

    def ConstructQueryURL(self, KeywordParams, PageNumber):
        """
        Construct the query based on reader and keyword parameters
        :param KeywordParams parameter for constructing the QueryURL.
        :param PageNumber current page (starting from 0, to be modified)
        :returns QueryURL a string
        """
        if not(isinstance(self.SearchURL, str)):
            raise ValueError('Search URL is not defined for constructing search URL')

        QueryURL = self.SearchURL + '?'
        for QueryKey, QueryValue in KeywordParams.items():
            if QueryKey not in self.QueryParams:
                print('Key {} not found in list of keys'.format(QueryKey))
            elif self.QueryParams[QueryKey] is not None:
                if QueryKey == 'NumberOfPages':
                    QueryValue = PageNumber*self.PageMultiplier

                QueryURL += '{}={}'.format(self.QueryParams[QueryKey], QueryValue)
                QueryURL += '&'
        return QueryURL

    def GetLinkOfJobPostFromJobPostDOM(self, JobPostDOM):
        """
        Return Link from the job post given the DOM element that contains 
        the link, else None
        """
        # Sometimes the link is the main Job post DOM element,
        # to check whether that is the case as per the constants defined.
        LinkDOM = None
        if JobPostDOM is not None:
            ClassName = JobPostDOM['class'] if JobPostDOM.has_attr('class') else None
            if ClassName is not None and self.Constants.RESULT_LINK_CLASS is not None:
                if JobPostDOM.name == self.Constants.RESULT_LINK_TAG and self.Constants.RESULT_LINK_CLASS in ClassName:
                    return JobPostDOM['href']
        
        return self.GetDataFromJobPostDOM(JobPostDOM, 
                                          self.Constants.RESULT_LINK_TAG, 
                                          self.Constants.RESULT_LINK_CLASS, 
                                          'href')    

    def GetJobTitleFromJobPostDOM(self, JobPostDOM, DOMAttr=None):
        """
        Return Job title from the job post given the DOM element that 
        contains the link, else None
        """
        return self.GetDataFromJobPostDOM(JobPostDOM, 
                                          self.Constants.RESULT_TITLE_TAG, 
                                          self.Constants.RESULT_TITLE_CLASS, 
                                          DOMAttr)

    def GetCompanyFromJobPostDOM(self, JobPostDOM, DOMAttr=None):
        """
        Return company name from the job post given the DOM element
        that contains the link, else None
        """
        return self.GetDataFromJobPostDOM(JobPostDOM, 
                                          self.Constants.RESULT_COMPANY_TAG, 
                                          self.Constants.RESULT_COMPANY_CLASS, 
                                          DOMAttr)

    def GetPostedTimeFromJobPostDOM(self, JobPostDOM, DOMAttr=None):
        """
        Return time at which the job is posted from the job post 
        given the DOM element that contains the link, else None
        """
        return self.GetDataFromJobPostDOM(JobPostDOM, 
                                          self.Constants.RESULT_POSTED_TAG, 
                                          self.Constants.RESULT_POSTED_CLASS, 
                                          DOMAttr)

    def GetJobLocationFromJobPostDOM(self, JobPostDOM, DOMAttr=None):
        """
        Return time at which the job is posted from the job post 
        given the DOM element that contains the link, else None
        """
        return self.GetDataFromJobPostDOM(JobPostDOM, 
                                          self.Constants.RESULT_LOCATION_TAG, 
                                          self.Constants.RESULT_LOCATION_CLASS, 
                                          DOMAttr)
        

    def GetDataFromJobPostDOM(self, JobPostDOM, CustomDataDOMTag, CustomDataDOMClass=None, CustomDataDOMAttribute=None):
        """
        Get custom data as per requested by the user, given the tag
        from the company DOM
        """
        JobCustomData = None
        if isinstance(CustomDataDOMTag, str):
            if CustomDataDOMClass is None:
                JobCustomData = JobPostDOM.find(CustomDataDOMTag)
            elif isinstance(CustomDataDOMClass, str):
                JobCustomData = JobPostDOM.find(CustomDataDOMTag, class_=CustomDataDOMClass)
            else:
                raise TypeError('CustomDataDOMClass should either\
                                be none or str, not' + type(CustomDataDOMClass))
            if JobCustomData is not None:
                if isinstance(CustomDataDOMAttribute, str):
                    return JobCustomData[CustomDataDOMAttribute]
                elif CustomDataDOMAttribute is None:
                    return JobCustomData.text
                else:
                    raise TypeError('CustomDataDOMAttribute should either\
                                     be none (for innerText) or str, not' + type(CustomDataDOMAttribute))
        return None

    def ListJobContents(self, Content, ToDisplay=None):
        """
        Returns the list of Job list to the Listing
        To prepare: Custom data as per the user requests.
        """
        Soup = BeautifulSoup(Content.replace('\\n', '').replace('  ', ''), features="html.parser")
        JobPostResult = Soup.find(self.Constants.RESULT_LIST_TAG, class_=self.Constants.RESULT_LIST_CLASS)

        if JobPostResult is not None:
            AllJobPostDOMList = JobPostResult.findAll(self.Constants.RESULT_PARENT_TAG)
            if AllJobPostDOMList is not None:
                return self.ListAllAvailableCompaniesInfo(AllJobPostDOMList, ToDisplay)
            else:
                raise DOMNotFoundException('No DOM element related to search list found')
        return None
        # else:
        #     raise DOMNotFoundException('No DOM element related to search result found')

    def ListAllAvailableCompaniesInfo(self, AllJobPostDOMList, ToDisplay):
        """
        Prepares and returns the link associated to the Job details.
        :param AllJobPostDOMList List of all DOM denoting the Job post.
        :returns a dictionary of links and required details for the Job Post.
        """
        # To be replaced with dataframe or np array.
        # Useful for people performing data analytics
        columns = ['JobLink', 'JobTitle', 'CompanyName', 'TimePosted', 'JobLocation']
        dataframe = pd.DataFrame(columns=columns)
        if ToDisplay is not None:
            ToDisplay = set(ToDisplay)
            for Attr in ToDisplay:
                if Attr not in self.ToDisplay:
                    ToDisplay.remove(Attr)

        JobDictionary = {}
        index = 1
        for JobPostDOM in AllJobPostDOMList:
            Link = self.GetLinkOfJobPostFromJobPostDOM(JobPostDOM)
            # print(JobPostDOM)
            # Check if domain name is given or not
            if Link is not None and not(Link.startswith('https://')) and not(Link.startswith('http://')):
                Link = self.DomainName + Link
            # to check whether if the link has relative path or absolute path
            if Link is not None:
                # JobDictionary[Link] = {}
                Dictionary =  {
                        'JobLink':Link,
                        'JobTitle': self.GetJobTitleFromJobPostDOM(JobPostDOM), 
                        'CompanyName': self.GetCompanyFromJobPostDOM(JobPostDOM), 
                        'TimePosted': self.GetPostedTimeFromJobPostDOM(JobPostDOM),
                        'JobLocation': self.GetJobLocationFromJobPostDOM(JobPostDOM)}
                dataframe = dataframe.append(Dictionary, ignore_index=True)

        return dataframe

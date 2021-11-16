#!/usr/bin/env python
from bs4 import BeautifulSoup
import importlib
from ReaderInterfaces.IReader import IReader
from ReaderImplementation.Constants.LinkedInReaderConstants import *
from pandas import DataFrame

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

class JobReader(IReader):
    """
    An attempt to generalize Job post retrieving, according to the user requests.
    By default, we are using LinkedIn as a Job Scraping website.
    To decide from which website to scrape, you need to declare constants, as the
    reader is totally dependent on the constants. If classes are not known or they are empty,
    you can put them as None.
    For reference, you can see ./Constants/LinkedInReaderConstants.py
    """
    def __init__(self, Platform=None):
        # Dynamic module loading:
        # This is where constants defined are loaded and helpful for searching the 
        # required data from the pages
        if Platform is not None:
            self.Constants = importlib.import_module('ReaderImplementation.Constants.%sReaderConstants' % Platform)
        else:
            self.Constants = importlib.import_module('ReaderImplementation.Constants.LinkedInReaderConstants')

        self.ToDisplay = ['JobLink', 'CompanyName', 'JobTitle', 'JobLocation', 'TimePosted']

        self.DomainName = self.Constants.DOMAIN_NAME
        self.SearchURL = self.Constants.JOB_SEARCH_URL
        self.QueryParams = {
                            'SearchQuery':     self.Constants.JOB_SEARCH_QUERY, 
                            "JobLocation":     self.Constants.JOB_SEARCH_LOCATION,
                            "ExperienceLevel": self.Constants.JOB_SEARCH_EXP, 
                            "DatePosted":      self.Constants.JOB_SEARCH_TIME_POSTED, 
                            "NumberOfPages":   self.Constants.JOB_SEARCH_PAGE_KEY
                            }
        self.UserTags, self.UserClass, self.UserAttr = {}, {}, {}
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

        QueryURL = '%s?' % self.SearchURL

        for QueryKey, QueryValue in KeywordParams.items():
            if QueryKey not in self.QueryParams:
                print('Key %s not found in list of keys' % QueryKey)

            elif self.QueryParams[QueryKey] is not None:
                if QueryKey == 'NumberOfPages':
                    QueryValue = PageNumber * self.PageMultiplier

                QueryURL += '%s=%s&' % (self.QueryParams[QueryKey], QueryValue)

        return QueryURL

    def SetTagsFromUser(self, UserAttr, TagName, TagClass=None, DOMAttr=None):
        """
        Set user according to the user observed tags, class, and retrieve
        attribute/DOM inner text
        :param UserAttr title to retrieve
        :param TagName Tag for the DOM element from Job Post
        :param TagClass ClassName for specific searching
        :param DOMAttr DOM attr that will be returned on selecting the UserAttr
        :returns None
        """
        self.UserTags[UserAttr] = TagName
        self.UserClass[UserAttr] = TagClass
        self.UserAttr[UserAttr] = DOMAttr

    def GetLinkOfJobPostFromJobPostDOM(self, JobPostDOM):
        """
        Return Link from the job post given the DOM element that contains 
        the link, else None
        """
        # Sometimes the link is the main Job post DOM element,
        # to check whether that is the case as per the constants defined.
        if JobPostDOM is not None:
            ClassName = JobPostDOM['class'] if JobPostDOM.has_attr('class') else None

            if ClassName is not None and self.Constants.RESULT_LINK_CLASS is not None:
                if JobPostDOM.name == self.Constants.RESULT_LINK_TAG and self.Constants.RESULT_LINK_CLASS in ClassName:
                    return JobPostDOM['href'].strip()
        
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
    
    def GetUserDataFromJobPostDOM(self, Attr, JobPostDOM, DOMAttr=None):
        """
        Get data defined programatically by user
        :param self instance of the object
        :param Attr attribute to retrieve
        :param JobPostDOM internal parsing of DOM
        :param DOMAttr attribute to retrieve, defaults to None
        :returns Data if Attr is defined in UserAttr and it exists in DOM, else 
        returns None
        """
        UserTags = self.UserTags[Attr] if Attr in self.UserTags else None
        UserClass = self.UserClass[Attr] if Attr in self.UserTags else None
        UserAttr = self.UserAttr[Attr] if Attr in self.UserTags else DOMAttr
        return self.GetDataFromJobPostDOM(JobPostDOM,
                                          UserTags,
                                          UserClass,
                                          UserAttr)

    def GetDataFromJobPostDOM(self, JobPostDOM, CustomDataDOMTag, CustomDataDOMClass=None, CustomDataDOMAttribute=None):
        """
        Get custom data as per requested by the user, given the JobPostDOM and
        Tag to retrieve
        :param JobPostDOM main DOM element
        :param CustomDataDOMTag Tag to be searched
        :param CustomDataDOMClass class associated with the tag in DOM element, defaults to None
        :param CustomDataDOMAttribute attribute to be returned, defaults to None
        :returns Attribute of the DOM if CustomDataDOMAttribute is defined, else returns inner text for valid
        tag and class value
        """
        JobCustomData = None
        if isinstance(CustomDataDOMTag, str):
            JobCustomData = JobPostDOM.find(CustomDataDOMTag, class_=CustomDataDOMClass) \
                if isinstance(CustomDataDOMClass, str) else JobPostDOM.find(CustomDataDOMTag)

            if JobCustomData is not None:
                if isinstance(CustomDataDOMAttribute, str):
                    return JobCustomData[CustomDataDOMAttribute]
                else:
                    return JobCustomData.text.strip()
        return None

    def Columns(self, ToDisplay):
        """
        Set the columns
        """
        columns = list(self.ToDisplay)
        if ToDisplay is not None:
            ToDisplay = set(ToDisplay)
            for Attr in ToDisplay:
                if Attr in self.ToDisplay:
                    ToDisplay.remove(Attr)

            columns += list(ToDisplay)

        return columns

    def ListContents(self, Content, ToDisplay=None):
        """
        Returns the list of Job list to the Listing
        To prepare: Custom data as per the user requests.
        """
        ToDisplay = self.Columns(ToDisplay)

        Soup = BeautifulSoup(Content, features="html.parser", from_encoding="UTF-8")
        JobPostResult = Soup.find(self.Constants.RESULT_LIST_TAG, class_=self.Constants.RESULT_LIST_CLASS)

        if JobPostResult is not None:
            AllJobPostDOMList = JobPostResult.findAll(self.Constants.RESULT_PARENT_TAG)

            if AllJobPostDOMList is not None:
                return self.ListAllAvailableCompaniesInfo(AllJobPostDOMList, ToDisplay)
            else:
                raise DOMNotFoundException('No DOM element related to search list found')

        return DataFrame(columns=ToDisplay)

    def ListAllAvailableCompaniesInfo(self, AllJobPostDOMList, ToDisplay=None):
        """
        Prepares and returns the link associated to the Job details.
        :param AllJobPostDOMList List of all DOM denoting the Job post.
        :returns a dictionary of links and required details for the Job Post.
        """
        # To be replaced with dataframe or np array.
        # Useful for people performing data analytics
        dataframe = DataFrame(columns=ToDisplay)

        for JobPostDOM in AllJobPostDOMList:
            Link = self.GetLinkOfJobPostFromJobPostDOM(JobPostDOM)
            # to check whether if the link has relative path or absolute path
            if Link is not None:
                # Check if domain name is given or not
                Link = '%s%s' % (self.DomainName, Link) if Link is not None and not(Link.startswith('https://')) else Link
                Dictionary = {
                        'JobLink': Link,
                        'JobTitle': self.GetJobTitleFromJobPostDOM(JobPostDOM), 
                        'CompanyName': self.GetCompanyFromJobPostDOM(JobPostDOM), 
                        'TimePosted': self.GetPostedTimeFromJobPostDOM(JobPostDOM),
                        'JobLocation': self.GetJobLocationFromJobPostDOM(JobPostDOM)}

                if ToDisplay is not None:
                    for DisplayAttr in ToDisplay:
                        if DisplayAttr not in self.ToDisplay:
                            Dictionary[DisplayAttr] = self.GetDataFromJobPostDOM(JobPostDOM,
                                                                                self.UserTags[DisplayAttr],
                                                                                self.UserClass[DisplayAttr],
                                                                                self.UserAttr[DisplayAttr])

                dataframe = dataframe.append(Dictionary, ignore_index=True)

        return dataframe

#!/usr/bin/env python
import requests
import json
from ReaderImplementation.JobReader import JobReader
from Utility.HistoryList import HistoryList
from TaskExecutor.TaskExecutor import SendParallelRequest
import pandas as pd
from time import time

class JobListing:
    """
    Job listing class to list available Jobs from Multiple sites, default takes linkedin
    as website for Job Scraping
    """
    def __init__(self, website=['LinkedIn'], HistorySize=10):
        self.HistoryList = HistoryList(HistorySize)
        self.readers = {}
        if "LinkedIn" in website:
            self.readers["LinkedIn"] = JobReader('LinkedIn')
        if "Indeed" in website:
            self.readers["Indeed"] = JobReader('Indeed')
        self.QueryResults = None

    def CreateSession(WebsiteParams):
        """
        To create a session for personalized session.
        :param WebsiteParams parameter for website (to be read thorugh a file
        for easier)
        """
        pass

    def SendRequests(self, KeywordParams):
        """
        Sends multiple requests based on keyword parameters.
        :param KeywordParams paramters for sending the requests
        :returns Details from all the available list
        """
        if isinstance(KeywordParams, dict) == False:
            raise TypeError('KeywordParams not an instance of dictionary')
        else:
            start = time()
            URLParamList = []
            for ReaderNames, Queries in KeywordParams.items():
                if ReaderNames in self.readers:
                    reader = self.readers[ReaderNames]
                    for query in Queries:
                        TotalPages = query['NumberOfPages'] if 'NumberOfPages' in query else 1
                        # Generate argument for the JobReader as tuples
                        URLParamList += [(reader, reader.ConstructQueryURL(query, PageNumber))
                                         for PageNumber in range(TotalPages)]
                else:
                    print('No reader found for {}'.format(ReaderNames))

            print(URLParamList)

            if len(URLParamList) > 0:
                JobDetails = SendParallelRequest(self.__Send__, URLParamList)
                self.QueryResults = JobDetails
                self.HistoryList += ([URLTuple[1] for URLTuple in URLParamList], JobDetails)
                end = time()
                print('Finished.\nTime taken for scraping: {}s'.format(end - start))

            return JobDetails

    def SetNewData(self, Platform, UserAttribute, TagName, TagClass=None, DOMAttr=None):
        """
        Sets custom data to retrieve from the user.
        """
        self.Reader[Platform].SetTagsFromUser(UserAttribute, TagName, TagClass, DOMAttr)


    def __Send__(self, Params):
        """
        Internal method to send the request to required URL parameter
        """
        Reader, QueryURL = Params
        request = requests.get(QueryURL)
        JobDetails = Reader.ListContents(request.content)
        return JobDetails

    def FileHandle(self, mode, saveAs):
        """
        Save the file with certain mode (either w, w+, wb, a+)
        :param mode
        :param saveAs file name
        """
        if self.QueryResults is not None and isinstance(self.QueryResults, pd.DataFrame):
            self.QueryResults.to_csv(saveAs, index=False)
        else:
            print('No search has been done to be saved')

    def Results(self):
        """
        Prints the recent results from the Job list
        """
        if self.QueryResults is None:
            print('{"Message": "No results as of yet"}')
            return None
        return self.QueryResults

    def StoreCurrResults(self, saveAs='Output.csv'):
        """
        Creates a new file and stores the result in a new file
        """
        self.FileHandle('w', saveAs)   

    def PrintRecentHistory(self):
        """
        Print results for recently searched queries. The history size depends on
        parameter HistorySize
        """
        print(self.HistoryList)

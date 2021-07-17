#!/usr/bin/env python
import requests
import json
from ReaderImplementation.Reader import Reader
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
            self.readers["LinkedIn"] = Reader('LinkedIn')
        if "Indeed" in website:
            self.readers["Indeed"] = Reader('Indeed')
        self.QueryResults = None

    def SendRequests(self, KeywordParams):
        """
        Sends multiple requests based on keyword parameters.
        :param KeywordParams paramters for sending the requests
        :returns Details from all the available list
        """
        if isinstance(KeywordParams, dict) == False:
            print('keyWord not an instance of dictionary')
        else:
            start = time()
            JobDetails = {}

            URLParamList = []
            for ReaderNames in KeywordParams:
                if ReaderNames in self.readers:
                    reader = self.readers[ReaderNames]
                    parameters = KeywordParams[ReaderNames]
                    TotalPages = parameters['NumberOfPages'] if 'NumberOfPages' in parameters else 1
                    for PageNumber in range(TotalPages):
                        QueryURL = reader.ConstructQueryURL(parameters, PageNumber)
                        Tuple = (reader, QueryURL)
                        URLParamList.append(Tuple)
                        print(QueryURL)
                else:
                    print('No reader found for {}'.format(ReaderNames))   

            JobDetails = SendParallelRequest(self.__Send__, URLParamList)
            JobDetails.reset_index(drop=True)
            self.QueryResults = JobDetails
            self.HistoryList += JobDetails
            end = time()

            print('Finished.\nTime taken for scraping: {}s'.format(end - start))
            return JobDetails

    def __Send__(self, Params):
        """
        Internal method to send the request to required URL parameter
        """
        Reader, QueryURL = Params
        request = requests.get(QueryURL)
        response = str(request.content)
        JobDetails = Reader.ListJobContents(response)
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

    def AppendCurrResults(self, saveAs='CurrentSearch.json'):
        """
        Appends to an existing file, creates new one if not exists
        """
        self.FileHandle('a+', saveAs)        

    def PrintRecentHistory(self):
        """
        Print results for recently searched queries. The history size depends on
        parameter HistorySize
        """
        print(self.HistoryList)

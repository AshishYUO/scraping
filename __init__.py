#!/usr/bin/env python
import socket
from ListingImplementation.JobListing import JobListing

if __name__ == "__main__":
    JobList = JobListing(website=['LinkedIn', 'Indeed'])
    JobList.SendRequests({'Indeed': {
                                'SearchQuery': 'Frontend Developer', 
                                'JobLocation': 'India',
                                'NumberOfPages': 4
                                }, 
                          'LinkedIn': {
                                'SearchQuery': 'software engineer', 
                                'JobLocation': 'India',
                                'NumberOfPages': 4
                                }
                            })
    # JobList.PrintRecentHistory()
    curr = JobList.Results()
    print(curr)
    JobList.StoreCurrResults()

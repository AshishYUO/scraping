#!/usr/bin/env python
from abc import ABC, abstractmethod

class IReader(ABC):
	@abstractmethod
	def ConstructQueryURL(self, KeywordParams, TotalPages):
		"""
        Construct the URL for request. To be implemented by other readers
        :param KeywordParams, for mapping get keys with their values
        :param TotalPages, display first n pages.
        :returns url string
        """
		raise NotImplementedError
		
	@abstractmethod
	def ListContents(self, Content, ToDisplay):
		"""
		Constructs the result for the pages. To be implemented by Job Reader
		:param Content: HTML content to be parsed for Job searching
		"""
		raise NotImplementedError

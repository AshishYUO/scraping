"""
To create a constant file, keep in mind that the name should be the same as
you would pass to the reader. (If it's {LinkedIn}ReaderConstants, or 
{Indeed}ReaderConstants, pass as LinkedIn or Indeed respectively)
"""
# Constants for URL construction
DOMAIN_NAME='https://linkedin.com'
# Job search URL for searching the LinkedIn Job.
JOB_SEARCH_URL='https://linkedin.com/jobs/search'
# Search query and location are at least mandatory.
JOB_SEARCH_QUERY='keywords'

JOB_SEARCH_LOCATION='location'
# Experience level
JOB_SEARCH_EXP='f_E'

JOB_SEARCH_EXP_VALUE_ARR = ["Internship", "Associate", "Entry Level", "Mid-Senior Level", "Director", "Executive"]

def EXP_VALUE(ValueArr):
	Join = []
	for Value in ValueArr:
		Val = JOB_SEARCH_EXP_VALUE_ARR.index(Value) + 1
		if Val > 0:
			Join.append(Val)
	return ','.join(Join)

# Page number: often times these are mentioned as offsets. You can mention
# offset by a PageNumber * JOB_SEARCH_PAGE_MULTIPLIER
JOB_SEARCH_PAGE_KEY='pageNums'

JOB_SEARCH_PAGE_MULTIPLIER=1
# Time recently posted jobs.
JOB_SEARCH_TIME_POSTED='f_TPR'

# Constants for classes and tags
RESULT_LIST_CLASS='jobs-search__results-list'

RESULT_LIST_TAG='ul'

RESULT_PARENT_TAG='li'

RESULT_TITLE_CLASS='base-search-card__title'

RESULT_TITLE_TAG='h3'

RESULT_LINK_CLASS='base-card__full-link'

RESULT_LINK_TAG='a'

RESULT_COMPANY_CLASS='base-search-card__subtitle'

RESULT_COMPANY_TAG='h4'

RESULT_LOCATION_CLASS='job-search-card__location'

RESULT_LOCATION_TAG='span'

RESULT_POSTED_TAG='time'

RESULT_POSTED_CLASS=None

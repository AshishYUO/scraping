from concurrent.futures import ThreadPoolExecutor
from pandas import DataFrame

def SendParallelRequest(Method, URLParamList):
    """
    Parallel execution of method
    :param method, method to execute
    :param URLParamList URL parameters to be passed to the method
    :returns DataFrame from multiple sources
    """
    URLListResult = DataFrame()
    with ThreadPoolExecutor(max_workers=5) as Executor:
        Executor.submit(Method, len(URLParamList))
        
        result = Executor.map(Method, URLParamList)

    for dictionary in result:
        URLListResult = URLListResult.append(dictionary)

    return URLListResult

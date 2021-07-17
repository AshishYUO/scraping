from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def SendParallelRequest(Method, URLParamList):
	"""
	Parallel execution of method
	:param method, method to execute
	:param URLParamList URL parameters to be passed to the method
	:returns DataFrame from multiple sources
	"""
	URLListResult = pd.DataFrame()
	with ThreadPoolExecutor(max_workers=5) as Executor:
		Executor.submit(Method, len(URLParamList))
		
		result = Executor.map(Method, URLParamList)

	for dictionary in result:
		URLListResult = URLListResult.append(dictionary)

	return URLListResult

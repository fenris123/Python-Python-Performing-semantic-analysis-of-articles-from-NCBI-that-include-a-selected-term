# Python-Python-Performing-semantic-analysis-of-articles-from-NCBI-that-include-a-selected-term


Program Description:
This program conducts a simple semantic analysis by conducting a frequency analysis of word usage within article abstracts retrieved from the NCBI database. 
Specifically designed to analyze articles containing a user-specified term, it provides insights into the language used within this subset of articles.

Usage:
The program is platform-independent and can be used with any operating system.

Target Audience:
Developed with simplicity in mind, the program is tailored for users with minimal computer literacy or programming experience. 
It offers a straightforward approach to exploring the language patterns in articles related to a specific search term.

Limitations:
Due to technical constraints, the program restricts the number of articles retrieved to 200. 
This limitation ensures compliance with the NCBI API usage policies while providing a manageable dataset for analysis.

Caution:
Users should interpret the results with caution, recognizing that the analysis is based on a limited sample size. 
The program aims to demonstrate the simplicity of conducting semantic analysis on article abstracts, rather than providing exhaustive linguistic insights.


LIBRARIES:
here's a simplified list of the Python libraries used:

os
urllib.
xml.etree.ElementTree.
pandas.
json.
collections.Counter.
string.
nltk with nltk.corpus.stopwords: (To remove words with "no semantic sense" as articles, prepositions...)

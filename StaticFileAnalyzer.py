#! /usr/env/python
"""Extracts information from a file containing datasets as JSON objects, 
then creates a CSV file containing the results.

Script usage
------------
user@host: python StaticFileAnalyzer.py <input_file> <destination_file>

"""

import sys
import utils.PortalUtils as PortalUtils
import utils.FileUtils as FileUtils

if __name__ == "__main__":
    docstring = """USAGE: python StaticFileAnalyzer.py <input_file> <output_file>
    """
    if len(sys.argv) < 3:
        sys.exit(docstring)
    datafile = sys.argv[1]
    outfile = sys.argv[2]

    Reader = FileUtils.JsonFileReader(datafile)
    datasets = Reader.get_all_datasets()
    Analyzer = PortalUtils.DatasetAnalyzer()
    for item in datasets:
        Analyzer.add_dataset(item)
    Analyzer.make_csv(outfile)

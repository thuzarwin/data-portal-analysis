"""Extract information from Austin's datasets.

Script usage:

    $ python PortalAnalytics.py <input_file> <destination_file>

"""

import json
import csv
import sys
import datetime


class DatasetAnalyzer:
    def __init__(self, json_filename):
        """Initialize a Dataset Analyzer.
        """
        with open(json_filename) as data_json:
            json_str = data_json.read()
            data_dict = json.loads(json_str)
        self._datasets = self._multiset_handler(data_dict)

        self._headers = ["id", "soc_resource_id", "dept",
                         "name", "col_position", "col_name", "col_field_name",
                         "soc_id", "soc_table_column_id",
                         "soc_data_type_name", "soc_render_type_name",
                         "num_null", "num_not_null", "ex_value",
                         "snapshot_date_time", "is_current",
                         "report_creation_time"]

        self._creation_time = datetime.datetime.now().isoformat()
        self._rows = self._analyze_all()


    def _multiset_handler(self, data_dict):
        try:
            datasets = data_dict['datasets']
        except(KeyError):
            datasets = [data_dict]
        except:
            raise KeyError("Error accessing dataset JSON object")
        return datasets
            
    def _analyze_dataset(self, dataset):
        """Analyze a dataset (dict) and return a list of rows.
        """
        rows = []
        
        dataset_time = self._get_date_time(dataset)
        dataset_info = self._get_dataset_info(dataset)
        for col in dataset['columns']:
            current_row = []
            current_row += dataset_info
            current_row.append(col['position'])
            current_row.append(col['name'])
            current_row.append(col['fieldName'])
            current_row.append(col['id'])
            current_row.append(col['tableColumnId'])
            current_row.append(col['dataTypeName'])
            current_row.append(col['renderTypeName'])
            current_row += self._get_cached_contents(col)
            current_row.append(dataset_time)
            current_row.append(u"IS_CURRENT")         # placeholder
            current_row.append(self._creation_time)
            encoded_row = []      # csv module doesn't like unicode
            for item in current_row:
                if isinstance(item, unicode):
                    item = item.encode('utf-8')
                encoded_row.append(item)

            rows.append(encoded_row)

        return rows

    def _analyze_all(self):
        """Run the analyzer on all datasets and return the results.
        """
        results = []
        for item in self._datasets:
            for row in self._analyze_dataset(item):
                results.append(row)
        return results

    def _get_dataset_info(self, dataset):
        """Returns information about the dataset as a list.
        """
        dataset_id = dataset['id']
        dataset_name = dataset['name']
        try:
            custom = dataset['metadata']['custom_fields']
            dataset_dpt = custom['Additional Information']['Department']
        except:
            # print dataset['name']
            dataset_dpt = "No Department Information"

        return [dataset_id, dataset_name, dataset_dpt]
        
    def _get_cached_contents(self, col):
        """This function retrieves information from columns
        that have a section for cached contents.
        """
        return_list = []
        try:
            cached = col['cachedContents']
            return_list.append(cached['null'])
            return_list.append(cached['non_null'])
        except:
            return_list.append('null')
            return_list.append('null')
        try:
            top = col['cachedContents']['top']
            item = top[0]['item']
            if col['dataTypeName'] == 'url':
                try:
                    item = item['url']
                except:
                    item = item['description']
            if col['dataTypeName'] == 'location':
                item = item['human_address']['address']
        except:
            item = 'null'

        return_list.append(item)
        return return_list

    def _get_date_time(self, dataset):
        """This function fills the snapshot_date_time column.
        """
        try:
            date = dataset['publicationDate']
        except:
            date = "null"
        return date

    def make_csv(self, filename):
        with open(filename, "wb") as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self._headers)
            for number, row in enumerate(self._rows):
                writer.writerow([number+1]+row)


if __name__ == "__main__":
    docstring = """USAGE: python PortalAnalytics.py <input_file> <output_file="out.csv"> """
    if len(sys.argv) < 3:
        sys.exit(docstring)
    datafile = sys.argv[1]
    outfile = sys.argv[2]

    Analyzer = DatasetAnalyzer(datafile)
    Analyzer.make_csv(outfile)

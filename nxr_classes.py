import requests
import pandas as pd
import json

class Organisations:
    def __init__(self, register):
        self.register = register
        self.overview = pd.DataFrame()
        self.request = dict()
        self.json = dict()
        self.data = dict()
        self.df = pd.DataFrame()

    def get_overview(self):
        res = requests.get("https://data-"+ self.register +".udir.no/v3/enheter?antallPerSide=20000")
        j = res.json()
        orgs = j['Enheter']
        self.overview = pd.DataFrame.from_dict(orgs)

    # Method for collection data for specific organisation
    def get_org(self, orgnr):
        res_org = requests.get("https://data-"+ self.register +".udir.no/v3/enhet/" + orgnr)
        self.request[orgnr] = res_org.status_code

        try: 
            res_org.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Request error:" + str(e)

        self.json[orgnr] = res_org.json()

    def flatten_json(self, orgnr):
        json_data = self.json[orgnr]

        new_dict = dict()

        json_flat = self.walk_dict(json_data, new_dict)

        self.data[orgnr] = json_flat

    # Recursive helper method for traversing and flattening json
    def walk_dict(self,d, new_dict, parent_key = ''):

        for key, val in d.items():
            # If val is a dictionary, traverse
            # the nested dictionary
            if isinstance(val, dict):
                self.walk_dict(val, new_dict, parent_key = key + '_')
            # if val is a list, traverse the list of 
            # dictionaries. Adding suffix i to key. 
            elif isinstance(val, list):
                for i in range(len(val)): # for each list element
                    if isinstance(val[i], dict): # if the list element is dictionary, walk it
                        self.walk_dict(val[i], new_dict, parent_key = key + '_' + str(i) + '_')
            else:
                new_dict[parent_key + key] = val

        return new_dict
    
    def gen_df(self):
        self.df = pd.DataFrame.from_dict(self.data, orient = "index")


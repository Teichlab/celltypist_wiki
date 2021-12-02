from celltypist import models
import json
from datetime import datetime
import os
import sys
#------------> setting here
default_model = 'Immune_All_Low.pkl'
models_preceding = ['Immune_All_Low.pkl', 'Immune_All_High.pkl', 'Immune_All_PIP.pkl', 'Immune_All_AddPIP.pkl']
#<------------ setting here

##Before all of these...
# 1) All models in the s3 are up-to-date, some of them will be usable by the users, some for internal use
# 2) Store all usable (see 1 above) models in `model_folder` 
# 3) 1) and 2) should both be up-to-date

#all usable models
model_folder = sys.argv[1]
all_models = os.listdir(model_folder)
all_models = models_preceding + sorted([x for x in all_models if x not in models_preceding])

#basic info
dict_ = {"description": "CellTypist model list", "last_update": str(datetime.now())}

#model list
model_list = []
for each_model in all_models:
    model_load = models.Model.load(f"{model_folder}/{each_model}")
    filename = each_model
    url = model_load.description['url']
    #<-----------------------------Add version from here----------------------------->
    if filename.startswith('Immune') and (filename != 'Immune_All_PIP.pkl') and (filename != 'Immune_All_AddPIP.pkl'):
        version = url[43:45]
    elif (filename == 'Cells_Lung_Airway.pkl') or (filename == 'Nuclei_Lung_Airway.pkl'):
        version = 'v1'
    else:
        version = 'v1'
    #<-----------------------------Add version end here----------------------------->
    date = model_load.description['date']
    details = model_load.description['details']
    number_celltypes = model_load.description['number_celltypes']
    each_info = {"filename": filename, "url": url, "version": version, "date": date, "details": details, "No_celltypes": number_celltypes}
    if filename == default_model:
        each_info['default'] = True
    model_list.append(each_info)
dict_["models"] = model_list

#dump
with open('json/models.json', 'w') as f:
    json.dump(dict_, f, indent = 2)

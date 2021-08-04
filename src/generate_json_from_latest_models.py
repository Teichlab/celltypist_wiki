from celltypist import models
import json
from datetime import datetime

#download latest models
models.download_models(force_update = True)
model_folder = models.models_path
print(f"models are stored in {model_folder}")

#basic info
dict_ = {"description": "CellTypist model list", "last_update": str(datetime.now())}

#model list
model_list = []
all_models = models.get_all_models()
for each_model in all_models:
    model_load = models.Model.load(each_model)
    #
    filename = each_model
    url = model_load.description['url']
    version = url[43:45]
    date = model_load.description['date']
    details = model_load.description['details']
    number_celltypes = model_load.description['number_celltypes']
    #
    each_info = {"filename": filename, "url": url, "version": version, "date": date, "details": details, "No_celltypes": number_celltypes}
    if filename == 'Immune_All_Low.pkl':
        each_info['default'] = True
    model_list.append(each_info)

#combine info
dict_["models"] = model_list

#dump
with open('../json/models.json', 'w') as f:
    json.dump(dict_, f, indent = 2)

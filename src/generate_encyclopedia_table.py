import pandas as pd
import numpy as np

#Tissue & Dataset
TD = pd.read_csv('tables/celltypist_immune_meta.csv')
#filter
combine = TD.majority_voting_FS + TD.Tissue + TD.Dataset
counts = combine.value_counts()
keep = counts.index[counts >= 5]
TD = TD[np.isin(combine, keep)]
#main
celltypes = np.unique(TD.majority_voting_FS)
assert len(celltypes) == 87
tissues  = [', '.join(list(np.unique(TD.loc[TD.majority_voting_FS == celltype, 'Tissue']))) for celltype in celltypes]
datasets = [', '.join(list(np.unique(TD.loc[TD.majority_voting_FS == celltype, 'Dataset']))) for celltype in celltypes]
df_TD = pd.DataFrame(dict(Tissues = tissues, Datasets = datasets), index = celltypes)

#Top 10 markers
from celltypist import models
#load
print(f"Make sure the Immune_All_Low.pkl is the latest model")
model = models.Model.load('Immune_All_Low.pkl')
features = model.features
celltypes = model.cell_types
coef = model.classifier.coef_
assert len(celltypes) == 87
assert len(features) == coef.shape[1]
assert len(celltypes) == coef.shape[0]
#main
gene_index = np.argpartition(coef, -10, axis = 1)[:, -10:]
gene_index = features[gene_index]
gene_index = [", ".join(list(x)) for x in gene_index]
df_T10 = pd.DataFrame(gene_index, index = celltypes, columns = ['Top 10 important genes from the Celltypist model'])

#Basic
df_Basic = pd.read_excel('tables/Basic_celltype_information.xlsx')
df_Basic.set_index('Low-hierarchy cell types', inplace=True, drop = False)

#Order
df_TD = df_TD.loc[df_Basic['Low-hierarchy cell types']]
df_T10 = df_T10.loc[df_Basic['Low-hierarchy cell types']]

#Combine
df = df_Basic[['High-hierarchy cell types', 'Low-hierarchy cell types', 'Description', 'Cell Ontology ID']].join(df_TD[['Tissues', 'Datasets']]).join(df_Basic[['Curated markers']]).join(df_T10[['Top 10 important genes from the Celltypist model']])
with pd.ExcelWriter('encyclopedia/encyclopedia_table.xlsx') as writer:
    df.to_excel(writer, sheet_name = "Main", index = False)

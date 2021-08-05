import pandas as pd
import numpy as np

#Tissue & Dataset
TD = pd.read_csv('../tables/celltypist_immune_meta.csv')
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

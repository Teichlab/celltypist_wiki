import pandas as pd
import numpy as np
import pickle
import sys
import scanpy as sc
import os
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
atlas = sys.argv[1]
version = sys.argv[2]
#setting->
setting = pd.read_csv(f"{ROOT_PATH}/atlases/{atlas}/{version}/config/Heatmap.config", header = None, index_col = 0)
adata = sc.read(setting.loc['adata_path', 1])
tissue_column = setting.loc['tissue_column', 1]
celltype_column = setting.loc['celltype_column', 1]
tissue_order = pd.read_csv(f'{ROOT_PATH}/atlases/{atlas}/{version}/Heatmap_data/tissue_order.txt', header = None)[0].values
celltype_order = pd.read_csv(f'{ROOT_PATH}/atlases/{atlas}/{version}/Heatmap_data/celltype_order.txt', header = None)[0].values
use_raw = setting.loc['use_raw', 1]
filter_out = int(setting.loc['filter_out', 1])
do_normalize = setting.loc['do_normalize', 1]
#<-setting

def celltypist_AverageExpression_PercentExpression(adata,
                                                   group1_by, group2_by,
                                                   group1_order, group2_order,
                                                   use_raw = 'True',
                                                   filter_out = 5):
    #group1 == organ ;  group2 == cell type
    adata = adata.raw.to_adata() if use_raw in ['true', 'True', 'TRUE'] else adata
    adata.X = np.expm1(adata.X)
    #assert groups
    assert np.all(np.unique(adata.obs[group1_by]) == np.unique(np.array(group1_order)))
    assert np.all(np.unique(adata.obs[group2_by]) == np.unique(np.array(group2_order)))
    groups = [f"{x}___{y}" for x in group1_order for y in group2_order]
    #main
    exp = pd.DataFrame(np.nan, index = adata.var_names, columns = groups)
    pct = pd.DataFrame(np.nan, index = adata.var_names, columns = groups)
    for x in group1_order:
        for y in group2_order:
            group = f"{x}___{y}"
            flag = (adata.obs[group1_by] == x) & (adata.obs[group2_by] == y)
            if np.sum(flag) <= filter_out:
                continue
            else:
                exp_input = adata.X[flag, :].mean(axis = 0)
                pct_input = (adata.X[flag, :] > 0).mean(axis = 0)
                exp[group] = exp_input.A1 if isinstance(exp_input, np.matrix) else exp_input
                pct[group] = pct_input.A1 if isinstance(pct_input, np.matrix) else pct_input
    return {'exp': np.log1p(exp), 'pct': pct, 'group1': group1_order, 'group2': group2_order}

#main
if do_normalize in ['true', 'True', 'TRUE']:
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
exp_pct = celltypist_AverageExpression_PercentExpression(adata, tissue_column, celltype_column, tissue_order, celltype_order, use_raw, filter_out)
with open(f'{ROOT_PATH}/atlases/{atlas}/{version}/Heatmap_data/exp_pct_celltypist.pkl', 'wb') as f:
    pickle.dump(exp_pct, f)

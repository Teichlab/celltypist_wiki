# CellTypist wiki
Materials and scripts for building cell type encyclopedia table

## Generate newest json file from latest models
Make sure that the latest models are uploaded to `s3://celltypist/models/*/`. Put all shareable models in a local folder (a subset of s3 models), and run the following:  
```console
python src/generate_json_from_latest_models.py /path/to/local_model_folder
```
(Find all settings within the 'setting here' section <- no need to change in most cases)  
New json file will stay in `json/models.json`. Upload to `s3://celltypist/models/`.

## Generate encyclopedia database with tissue, dataset, and marker information
Cell types with <10 cells from a tissue-dataset combination are removed. Make sure the latest models are in `~/.celltypist/data/models/`.
```console
python src/generate_encyclopedia.py
```
(Find all settings at the top)  
The resulting table will stay in `encyclopedia/encyclopedia_table.xlsx`, and database in `encyclopedia/encyclopedia.db`.

## Generate average and percent expression for gene expression heat map
AnnData should be log-normalised first (1e4). Tissue and cell type orders are defined in the `Heatmap_data/tissue_order.txt` and `Heatmap_data/celltype_order.txt`, respectively. Currently tissue and cell type information is stored in `Tissue` and `re_harmonise_annotation` columns.  
Cell types with <=10 cells from a tissue-celltype combination are thought as non-existing (black grids in the heat map).  
(Find all settings within the 'setting here' section)
```console
python src/generate_Heatmap_data.py /path/to/adata
```
Heatmap data will stay in `Heatmap_data/exp_pct_celltypist_immune.pkl`. Upload to `s3://celltypist/Heatmap_data/`.

## Images
Images are in `images/*.png`. White background, 842 x 736 (pixels).  
Correspondence between cell type names and images is in `images/celltype_to_image.csv`.

## Other tables
`tables/Basic_celltype_information.xlsx`: free text of basic cell type information.  
`tables/celltypist_immune_meta.csv`: cell meta-information for deriving the tissue and dataset information: `adata.obs[['re_harmonise_annotation', 'Tissue', 'Dataset']].to_csv('celltypist_immune_meta.csv', header=True, index=False)`.  
`tables/dataset_to_PMID.csv`: link/paper of each data set.

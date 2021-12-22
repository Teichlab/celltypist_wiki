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
Run the following command with the atlas name (e.g. `Pan_Immune_CellTypist`).
```console
python src/generate_Heatmap_data.py an_atlas_name
```
All settings can be found in the configuration file specific to each atlas (`atlases/an_atlas_name/config/Heatmap.config`), including:
   1) `adata_path`: path to the AnnData.
   2) `tissue_column`: cell metadata column specifying tissue/organ information.
   3) `celltype_column`: cell metadata column specifying cell type information.
   4) `use_raw`: whether to use the `.raw` attribute for expression matrix in the AnnData.
   5) `filter_out`:  cell types with <=`filter_out` cells from a tissue-celltype combination are thought as non-existing (black grids in the heat map).
   6) `do_normalize`: log-normalise (to 1e4) the data if the AnnData is provided in raw counts.  
  
Tissue and cell type orders are defined in the `atlases/an_atlas_name/Heatmap_data/tissue_order.txt` and `atlases/an_atlas_name/Heatmap_data/celltype_order.txt`, respectively.  
  
Heatmap data will stay in `atlases/an_atlas_name/Heatmap_data/exp_pct_celltypist.pkl`. Upload to `s3://celltypist/Heatmap_data/an_atlas_name/`.

## Images
Images are in `images/*.png`. White background, 842 x 736 (pixels).  
  
Correspondence between cell type names and images for a given atlas is in `atlases/an_atlas_name/tables/celltype_to_image.csv`.

## Other tables
`atlases/an_atlas_name/tables/Basic_celltype_information.xlsx`: free text of basic cell type information.  
  
`atlases/an_atlas_name/tables/celltypist_meta.csv`: cell meta-information for deriving the tissue and dataset information (e.g. `adata.obs[['CellType', 'Tissue', 'Dataset']].to_csv('celltypist_meta.csv', header=True, index=False)`).  
  
`atlases/an_atlas_name/tables/dataset_to_PMID.csv`: link/paper of each data set.

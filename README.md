# CellTypist wiki
Materials and scripts for building cell type encyclopedia table

## Generate newest json file from latest models in Sanger S3
Make sure that the latest models are uploaded to `s3://celltypist/models/v6/`, and that the old json [file](https://celltypist.cog.sanger.ac.uk/models/models.json) contains matched names with the models uploaded (`filename`).
```console
python src/generate_json_from_latest_models.py
```
New json file will stay in `json/models.json`. Upload to `s3://celltypist/models/`.

## Generate encyclopedia table with tissue, dataset, and marker information
Cell types with <5 cells from a tissue-dataset combination are removed. Make sure the latest models are in `~/.celltypist/data/models/`.
```console
python src/generate_encyclopedia_table.py
```
The resulting table will stay in `encyclopedia/encyclopedia_table.xlsx`.

## Images
Images are in `images/*.png`. White background, 842 x 736 (pixels).  
Correspondence between cell type names and images is in `images/celltype_to_image.csv`.

## Other tables
`tables/Basic_celltype_information.xlsx`: free text of basic cell type information.  
`tables/celltypist_immune_meta.csv`: cell meta-information for deriving the tissue and dataset information.
`tables/dataset_to_PMID.csv`: link/paper of each data set.

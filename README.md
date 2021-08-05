# CellTypist wiki
Materials and scripts for building cell type encyclopedia table

## Generate newest json file from latest models in Sanger S3
Make sure that the latest models are uploaded to `s3://celltypist/models/v6/`, and that the old json [file](https://celltypist.cog.sanger.ac.uk/models/models.json) contains matched names with the models uploaded (`filename`).
```console
python src/generate_json_from_latest_models.py
```
New json file will stay in `json/models.json`. Upload to `s3://celltypist/models/`.

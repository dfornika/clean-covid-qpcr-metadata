# clean-covid-qpcr-metadata
Perform data cleaning on a metadata csv for COVID qPCR data

## Usage:

### Clean Metadata

The `clean_metadata.py` script expects a csv-formatted input file with the following fields:
```
containerid
second_containerid
seq_containerid
collection_date
ncov_qpcr_e_sarbeco_result
ncov_qpcr_rdrp_lee_result
ncov_qpcr_n_sarbeco_result
ncov_qpcr_n2_result
ncov_qpcr_orf1_result
```

It outputs a cleaned csv-formatted metadata file with the following fields:
```
containerid
second_containerid
seq_containerid
Ct_combo
collection_date
ncov_qpcr_e_sarbeco_result
ncov_qpcr_rdrp_lee_result
ncov_qpcr_n_sarbeco_result
ncov_qpcr_n2_result
ncov_qpcr_orf1_result
```
Note the additional `Ct_combo` field, which represents the selected Ct value of those that are available.

```
usage: clean_metadata.py [-h] all_metadata

positional arguments:
  all_metadata

optional arguments:
  -h, --help    show this help message and exit
```

### Generate ncov-tools metadata for a sequencing run

The `generate_ncov_tools_metadata_for_run.py` script takes the output from the `clean_metadata.py` script as input.
It also requires a path to a directory where fastq files are stored in directories named by illumina run ID, and
the specific illumina run ID for which the metadata file is to be prepared.

It outputs a tsv-formatted file with the following fields, which can be used as input for [ncov-tools](https://github.com/jts/ncov-tools):
```
sample
ct
date
```

```
usage: generate_ncov_tools_metadata_for_run.py [-h] [-r RUN_ID] [-f FASTQ_DIR] all_metadata_cleaned

positional arguments:
  all_metadata_cleaned

optional arguments:
  -h, --help            show this help message and exit
  -r RUN_ID, --run-id RUN_ID
  -f FASTQ_DIR, --fastq-dir FASTQ_DIR
```
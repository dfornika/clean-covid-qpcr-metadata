#!/usr/bin/env python3

import argparse
import csv
import json
import glob
import os


def select_container_id(metadata_record, library_ids):
    container_id_fields = [
        'containerid',
        'second_containerid',
        'seq_containerid',
    ]
    for field in container_id_fields:
        pass

def parse_all_metadata_cleaned(all_metadata_cleaned_path, container_id_fields):
    """
    Take a path to a 'cleaned' 'All_metadata.csv' file as input.
    Return a dict of metadata records, indexed by each of the three container ID fields.
    {
      "by_containerid": {
                          "R12345678": {"containerid": "R12345678", "second_containerid": "", "seq_containerid": "", "collection_date": "2021-10-31", ...},
                          ...
                        },
      "by_second_containerid": {
                                 "R3851945": {"containerid": "", "second_containerid": "R3851945", "seq_containerid": "", "collection_date": "2021-08-21", ...},
                                 ...
                               },
      "by_seq_containerid": {
                              "E14589235": {"containerid": "", "second_containerid": "", "seq_containerid": "E14589235", "collection_date": "2021-11-21", ...},
                            }
    }
    For each index, records are omitted if the container ID is "".
    The fields of the metadata records are:
    [
      'containerid',
      'second_containerid',
      'seq_containerid',
      'Ct_combo',
      'collection_date',
      'ncov_qpcr_e_sarbeco_result',
      'ncov_qpcr_rdrp_lee_result',
      'ncov_qpcr_n_sarbeco_result',
      'ncov_qpcr_n2_result',
      'ncov_qpcr_orf1_result,
    ]
    """

    all_metadata_cleaned = {}
    for container_id_field in container_id_fields:
        all_metadata_cleaned['by_' + container_id_field] = {}

    with open(all_metadata_cleaned_path, 'r') as f:
        reader = csv.DictReader(f, dialect='unix')
        for row in reader:
            for container_id_field in container_id_fields:
                if row[container_id_field] != "":
                    all_metadata_cleaned['by_' + container_id_field][row[container_id_field]] = row

    return all_metadata_cleaned
            

def get_library_ids_from_fastqs(fastq_dir, run_id):
    """
    Read fastq filenames in fastq_dir/run_id. Skip the 'Undetermined.fastq' files.
    Take the fastq filename up to the first underscore ('_') as the library id.
    Returns a set of all library ids for the run.
    """
    library_ids = set()
    fastq_glob = os.path.join(fastq_dir, run_id, '*_R1.fastq*')
    for fastq_path in glob.glob(fastq_glob):
        fastq_filename = os.path.basename(fastq_path)
        if not fastq_filename.startswith('Undetermined'):
            library_ids.add(fastq_filename.split('_')[0])

    return library_ids


def get_metadata_record_for_library(metadata_records, library_id, container_id_fields):
    """
    """
    selected_metadata_record = None
    output_metadata_record = None
    fastq_container_id = library_id.split('-')[0]
    indexes = ['by_' + x for x in container_id_fields]
    for index in indexes:
        if fastq_container_id in metadata_records[index]:
            selected_metadata_record = metadata_records[index][fastq_container_id]
            
    if selected_metadata_record:
        output_metadata_record = {
            'sample': library_id,
            'ct': selected_metadata_record['Ct_combo'],
            'date': selected_metadata_record['collection_date'],
        }

    return output_metadata_record


def main(args):
    container_id_fields = [
        'containerid',
        'second_containerid',
        'seq_containerid',
    ]

    output_fields = [
        'sample',
        'ct',
        'date',
    ]

    library_ids_for_run = list(sorted(get_library_ids_from_fastqs(args.fastq_dir, args.run_id)))
    all_metadata_cleaned = parse_all_metadata_cleaned(args.all_metadata_cleaned, container_id_fields)

    print('\t'.join(output_fields))

    for library_id in library_ids_for_run:
        metadata_record = get_metadata_record_for_library(all_metadata_cleaned, library_id, container_id_fields)
        if metadata_record:
            output_line = [metadata_record[x] for x in output_fields]
            print('\t'.join(output_line))
        elif library_id.startswith('NEG'):
            print('\t'.join([library_id,"0.0",""]))
        else:
            print('\t'.join([library_id,"",""]))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run-id')
    parser.add_argument('-f', '--fastq-dir')
    parser.add_argument('all_metadata_cleaned')
    args = parser.parse_args()

    main(args)

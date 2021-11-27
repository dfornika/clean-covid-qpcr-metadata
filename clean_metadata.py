#!/usr/bin/env python3

import argparse
import csv
import re


def choose_ct(metadata_record):
    """
    Select the Ct score to use for the 'Ct_combo' field in the output.
    Selection is made based on a prioritized list of available Ct scores.
    """
    ct_fields_by_priority = [
        'ncov_qpcr_e_sarbeco_result',
        'ncov_qpcr_rdrp_lee_result',
        'ncov_qpcr_n2_result',
        'ncov_qpcr_n_sarbeco_result',
        'ncov_qpcr_orf1_result',
    ]

    for f in ct_fields_by_priority:
        if f in metadata_record and metadata_record[f] != "":
            return metadata_record[f]

    return ""

def remove_zero_cts(metadata_record):
    """
    Remove any Ct score that is '0' or '0.0...'
    """
    ct_fields = [
        'ncov_qpcr_e_sarbeco_result',
        'ncov_qpcr_rdrp_lee_result',
        'ncov_qpcr_n2_result',
        'ncov_qpcr_n_sarbeco_result',
        'ncov_qpcr_orf1_result',
    ]
    for field in ct_fields:
        if re.match('0\.0+$', metadata_record[field]) or re.match('0$', metadata_record[field]):
            metadata_record[field] = ""

    return metadata_record


def handle_nonstandard_ct(ct):
    """
    Use a variety of regexes to extract the Ct value from various non-standard formats
    Also clean records that have contents that do not include a valid Ct value
    """
    parsed_ct = ct

    # These contain valid ct values with some additional chars
    pos_regexes = [
        '^(\d+)$',                                     # "36"                   -> "36"
        '\(Ct\.\s+(\d+\.\d+)\)',                       # "(Ct. 21.3)"           -> "21.3"
        '[:=-][\s+]?(\d+\.\d+)',                       # "CT=22.1"              -> "22.1", "E:20.5" -> "20.5", "SARS-CoV-2: 21.26" -> "21.26"
        '(\d+\.\d+)\s+\d+\.\d+',                       # "27.6   27.6"          -> "27.6"
        '[A-Z][:=]\d+\s+(\d+.\d+)',                    # "E=1038   10.38"       -> "10.38", "E:23083   23.83" -> "23.83"
        '[A-Z]\s+(\d+.\d+)',                           # "NAT   28.2"           -> "28.2"
        '[A-Z]+(\d+\.\d+)',                            # "EL31.13"              -> "31.33"
        '\d+\s+(\d+\.\d+)',                            # "24  24.00"            -> "24.00"
        '(\d+\.\d+)\s+[A-Za-z]+',                      # "33.21 PANTHER"        -> "33.21"
        '[A-Za-z0-9]+[:=]-?\s+(\d+\.\d+)',             # "ORF1AB: 33.1"         -> "33.1", "E:-   36.8" -> "36.8"
        '[A-Za-z0-9]+[:=]-?(\d+)$',                    # "ORF:36"               -> "36"
        '[A-Za-z0-9]+[:=]\s+(\d+)\s+[A-Za-z\(\)]+',    # "ORF1AB: 36 (PANTHER)" -> "36"
    ]

    # These contain no valid ct value. Replace with ""
    null_regexes = [
        'NEGA$',
        'EPICOV$',
        'N/A$',
        'NAT$',
        'CT[=:]?$',
        '[A-Za-z0-9]+[:=]N/A$',
        '[A-Za-z0-9]+[:=][0\-]?$',
        '[A-Za-z0-9]+[:=]NEG$',
        '-\d+$',
        '-$',
        '[A-Z]+$',
        '^[A-Za-z][A-Za-z0-9\s\(\)/]+$',
        '>\d+$',
    ]
    
    for regex in pos_regexes:
        matches = re.search(regex, ct)
        if matches:
            return matches.group(1)

    for regex in null_regexes:
        if re.match(regex, ct):
            return ""

    return parsed_ct
    

def clean_metadata_record(metadata_record):
    """
    Take a metadata record and clean it by handling non-standard Ct scores (anything not a simple floating-point number)
    Also remove any Ct score that is recorded as '0' or '0.0'
    """
    metadata_record.pop("")
    for field in metadata_record:
        metadata_record[field] = metadata_record[field].strip()
        if field.startswith('ncov_qpcr') and not re.match('\d+\.\d+$', metadata_record[field]):
            metadata_record[field] = handle_nonstandard_ct(metadata_record[field])
    metadata_record = remove_zero_cts(metadata_record)
    metadata_record['Ct_combo'] = choose_ct(metadata_record)

    return metadata_record


def print_record(metadata_record, output_fields):
    """
    Print the metadata_record, separated by comma chars, with fields in the same order as output_fields
    """
    output_line = [metadata_record[x] for x in output_fields]
    print(','.join(output_line))


def print_header(output_fields):
    """
    Print the output_fields, separated by comma chars
    """
    print(','.join(output_fields))


def main(args):

    output_fields = [
        'containerid',
        'second_containerid',
        'seq_containerid',
        'Ct_combo',
        'collection_date',
        'ncov_qpcr_e_sarbeco_result',
        'ncov_qpcr_rdrp_lee_result',
        'ncov_qpcr_n_sarbeco_result',
        'ncov_qpcr_n2_result',
        'ncov_qpcr_orf1_result'
    ]

    print_header(output_fields)

    with open(args.all_metadata, 'r') as f:
        reader = csv.DictReader(f, dialect='unix')
        for metadata_record in reader:
            cleaned_metadata_record = clean_metadata_record(metadata_record)
            try:
                print_record(cleaned_metadata_record, output_fields)
            except BrokenPipeError as e:
                exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('all_metadata')
    args = parser.parse_args()
    main(args)


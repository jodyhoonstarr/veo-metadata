#!/usr/env/bin python

from utils import read_csv, write_json


def format_detailed_occ(pretty=None):
    print("Creating detailed occupation labels")
    csv_file = '../raw/label_dod_occ_code_w_mosc.csv'
    csv_patch_file = '../raw/label_dod_occ_code.csv'
    json_file = '../out/metadata/label_dod_occ_code_detailed.json'
    json_file_rollup = '../out/metadata/label_dod_occ_code_rollup.json'

    mos_dict = {}
    occ_dict = {}

    for i, row in enumerate(read_csv(csv_file)):
        dod_id = row['dod_occ_code']
        label = row['label']
        details = "{} ({})".format(row['moc_code_label'], row['moc_code'])

        # update the mos dictionary
        if dod_id in mos_dict:
            mos_dict[dod_id] = "{}, {}".format(mos_dict[dod_id], details)
        else:
            mos_dict[dod_id] = details
        # update the occ dictionary
        if dod_id not in occ_dict:
            occ_dict[dod_id] = label

    # get all mos codes associated with the rollups e.g. 10X
    mos_rollup_dict = {}
    for mos_two in mos_dict.keys():
        if 'X' in mos_two:
            for mos_three in mos_dict.keys():
                if 'X' not in mos_three:
                    if mos_two[0:2] != mos_three[0:2]:
                        continue
                    if mos_two not in mos_rollup_dict:
                        mos_rollup_dict[mos_two] = mos_dict[mos_three]
                    else:
                        mos_rollup_dict[mos_two] = "{}, {}".format(
                            mos_rollup_dict[mos_two], mos_dict[mos_three])

    # patch the mos_dict with the updated rollup values
    for key in mos_rollup_dict.keys():
        mos_dict[key] = mos_rollup_dict[key]

    # output data
    csv_data = []
    csv_data_rollup = []

    # monkey patch the all jobs '000' rollup from the label_dod_occ_code
    for i, row in enumerate(read_csv(csv_patch_file)):
        if 'A' in row['dod_occ_code_level']:
            dod_id = row['dod_occ_code']
            label = row['label']
            csv_data.extend([{'id': dod_id, 'label': label, 'details': label}])
            csv_data_rollup.extend(
                [{'id': dod_id, 'label': label, 'details': label}])

    # fill out standard occ data
    for key in occ_dict.keys():
        if key not in mos_dict:
            print("ERROR: no mos code found for {}".format(key))
            break
        ident = key
        label = occ_dict[key]
        details = mos_dict[key]

        if 'X' not in ident:
            csv_data.extend([{'id': ident, 'label': label, 'details': details}])
        else:
            csv_data_rollup.extend(
                [{'id': ident, 'label': label, 'details': details}])

    write_json(csv_data, json_file, "labels", pretty)
    write_json(csv_data_rollup, json_file_rollup, "labels", pretty)

import argparse
import csv
import re
from collections import defaultdict

import pandas as pd
from faker import Faker

# Column names for the log file
hour_column = 'Hora'
complete_name_column = 'Nome completo'
affected_user_column = 'Usuário afetado'
event_context_column = 'Contexto do Evento'
component_column = 'Componente'
event_name_column = 'Nome do evento'
description_column = 'Descrição'
origin_column = 'Origem'
ip_address_column = 'endereço IP'

# Regular expression for finding the user ids in the logs
id_pattern = "The user with id '(-?\\d+)'"

# Fallback id for fields where no id is present
null_id = -288


# Main anonymization function
def anonymize_dataset(source_dataset_path, target_dataset_path) -> None:
    """anonymize_dataset takes the path to the dataset to anonymize and the target path for the result.

    The anonymization procedure applies pseudonymisation to the students names and id, while removing
    the origin and ip address columns, as those are unnecessary to the kind of analysis we have in mind."""
    df = pd.read_csv(source_dataset_path)
    df = suppress_columns(df)
    df = anonymize_names(df)
    df = anonymize_ids(df)
    df.to_csv(target_dataset_path, index=False, quoting=csv.QUOTE_NONE)


# Column removal
def suppress_columns(df) -> pd.DataFrame:
    """Function that suppresses unnecessary columns from the dataset"""
    df.drop([origin_column, ip_address_column], axis=1, inplace=True)
    return df


# Name anonymization
def get_fake_names(length) -> list:
    """Returns a list of fake names, to be used as substitutes to the real students names"""
    names = set()
    fake = Faker()
    while len(names) < length:
        names.add(fake.name())
    return list(names)


def anonymize_names(df) -> pd.DataFrame:
    """Function that replaces original students names with randomly created ones.

    Since we want to follow the trajectory of each student we must map each real name to the same generated one,
    so changes are consistent throughout the dataset"""
    original_names = set()
    original_names.update(df[complete_name_column].unique())
    original_names.update(df[affected_user_column].unique())
    original_names = list(original_names)
    names_dict = dict(zip(original_names, get_fake_names(len(original_names))))
    names_dict["-"] = "-"  # for non-present names in the affected user column
    df[complete_name_column] = df[complete_name_column].apply(lambda name: names_dict[name])
    df[affected_user_column] = df[affected_user_column].apply(lambda name: names_dict[name])
    return df


# ID anonymization
def get_user_id(row) -> str:
    """Searches the description column for entries with a user id, returning the found one or the fallback id"""
    pattern = re.match(id_pattern, row[description_column])
    if pattern is not None:
        return pattern.group(1)
    return str(null_id)


def replace_user_id(description, id_dict) -> str:
    """Searches for all ids inside the description field, changing their occurrences by their values on the dict"""
    for user_id in id_dict:
        description = description.replace(user_id, id_dict[user_id])
    return description


def anonymize_ids(df) -> pd.DataFrame:
    """Replaces original student ids with randomly created new ones.

    As with the students name each original id must map to the same new generated id on all occurrences
    throughout the dataset"""
    all_user_ids = df.apply(get_user_id, axis=1)
    original_ids = set()
    original_ids.update(all_user_ids.unique())
    original_ids = list(original_ids)
    ids_dict = defaultdict(lambda: str(null_id),
                           zip(original_ids, [str(x) for x in range(len(original_ids))]))
    df[description_column] = df[description_column].apply(lambda field: replace_user_id(field, ids_dict))
    return df


# Main script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Use this tool to anonymize the logs obtained from moodle, generating
                                     random names for the students and removing the origin and ip address columns''')
    parser.add_argument("source_path", help="Path to the moodle logs to anonymize")
    parser.add_argument("target_path", help="Path to save the anonymized logs")

    args = parser.parse_args()
    anonymize_dataset(args.source_path, args.target_path)

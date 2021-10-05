import argparse
import re
from random import randint

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

# Column names for the grades file
# Here we assume a column with full student name, which is not the default
# You should either change this value or create this column beforehand
grades_complete_name_column = 'Nome completo'

# Regular expression for finding the user ids in the logs
id_pattern = "The user with id '(-?\\d+)'"

# Fallback id for fields where no id is present
null_id = -288


# Main logs anonymization function
def anonymize_dataset(source_dataset_path, target_dataset_path) -> None:
    """anonymize_dataset takes the path to the dataset to anonymize and the target path for the result.

    The anonymization procedure applies pseudonymisation to the students names and id, while removing
    the origin and ip address columns, as those are unnecessary to the kind of analysis we have in mind."""
    df = pd.read_csv(source_dataset_path)
    df = suppress_columns(df)
    df = anonymize_names(df, complete_name_column, affected_user_column)
    df = anonymize_ids(df)
    df.to_csv(target_dataset_path, index=False)


# Column removal
def suppress_columns(df) -> pd.DataFrame:
    """Function that suppresses unnecessary columns from the dataset"""
    df.drop(columns=[origin_column, ip_address_column], inplace=True, errors='ignore')
    return df


# Name anonymization
def get_fake_names(length) -> list:
    """Returns a list of fake names, to be used as substitutes to the real students names"""
    names = set()
    fake = Faker()
    while len(names) < length:
        names.add(fake.name())
    return list(names)


def anonymize_names(df, *column_names) -> pd.DataFrame:
    """Function that replaces original students names with randomly created ones.

    Since we want to follow the trajectory of each student we must map each real name to the same generated one,
    so changes are consistent throughout the dataset"""
    original_names = set()
    for column in column_names:
        if column in df.columns:
            original_names.update(df[column].unique())
    original_names = list(original_names)
    if len(original_names) == 0:
        return df
    names_dict = dict(zip(original_names, get_fake_names(len(original_names))))
    names_dict["-"] = "-"  # for non-present names in the affected user column
    for column in column_names:
        if column in df.columns:
            df[column] = df[column].apply(lambda name: names_dict[name])
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
        quoted_user_id = "'{}'".format(user_id)
        # Full string specifying user id, so we don't accidentally change course id too
        user_id_description = "The user with id '{}'".format(user_id)
        if user_id_description in description:
            quoted_generated_id = "'{}'".format(id_dict[user_id])
            description = description.replace(quoted_user_id, quoted_generated_id)
            break
    return description


def anonymize_ids(df) -> pd.DataFrame:
    """Replaces original student ids with randomly created new ones.

    As with the students name each original id must map to the same new generated id on all occurrences
    throughout the dataset"""
    if description_column not in df.columns:
        return df
    all_user_ids = df.apply(get_user_id, axis=1)
    original_ids = set()
    original_ids.update(all_user_ids.unique())
    original_ids = list(original_ids)
    ids_dict = {key: str(randint(0, 99999)) for key in original_ids}
    # Leave this default/admin ids without change
    ids_dict["-1"] = "-1"
    ids_dict["0"] = "0"
    ids_dict["1"] = "1"
    ids_dict["2"] = "2"
    df[description_column] = df[description_column].apply(lambda field: replace_user_id(field, ids_dict))
    return df


# Main grades anonymization function
def anonymize_grades(source_dataset_path, target_dataset_path) -> None:
    """anonymize_grades takes the path to the dataset to anonymize and the target path for the result.

    The anonymization procedure applies pseudonymisation to the full students names, making sure the same
    mapping of real name to fake name used in the anonymization of the logs is used here."""
    df = pd.read_excel(source_dataset_path)
    df = anonymize_names(df, grades_complete_name_column)
    with pd.ExcelWriter(target_dataset_path) as writer:
        df.to_excel(writer, index=False)


# Main script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Use this tool to anonymize the logs obtained from moodle, generating
                                     random names for the students and removing the origin and ip address columns''')
    parser.add_argument("source_logs_path", help="Path to the moodle logs to anonymize")
    parser.add_argument("target_logs_path", help="Path to save the anonymized logs")
    parser.add_argument("--source_grades_path", help="Path to the moodle logs to anonymize")
    parser.add_argument("--target_grades_path", help="Path to save the anonymized logs")

    args = parser.parse_args()
    anonymize_dataset(args.source_logs_path, args.target_logs_path)

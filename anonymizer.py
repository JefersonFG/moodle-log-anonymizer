import argparse
import csv

import pandas as pd

# Column names for the log file
hour_column = 'Hora'
complete_name_column = '"Nome completo"'
affected_user_column = '"Usuário afetado"'
event_context_column = '"Contexto do Evento"'
component_column = 'Componente'
event_name_column = '"Nome do evento"'
description_column = 'Descrição'
origin_column = 'Origem'
ip_address_column = '"endereço IP"'


# Main anonymization function
def anonymize_dataset(source_dataset_path, target_dataset_path):
    """anonymize_dataset takes the path to the dataset to anonymize and the target path for the result.

    The anonymization procedure applies pseudonymisation to the students names and id, while removing
    the origin and ip address columns, as those are unnecessary to the kind of analysis we have in mind."""
    df = pd.read_csv(source_dataset_path)
    df.to_csv(target_dataset_path, index=False, quoting=csv.QUOTE_NONE)


# Main script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Use this tool to anonymize the logs obtained from moodle, generating
                                     random names for the students and removing the origin and ip address columns''')
    parser.add_argument("source_path", help="Path to the moodle logs to anonymize")
    parser.add_argument("target_path", help="Path to save the anonymized logs")

    args = parser.parse_args()
    anonymize_dataset(args.source_path, args.target_path)

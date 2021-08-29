import csv
import os
import unittest

import pandas as pd

import anonymizer


class AnonymizerTest(unittest.TestCase):
    test_dataset_path = 'test_dataset.csv'
    anonymized_dataset_path = 'anonymized_dataset.csv'

    # List of columns to be suppressed on the anonymized dataset; must be present on the test dataset
    columns_to_be_removed = ['Origem', 'endereço IP']

    # List of student names present on the test dataset, to be checked against anonymized dataset, must not be present
    student_names = ['Test name 1', 'Test name 2']

    # List of user ids present on the test dataset, to be checked against anonymized dataset, must not be present
    user_ids = ['123456', '654321']

    def setUp(self):
        """"setUp creates the test dataset with valid data"""
        df = pd.DataFrame(
            {
                'Hora': [
                    '"01/01/2001 10:00"',
                    '"01/01/2001 11:00"',
                ],
                '"Nome completo"': [
                    '"Test name 1"',
                    '"Test name 2"',
                ],
                '"Usuário afetado"': [
                    '-',
                    '"Test name 2"',
                ],
                '"Contexto do Evento"': [
                    '"Test course 1"',
                    '"Test course 1"',
                ],
                'Componente': [
                    'Tarefa',
                    'Tarefa',
                ],
                '"Nome do evento"': [
                    '"O status da submissão foi visualizado."',
                    '"Comentário visualizado"',
                ],
                'Descrição': [
                    '''"The user with id '123456' has viewed the submission status page for the assignment with course module id '000000'."''',
                    '''"The user with id '654321' viewed the feedback for the user with id '654321' for the assignment with course module id '000000'."''',
                ],
                'Origem': [
                    'test_origin',
                    'test_origin2',
                ],
                '"endereço IP"': [
                    '0.0.0.0',
                    '0.0.0.1',
                ],
            }
        )

        df.to_csv(self.test_dataset_path, index=False, quoting=csv.QUOTE_NONE)

    def tearDown(self):
        """tearDown deletes both the source and the target files to clean up after the tests"""
        if os.path.exists(self.test_dataset_path):
            os.remove(self.test_dataset_path)
        if os.path.exists(self.anonymized_dataset_path):
            os.remove(self.anonymized_dataset_path)

    def test_create_anonymized_dataset(self):
        """Tests that the anonymized dataset is created, but doesn't validate its contents"""
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        self.assertTrue(os.path.exists(self.anonymized_dataset_path), "Anonymized dataset not created")

    def test_removed_columns(self):
        """Tests columns that must be removed from the original dataset for absence on anonymized dataset"""
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        df = pd.read_csv(self.anonymized_dataset_path)
        for column in self.columns_to_be_removed:
            self.assertNotIn(column, df.columns)

    def test_anonymized_names(self):
        """Tests that the original students names cannot be found anywhere on the anonymized dataset"""
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        with open(self.anonymized_dataset_path) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                for field in row:
                    for name in self.student_names:
                        self.assertNotIn(name, field)


if __name__ == '__main__':
    unittest.main()

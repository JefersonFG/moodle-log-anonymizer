import csv
import os
import unittest

import pandas as pd

import anonymizer


class AnonymizerTest(unittest.TestCase):
    test_dataset_path = 'test_dataset.csv'
    anonymized_dataset_path = 'anonymized_dataset.csv'

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
                    '''"The user with id '000000' has viewed the submission status page for the assignment with course module id '000000'."''',
                    '''"The user with id '000000' viewed the feedback for the user with id '000000' for the assignment with course module id '000000'."''',
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
        self.assertNotIn('Origem', df.columns)
        self.assertNotIn('endereço IP', df.columns)


if __name__ == '__main__':
    unittest.main()

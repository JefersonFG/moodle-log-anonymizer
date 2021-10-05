import csv
import os
import unittest

import pandas as pd

import anonymizer


class AnonymizerTest(unittest.TestCase):
    test_dataset_path = 'test_dataset.csv'
    test_dataset_fewer_columns_path = 'test_dataset_fewer_columns.csv'
    anonymized_dataset_path = 'anonymized_dataset.csv'

    test_grades_path = 'test_grades.xlsx'
    anonymized_test_grades_path = 'anonymized_grades.xlsx'

    # List of columns to be suppressed on the anonymized dataset; must be present on the test dataset
    columns_to_be_removed = [anonymizer.origin_column, anonymizer.ip_address_column]

    # List of student names present on the test dataset, to be checked against anonymized dataset, must not be present
    student_names = ['Test name 1', 'Test name 2']

    # List of user ids present on the test dataset, to be checked against anonymized dataset, must not be present
    user_ids = ['123456', '654321']

    def setUp(self):
        """"setUp creates the test dataset with valid data"""

        # Activity logs
        df = pd.DataFrame(
            {
                'Hora': [
                    '"01/01/2001 10:00"',
                    '"01/01/2001 11:00"',
                    '"01/01/2001 12:00"',
                ],
                '"Nome completo"': [
                    '"Test name 1"',
                    '"Test name 2"',
                    'Administrador Moodle'
                ],
                '"Usuário afetado"': [
                    '-',
                    '"Test name 2"',
                    '-'
                ],
                '"Contexto do Evento"': [
                    '"Test course 1"',
                    '"Test course 1"',
                    '"Test course 2"'
                ],
                'Componente': [
                    'Tarefa',
                    'Tarefa',
                    'Lixeira'
                ],
                '"Nome do evento"': [
                    '"O status da submissão foi visualizado."',
                    '"Comentário visualizado"',
                    'Item excluído'
                ],
                'Descrição': [
                    '''"The user with id '123456' has viewed the submission status page for the assignment with course module id '000000'."''',
                    '''"The user with id '654321' viewed the feedback for the user with id '654321' for the assignment with course module id '000000'."''',
                    '''Item com ID 192837 foi excluído.'''
                ],
                'Origem': [
                    'test_origin',
                    'test_origin2',
                    'cli'
                ],
                'endereço IP': [
                    '0.0.0.0',
                    '0.0.0.1',
                    ''
                ],
            }
        )

        df.to_csv(self.test_dataset_path, index=False, quoting=csv.QUOTE_NONE)

        df.drop(columns=[anonymizer.origin_column, anonymizer.ip_address_column], inplace=True, errors='ignore')
        df.to_csv(self.test_dataset_fewer_columns_path, index=False, quoting=csv.QUOTE_NONE)

        # Grades
        # Here we assume the grades have had the name and surname columns combined into one full name column
        # We also ignore the email column, if you're editing this script you might want to test the support here
        df = pd.DataFrame(
            {
                'Nome completo': [
                    'Test name 1',
                    'Test name 2',
                    'Test name 3'
                ],
                'Tarefa 1': [
                    '10',
                    '20',
                    '30'
                ],
                'Tarefa 2': [
                    '40',
                    '50',
                    '60'
                ],
                'Tarefa 3': [
                    '70',
                    '80',
                    '90'
                ],
                'Total do curso (Real)': [
                    '50',
                    '50',
                    '50'
                ],
            }
        )

        with pd.ExcelWriter(self.test_grades_path) as writer:
            df.to_excel(writer, index=False)

    def tearDown(self):
        """tearDown deletes both the source and the target files to clean up after the tests"""
        if os.path.exists(self.test_dataset_path):
            os.remove(self.test_dataset_path)
        if os.path.exists(self.test_dataset_fewer_columns_path):
            os.remove(self.test_dataset_fewer_columns_path)
        if os.path.exists(self.anonymized_dataset_path):
            os.remove(self.anonymized_dataset_path)
        if os.path.exists(self.test_grades_path):
            os.remove(self.test_grades_path)
        if os.path.exists(self.anonymized_test_grades_path):
            os.remove(self.anonymized_test_grades_path)

    def test_create_anonymized_dataset(self):
        """Tests that the anonymized dataset is created, but doesn't validate its contents"""
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        self.assertTrue(os.path.exists(self.anonymized_dataset_path), "Anonymized dataset not created")

        # Repeat test for input with fewer columns
        anonymizer.anonymize_dataset(self.test_dataset_fewer_columns_path, self.anonymized_dataset_path)
        self.assertTrue(os.path.exists(self.anonymized_dataset_path), "Anonymized dataset not created")

    def test_removed_columns(self):
        """Tests columns that must be removed from the original dataset for absence on anonymized dataset"""
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        df = pd.read_csv(self.anonymized_dataset_path)
        for column in self.columns_to_be_removed:
            self.assertNotIn(column, df.columns)

        # Repeat test for input with fewer columns
        anonymizer.anonymize_dataset(self.test_dataset_fewer_columns_path, self.anonymized_dataset_path)
        df = pd.read_csv(self.anonymized_dataset_path)
        for column in self.columns_to_be_removed:
            self.assertNotIn(column, df.columns)

    def test_anonymized_names_and_ids(self):
        """Tests that the original students names and IDs cannot be found anywhere on the anonymized dataset"""
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        self.check_names_and_ids()

        # Repeat test for input with fewer columns
        anonymizer.anonymize_dataset(self.test_dataset_fewer_columns_path, self.anonymized_dataset_path)
        self.check_names_and_ids()

    def check_names_and_ids(self):
        """Runs after the call to the anonymization functions, searches the anonymized dataset for names and ids"""
        with open(self.anonymized_dataset_path) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                for field in row:
                    for name in self.student_names:
                        self.assertNotIn(name, field)
                    for user_id in self.user_ids:
                        self.assertNotIn(user_id, field)

    def test_create_anonymized_grades(self):
        """Tests that the anonymized grades dataset is created, but doesn't validate its contents"""
        anonymizer.anonymize_grades(self.test_grades_path, self.anonymized_test_grades_path)
        self.assertTrue(os.path.exists(self.anonymized_test_grades_path), "Anonymized dataset not created")

    def test_anonymized_names_on_grades(self):
        """Tests that the original students names and IDs cannot be found anywhere on the anonymized dataset"""
        anonymizer.anonymize_grades(self.test_grades_path, self.anonymized_test_grades_path)
        df = pd.read_excel(self.anonymized_test_grades_path)
        for name in self.student_names:
            self.assertNotIn(name, df.values)


if __name__ == '__main__':
    unittest.main()

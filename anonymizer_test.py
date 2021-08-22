import os
import unittest

import anonymizer


class AnonymizerTest(unittest.TestCase):
    test_dataset_path = 'test_dataset.csv'
    anonymized_dataset_path = 'anonymized_dataset.csv'

    def setUp(self):
        """setUp creates an example dataset file to test the anonymization procedure"""
        dataset = '''Hora,"Nome completo","Usuário afetado","Contexto do Evento",Componente,"Nome do evento",Descrição,Origem,"endereço IP"\n"01/01/2001 10:00","Test name 1","Test name 2","Test course 1",Logs,"Relatório de log visto","The user with id '000000' viewed the log report for the course with id '00000'.",test_origin,0.0.0.0'''
        with open(self.test_dataset_path, "w") as f:
            f.write(dataset)

    def tearDown(self):
        """tearDown deletes both the source and the target files to clean up after the tests"""
        if os.path.exists(self.test_dataset_path):
            os.remove(self.test_dataset_path)
        if os.path.exists(self.anonymized_dataset_path):
            os.remove(self.anonymized_dataset_path)

    def test_anonymize(self):
        anonymizer.anonymize_dataset(self.test_dataset_path, self.anonymized_dataset_path)
        self.assertTrue(os.path.exists(self.anonymized_dataset_path), "Anonymized dataset not created")


if __name__ == '__main__':
    unittest.main()

from unittest import TestCase
from nose_parameterized import parameterized
from grapher.repositories.base import Repository


class RepositoryTest(TestCase):
    def test_from_dict_of_dicts(self):
        entries = {i: {} for i in range(4)}

        result = Repository.from_dict_of_dicts(entries)

        self.assertEqual(len(result[0]), 4)
        self.assertListEqual([i for i in range(4)], result[1])

    def test_to_dict_of_dicts(self):
        entities = [{} for _ in range(4)]
        indices = [i for i in range(4)]
        result = Repository.to_dict_of_dicts(entities, indices)

        self.assertDictEqual({i:{} for i in range(4)}, result)

    def test_to_dict_of_dicts_without_indices(self):
        entities = [{} for _ in range(4)]
        result = Repository.to_dict_of_dicts(entities)

        self.assertDictEqual({i:{} for i in range(4)}, result)

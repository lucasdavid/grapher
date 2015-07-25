from py2neo import Graph

from .base.common import It, Repository


class GraphRepository(Repository):
    def __init__(self, *labels, graph=None):
        self._labels = list(labels)
        self._graph = graph

    @property
    def graph(self):
        self._graph = self._graph or Graph()
        return self._graph

    def all(self):
        pass

    def create(self, entity):
        pass

    def find(self, **kwargs):
        self.graph.find_one(self._labels[0])

    def update(self, entity):
        pass

    def delete(self, ids):
        pass

    def find_many(self, ids):
        many = It.is_iterable(ids)
        ids = It.make_iterable(ids)

        self.graph.find()

        result = []

        return It.unwrap(ids, many)

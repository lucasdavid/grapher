from datetime import datetime
from unittest import TestCase
from py2neo import Graph, Node, Relationship, authenticate


class Neo4jSanityTest(TestCase):
    def setUp(self):
        authenticate('localhost:7474', 'neo4j', 'AdmLucas107!')
        self.g = Graph()

    def test_connection(self):
        result = self.g.find('Database')

        self.assertIsNotNone(result)

    def test_write(self):
        self.g.merge('User', )
        john = Node('User', name='john')
        maria = Node('User', name='maria')

        knows = Relationship(john, 'KNOWS', maria, since=datetime.now())

        self.g.create(knows)
        self.g.delete(john, maria, knows)

    def test_delete(self):
        self.g.delete_all()

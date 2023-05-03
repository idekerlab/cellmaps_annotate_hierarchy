import unittest
from cellmaps_annotate_hierarchy.cx2_network import CX2Network


class TestCX2Network(unittest.TestCase):
    def setUp(self):
        self.cx2_network = CX2Network()

    def test_add_node(self):
        node_id1 = self.cx2_network.add_node(0, 0, {'name': 'Node 1'})
        node_id2 = self.cx2_network.add_node(50, 50, {'name': 'Node 2'})

        self.assertEqual(len(self.cx2_network.nodes), 2)
        self.assertEqual(node_id1, 1)
        self.assertEqual(node_id2, 2)

        node1 = self.cx2_network.nodes[0]
        self.assertEqual(node1['id'], 1)
        self.assertEqual(node1['x'], 0)
        self.assertEqual(node1['y'], 0)
        self.assertEqual(node1['v']['name'], 'Node 1')

        node2 = self.cx2_network.nodes[1]
        self.assertEqual(node2['id'], 2)
        self.assertEqual(node2['x'], 50)
        self.assertEqual(node2['y'], 50)
        self.assertEqual(node2['v']['name'], 'Node 2')

    def test_delete_node(self):
        node_id1 = self.cx2_network.add_node(0, 0, {'name': 'Node 1'})
        node_id2 = self.cx2_network.add_node(50, 50, {'name': 'Node 2'})
        self.cx2_network.add_edge(node_id1, node_id2, {'interaction': 'interacts with'})

        self.assertEqual(len(self.cx2_network.nodes), 2)
        self.assertEqual(len(self.cx2_network.edges), 1)

        self.cx2_network.delete_node(node_id1)
        self.assertEqual(len(self.cx2_network.nodes), 1)
        self.assertEqual(len(self.cx2_network.edges), 0)

        remaining_node = self.cx2_network.nodes[0]
        self.assertEqual(remaining_node['id'], 2)
        self.assertEqual(remaining_node['x'], 50)
        self.assertEqual(remaining_node['y'], 50)
        self.assertEqual(remaining_node['v']['name'], 'Node 2')


if __name__ == '__main__':
    unittest.main()

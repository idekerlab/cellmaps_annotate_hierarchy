class CX2Network:
    def __init__(self, cx2_data=None):
        if cx2_data is None:
            self.cx2_data = [
                {
                    "CXVersion": "2.0",
                    "hasFragments": False
                },
                {
                    "metaData": [
                        {"name": "attributeDeclarations", "elementCount": 1},
                        {"name": "networkAttributes", "elementCount": 0},
                        {"name": "edges", "elementCount": 0},
                        {"name": "nodes", "elementCount": 0}
                    ]
                },
                {
                    "attributeDeclarations": [{
                        "nodes": {},
                        "networkAttributes": {},
                        "edges": {}
                    }]
                },
                {"networkAttributes": []},
                {"nodes": []},
                {"edges": []}
            ]
        else:
            self.cx2_data = cx2_data

        self.metaData = self.cx2_data[1]["metaData"]
        self.attribute_declarations = self.cx2_data[2]["attributeDeclarations"][0]
        self.network_attributes = self.cx2_data[3]["networkAttributes"]
        self.nodes = self.cx2_data[4]["nodes"]
        self.edges = self.cx2_data[5]["edges"]

    # Other methods

    def _get_aspect(self, aspect_name):
        for aspect in self.cx2_data:
            if aspect_name in aspect:
                return aspect[aspect_name]
        return None

    def _get_data_type(self, aspect, attribute_name):
        if aspect in self.attribute_declarations[0]:
            if attribute_name in self.attribute_declarations[0][aspect]:
                return self.attribute_declarations[0][aspect][attribute_name]['d']
        return None

    def _check_data_type(self, value, data_type):
        if data_type == 'string':
            return isinstance(value, str)
        elif data_type == 'integer':
            return isinstance(value, int)
        elif data_type == 'double':
            return isinstance(value, float)
        elif data_type == 'boolean':
            return isinstance(value, bool)
        elif data_type == 'list_of_string':
            return isinstance(value, list) and all(isinstance(v, str) for v in value)
        else:
            return False

    def _update_attribute_declaration(self, aspect, attribute_name, data_type):
        if aspect not in self.attribute_declarations[0]:
            self.attribute_declarations[0][aspect] = {}
        self.attribute_declarations[0][aspect][attribute_name] = {'d': data_type}

    def get_network_attribute(self, attribute_name):
        for attribute in self.network_attributes:
            if attribute['name'] == attribute_name:
                return attribute['value']
        return None

    def set_network_attribute(self, attribute_name, value):
        data_type = self._get_data_type('networkAttributes', attribute_name)
        if data_type is None or self._check_data_type(value, data_type):
            if data_type is None:
                data_type = type(value).__name__
                self._update_attribute_declaration('networkAttributes', attribute_name, data_type)
            for attribute in self.network_attributes:
                if attribute['name'] == attribute_name:
                    attribute['value'] = value
                    return
            self.network_attributes.append({'name': attribute_name, 'value': value})

    def get_node_attribute(self, node_id, attribute_name):
        for node in self.nodes:
            if node['id'] == node_id:
                return node['v'].get(attribute_name)
        return None

    def set_node_attribute(self, node_id, attribute_name, value):
        data_type = self._get_data_type('nodes', attribute_name)
        if data_type is None or self._check_data_type(value, data_type):
            if data_type is None:
                data_type = type(value).__name__
                self._update_attribute_declaration('nodes', attribute_name, data_type)
            for node in self.nodes:
                if node['id'] == node_id:
                    node['v'][attribute_name] = value
                    return

    def get_edge_attribute(self, edge_id, attribute_name):
        for edge in self.edges:
            if edge['id'] == edge_id:
                return edge['v'].get(attribute_name)
        return None

    def set_edge_attribute(self, edge_id, attribute_name, value):
        data_type = self._get_data_type('edges', attribute_name)
        if data_type is None or self._check_data_type(value, data_type):
            if data_type is None:
                data_type = type(value).__name__
                self._update_attribute_declaration('edges', attribute_name, data_type)
            for edge in self.edges:
                if edge['id'] == edge_id:
                    edge['v'][attribute_name] = value
                    return

    def add_node(self, x, y, attributes=None):
        if attributes is None:
            attributes = {}
        node_id = max([node['id'] for node in self.nodes], default=0) + 1
        new_node = {'id': node_id, 'x': x, 'y': y, 'v': attributes}
        self.nodes.append(new_node)
        return node_id

    def delete_node(self, node_id):
        self.nodes = [node for node in self.nodes if node['id'] != node_id]
        self.edges = [edge for edge in self.edges if edge['s'] != node_id and edge['t'] != node_id]

    def add_edge(self, source_node_id, target_node_id, attributes=None):
        if attributes is None:
            attributes = {}
        source_node = None
        target_node = None
        for node in self.nodes:
            if node['id'] == source_node_id:
                source_node = node
            if node['id'] == target_node_id:
                target_node = node
            if source_node is not None and target_node is not None:
                break

        if source_node is None or target_node is None:
            raise ValueError("Source or target node ID not found in the network.")

        edge_id = max([edge['id'] for edge in self.edges], default=0) + 1
        new_edge = {'id': edge_id, 's': source_node_id, 't': target_node_id, 'v': attributes}
        self.edges.append(new_edge)
        return edge_id

    def delete_edge(self, edge_id):
        self.edges = [edge for edge in self.edges if edge['id'] != edge_id]

    def get_node_by_name(self, node_name):
        for node in self.nodes:
            if node['v'].get('name') == node_name:
                return node
        return None

    def remove_network_attribute(self, attribute_name):
        self.network_attributes = [attr for attr in self.network_attributes if attr['name'] != attribute_name]

    def remove_node_attribute(self, node_id, attribute_name):
        for node in self.nodes:
            if node['id'] == node_id and attribute_name in node['v']:
                del node['v'][attribute_name]

    def remove_edge_attribute(self, edge_id, attribute_name):
        for edge in self.edges:
            if edge['id'] == edge_id and attribute_name in edge['v']:
                del edge['v'][attribute_name]

    def remove_attribute_from_all_nodes(self, attribute_name):
        for node in self.nodes:
            if attribute_name in node['v']:
                del node['v'][attribute_name]
        if 'nodes' in self.attribute_declarations[0] and attribute_name in self.attribute_declarations[0]['nodes']:
            del self.attribute_declarations[0]['nodes'][attribute_name]

    def remove_attribute_from_all_edges(self, attribute_name):
        for edge in self.edges:
            if attribute_name in edge['v']:
                del edge['v'][attribute_name]
        if 'edges' in self.attribute_declarations[0] and attribute_name in self.attribute_declarations[0]['edges']:
            del self.attribute_declarations[0]['edges'][attribute_name]

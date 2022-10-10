from kgeditor.utils.common import login_required
from flask_restx import Resource, fields, reqparse
from . import api
from kgeditor.dao.graph import GraphDAO
from flask import abort
from arango import ArangoClient
from icecream import ic

ns = api.namespace("Graph", path="/graph", description="Graph operations")
graph = api.model(
    "Graph",
    {
        "id": fields.Integer(readonly=True, description="The graph unique identifier"),
    }
)

graph_dao = GraphDAO()

graph_parser = reqparse.RequestParser()
graph_parser.add_argument('domain', type=str)

@ns.route("/")
class GraphList(Resource):
    """Show a list of all graphs, and lets you post to add """
    @ns.doc("list_graphs")
    @ns.expect(graph_parser)
    @login_required
    def get(self):
        """list all graphs"""
        data = graph_parser.parse_args()
        domain_id = data.get('domain')
        if domain_id:
            return graph_dao.all(domain_id=domain_id)
        return graph_dao.all()

    # @ns.doc('create_graph')
    # @login_required
    # def post(self):
    #     """Create new empty graph"""
    #     req_dict = api.payload
    #     name = req_dict.get('name')
    #     domain_id = req_dict.get('domain_id')
    #     private = req_dict.get('private')
    #     if None in [name, domain_id, private]:
    #         return abort(400, "Invalid parameters.")
    #     return graph_dao.create(api.payload)   
    
    @ns.doc('create_graph')
    @login_required
    def post(self):
        """Create new empty graph"""
        # if None in [name, domain_id, private]:
        #     return abort(400, "Invalid parameters.")

        def create_graph(data, name):
            # todo 存放到mysql

            # 创建链接客户端
            client = ArangoClient(hosts='http://172.20.106.45:8529')
            # 链接数据库
            db = client.db('domain_27', username='root', password='cqu1701')

            # todo 从 mysql中获取id
            graph_dao.create(api.payload)    
            graph_id = str(graph_dao.get_graph_id(name))
            id = graph_id
            ic(id)

            graph_name = 'graph_' + id

            if db.has_graph(graph_name):
                graph = db.graph(graph_name)
            else:
                graph = db.create_graph(graph_name)

            if not graph.has_edge_definition(data['edge_name']):
                edge = graph.create_edge_definition(
                    edge_collection=data['edge_name'],
                    from_vertex_collections=data['from'],
                    to_vertex_collections=data['to']
                )
        req_dict = api.payload
        ic(req_dict)
        name = req_dict.get('name')
        # domain_id = req_dict.get('domain_id')
        # private = req_dict.get('private')
        req_dict['domain_id'] = '27'
        req_dict['private'] = True
        # from 和 to 都必须是数组
        req = {'edge_name': req_dict['relation_type'], 'from': [req_dict['e1_type']], 'to': [req_dict['e2_type']]}
        ic(req)
        create_graph(req, name)

    @ns.route("/<int:graph_id>")
    @ns.response(404, 'Graph not found')
    @ns.param('id', "The graph identifier")
    class Graph(Resource):
        """Show a single graph item and lets you delete them"""
        @ns.doc('get_graph')
        @login_required
        def post(self,graph_id):
            '''Fetch a given resource'''
            ic(api.payload)
            req_dict = api.payload
            # graph_id = req_dict.get('graph_id')
            # new_collection = req_dict.get('new_collection')
            return graph_dao.get(graph_id, api.payload)

        @ns.doc('delete_graph')
        @login_required
        def delete(self, graph_id):
            '''Delete a graph'''
            return graph_dao.delete(graph_id)

    @ns.route("/<int:graph_id>/traverse")
    class GraphTraverse(Resource):
        @ns.doc('traverse_graph')
        @login_required
        def post(self, graph_id):
            '''Fetch a given graph'''
            req_dict = api.payload
            return graph_dao.traverse(graph_id, req_dict)

    @ns.route("/<int:graph_id>/neighbor")
    class GraphNeighbor(Resource):
        @ns.doc('get_vertex_neighbor')
        @login_required
        def post(self, graph_id):
            '''Fetch a given resource'''
            req_dict = api.payload
            return graph_dao.neighbor(graph_id, req_dict)
    
    @ns.route("/<int:graph_id>/insert_triplet")
    class GraphTriplet(Resource):
        @login_required
        def post(self, graph_id):
            req_dict = api.payload
            return graph_dao.insert_triplet(graph_id, req_dict)


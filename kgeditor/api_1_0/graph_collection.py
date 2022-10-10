from . import api
from kgeditor.utils.common import login_required
from kgeditor.dao.graph_collection import CollectionDAO
from kgeditor.dao.graph import GraphDAO
from flask import abort
from flask_restx import Resource, fields, reqparse
from arango import ArangoClient
from icecream import ic

ns = api.namespace("Graph", path="/graph", description="Graph operations")

collection_dao = CollectionDAO()

@ns.route('/<int:graph_id>/<string:type>')
class CollectionList(Resource):
    ''''''
    # @ns.doc('create_graph_edge')
    @login_required
    def get(self, graph_id, type):
        '''Create a new vertex'''

        return collection_dao.get(graph_id, type)

    # @login_required
    # def post(self, graph_id, type):
    #     '''Create a new vertex'''
        
    #     req_dict = api.payload
    #     name = req_dict.get('name')
    #     if not name:
    #         return abort(400, "Invalid parameters.")
    #     return collection_dao.create(graph_id, type, api.payload)
    @login_required
    def post(self, graph_id, type):
        '''Create a new vertex'''
        def create_edge_define(data):
            graph_dao = GraphDAO()
            # 获取到的ID（能打印的ID）   
            id = graph_id
            # ic(id)

            graph_name = 'graph_' + str(id)

            # 创建链接客户端
            client = ArangoClient(hosts='http://172.20.106.45:8529')
            # 链接数据库
            db = client.db('domain_27', username='root', password='cqu1701')

            graph = db.graph(graph_name)

            vertex_all = graph.vertex_collections()


            if not graph.has_edge_definition(data['edge_name']):
                edge = graph.create_edge_definition(
                    edge_collection=data['edge_name'],
                    from_vertex_collections=vertex_all,
                    to_vertex_collections=vertex_all
                )

        req_dict = api.payload
        relation_type_name = req_dict.get('name')
        if not relation_type_name:
            return abort(400, "Invalid parameters.")
        if type == 'vertex':
            return collection_dao.create(graph_id, type, api.payload)
        else:
            data = {'edge_name': relation_type_name}
            create_edge_define(data)
            return {'message': f'Create edge collection succeed.'}, 201

# @ns.route('/<int:graph_id>/edge/<string:collection>/<edge_id>')
# class Edge(Resource):
#     @ns.doc('get_graph_edge')
#     def get(self, graph_id, collection, edge_id):
#         '''Show a graph edge and lets you delete it.'''
#         return edge_dao.get(graph_id, collection, edge_id)

#     @ns.doc('delete_graph_edge')
#     def delete(self, graph_id, collection, edge_id):
#         '''Show a graph edge and lets you delete it.'''
#         return edge_dao.delete(graph_id, collection, edge_id)

#     @ns.doc('update_graph_edge')
#     def patch(self, graph_id, collection, edge_id):
#         '''Update graph edge'''
#         req_dict = api.payload
#         new_collection = req_dict.get('relation')
#         if new_collection is None:
#             return abort(400, 'Invalid parameters.')
#         return edge_dao.update(graph_id, collection, edge_id, new_collection)
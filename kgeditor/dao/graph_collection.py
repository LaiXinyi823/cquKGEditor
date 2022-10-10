import json
import logging
from kgeditor import domain_db
from flask import abort
from pyArango.query import AQLQuery
from arango import ArangoClient
from .graph_vertex import VertexDAO
from icecream import ic
from pyArango.connection import *

vertexdao = VertexDAO()

class CollectionDAO:
    def __init__(self):
        pass

    def get(self, graph_id, type):
        if type not in ['edge', 'vertex']:
            return abort(500, 'Database error.')
        arango_conn = Connection('http://172.20.106.45:8529', username='root', password='cqu1701')
        domain_db = arango_conn['domain_27']
        db_graph = domain_db.graphs['graph_{}'.format(graph_id)]
        url = "%s/%s" % (db_graph.getURL(), type)

        try:
            r = db_graph.connection.session.get(url)        
        except Exception as e:
            logging.error(e)
            return abort(500, 'Database error.')
        if r.status_code == 200:
            data = r.json()
            return {'data':data['collections'],'message':'Fetch edge succeed.'}, 200
        return abort(500, 'Database error.')

    def create(self, graph_id, type, req):
        if type not in ['edge', 'vertex']:
            return abort(500, 'Database error.')
        arango_conn = Connection('http://172.20.106.45:8529', username='root', password='cqu1701')
        domain_db = arango_conn['domain_27']
        db_graph = domain_db.graphs['graph_{}'.format(graph_id)]
        if type == 'vertex':
            collection_type = 'Collection' 
            url = "%s/vertex" % (db_graph.getURL())

            data = { 
                    "collection" : req['name'] 
                }
        else:
            collection_type = 'Edges' 
            url = "%s/edge" % (db_graph.getURL())
            data = { 
                "collection" : req['name'], 
                "from" : req['from'], 
                "to" : req['to'] 
            }
        try:
            domain_db.createCollection(collection_type, name=req['name'])
            vertexdao.create(graph_id, req['name'], {'name':'test'})
        except Exception as e:
            logging.error(e)
            if 'already has a collection' in e.message:
                pass
            else:       
                return abort(500, 'Database error.')
        

        try:
            print(url)
            r = db_graph.connection.session.post(url, json=data)
            print(r)        
        except Exception as e:
            logging.error(e)
            return abort(500, 'Database error.')

        return {'message': f'Create {type} collection succeed.'}, 201
    
    def create_edge(self, graph_id, req):
        def create_edge_define(data):
            # 获取到的ID（能打印的ID）   
            id = graph_id
            ic(id)

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


            # if not graph.has_edge_definition(data['edge_name']):
            #     edge = graph.create_edge_definition(
            #         edge_collection=data['edge_name'],
            #         from_vertex_collections=data['from'],
            #         to_vertex_collections=data['to']
            #     )
            graph.replace_edge_definition(
                edge_collection=data['edge_name'],
                from_vertex_collections=data['from'],
                to_vertex_collections=data['to']
            )
        data = {'edge_name': req['name'],'from':req['from'],'to':req['to']}
        ic(data)
        create_edge_define(data)
        return {'message': f'Create edge collection succeed.'}, 201
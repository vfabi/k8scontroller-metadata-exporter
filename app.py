#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    @project: k8s-controller-objects-metadata
    @component: core
    @author: vfabi
    @support: vfabi
    @initial date: 2020-05-17 18:30:40
    @license: this file is subject to the terms and conditions defined
        in file 'LICENSE', which is part of this source code package
    @description
        k8s-controller-objects-metadata entrypoint application.
    @todo

    THIS FILE IS PART OF @PROJECT_NAME@ PROJECT.
    PLEASE DO NOT MODIFY THIS FILE.
"""

import os
import json
from urllib.parse import urlparse
from kubernetes import client, config, watch
from flask import Flask, jsonify, request
from application.utils import strictNamespaceMappingEnvarParse


strict_namespece_mapping = strictNamespaceMappingEnvarParse(os.getenv('STRICT_NAMESPACE_MAPPING', None))
app = Flask(__name__)
config.load_incluster_config()
v1 = client.AppsV1Api()


@app.route('/deployments/', methods=['GET'])
def deployments():
    """Get deployments meta and status data.

    Note:
        For filtering return data by namespace you have 2 options:
        1 - you can use mapping from STRICT_NAMESPACE_MAPPING env variable to strictly map request domain name to namespace. In this case
            second option will be passed.
        2 - you can use URL filter with 'namespace' argument, for example: http://www.alpha.example.com/deployments/?namespace=develop
            If request domain is specified in strict namespace mapping (STRICT_NAMESPACE_MAPPING env variable) this filtering feature won't work.
    
    Returns:
        json object:
            [
                {
                    "image": "vfabi/testapp", 
                    "image_release": "latest", 
                    "labels": {
                        "app": "testapp"
                    }, 
                    "name": "testapp", 
                    "namespace": "develop", 
                    "status": {
                        "available_replicas": 1, 
                        "ready_replicas": 1,
                        "replicas": 1, 
                        "unavailable_replicas": null, 
                        "updated_replicas": 1
                    }
                },
            ] 
    """

    data = []
    domain = urlparse(request.url_root).netloc.split(':')[0]
    deployments = v1.list_deployment_for_all_namespaces(watch=False)
    
    if strict_namespece_mapping:
        namespace = strict_namespece_mapping.get(domain, None)
        if not namespace:
            namespace = request.args.get('namespace')
    else:
        namespace = request.args.get('namespace')

    for deployment in deployments.items:
        ddata = {}

        if namespace == deployment.metadata.namespace:
            ddata['name'] = deployment.metadata.name
            ddata['namespace'] = deployment.metadata.namespace
            ddata['labels'] = deployment.metadata.labels
            configmeta = deployment.metadata.annotations.get('kubectl.kubernetes.io/last-applied-configuration', None)
            if configmeta:
                meta = json.loads(configmeta)
                spec = meta.get('spec', None)
                if spec:
                    ddata['image'] = spec['template']['spec']['containers'][0]['image'].split(':')[0]
                    ddata['image_release'] = spec['template']['spec']['containers'][0]['image'].split(':')[1]
            ddata['status'] = {
                'replicas': deployment.status.replicas,
                'available_replicas': deployment.status.available_replicas,
                'ready_replicas': deployment.status.ready_replicas,
                'unavailable_replicas': deployment.status.unavailable_replicas,
                'updated_replicas': deployment.status.updated_replicas
            }
            data.append(ddata)

        if not namespace:
            ddata['name'] = deployment.metadata.name
            ddata['namespace'] = deployment.metadata.namespace
            ddata['labels'] = deployment.metadata.labels
            configmeta = deployment.metadata.annotations.get('kubectl.kubernetes.io/last-applied-configuration', None)
            if configmeta:
                meta = json.loads(configmeta)
                spec = meta.get('spec', None)
                if spec:
                    ddata['image'] = spec['template']['spec']['containers'][0]['image'].split(':')[0]
                    ddata['image_release'] = spec['template']['spec']['containers'][0]['image'].split(':')[1]
            ddata['status'] = {
                'replicas': deployment.status.replicas,
                'available_replicas': deployment.status.available_replicas,
                'ready_replicas': deployment.status.ready_replicas,
                'unavailable_replicas': deployment.status.unavailable_replicas,
                'updated_replicas': deployment.status.updated_replicas
            }
            data.append(ddata)

    return jsonify(data)


if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=8000
    )

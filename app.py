#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    @project: k8scontroller-metadata-exporter
    @component: core
    @author: vfabi
    @support: vfabi
    @initial date: 2020-05-17 18:30:40
    @license: this file is subject to the terms and conditions defined
        in file 'LICENSE', which is part of this source code package
    @description
        k8scontroller-metadata-exporter application entrypoint.
    @todo

    THIS FILE IS PART OF @PROJECT_NAME@ PROJECT.
    PLEASE DO NOT MODIFY THIS FILE.
"""

import os
from urllib.parse import urlparse
from kubernetes import client, config, watch
from flask import Flask, jsonify, request
from application.utils import strictNamespaceMappingEnvarParse


strict_namespece_mapping = strictNamespaceMappingEnvarParse(os.getenv('STRICT_NAMESPACE_MAPPING', None))
app = Flask(__name__)
config.load_incluster_config()


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
                    "name": "testapp",
                    "namespace": "develop",
                    "images":[
                        "mcr.microsoft.com/aks/hcp/tunnel-openvpn:1.0.8",
                        "mcr.microsoft.com/aks/hcp/hcp-tunnel-front:v1.9.2-v3.0.14"
                    ],
                    "labels": {
                        "app": "testapp"
                    },
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

    api = client.AppsV1Api()
    data = []
    domain = urlparse(request.url_root).netloc.split(':')[0]

    if strict_namespece_mapping:
        namespace = strict_namespece_mapping.get(domain, None)
        if not namespace:
            namespace = request.args.get('namespace')
    else:
        namespace = request.args.get('namespace')

    try:
        deployments = api.list_deployment_for_all_namespaces(watch=False)
        for deployment in deployments.items:
            deploymentdata = {}
            deploymentdata['images'] = []
            if namespace == deployment.metadata.namespace:
                deploymentdata['name'] = deployment.metadata.name
                deploymentdata['namespace'] = deployment.metadata.namespace
                deploymentdata['labels'] = deployment.metadata.labels
                for container in deployment.spec.template.spec.containers:
                    deploymentdata['images'].append(container.image)
                deploymentdata['status'] = {
                    'replicas': deployment.status.replicas,
                    'available_replicas': deployment.status.available_replicas,
                    'ready_replicas': deployment.status.ready_replicas,
                    'unavailable_replicas': deployment.status.unavailable_replicas,
                    'updated_replicas': deployment.status.updated_replicas
                }
                data.append(deploymentdata)
            if not namespace:
                deploymentdata['name'] = deployment.metadata.name
                deploymentdata['namespace'] = deployment.metadata.namespace
                deploymentdata['labels'] = deployment.metadata.labels
                for container in deployment.spec.template.spec.containers:
                    deploymentdata['images'].append(container.image)
                deploymentdata['status'] = {
                    'replicas': deployment.status.replicas,
                    'available_replicas': deployment.status.available_replicas,
                    'ready_replicas': deployment.status.ready_replicas,
                    'unavailable_replicas': deployment.status.unavailable_replicas,
                    'updated_replicas': deployment.status.updated_replicas
                }
                data.append(deploymentdata)
        return jsonify(data)
    except Exception as e:
        response = {'error': f'Exception. Details: {e}.'}
        return jsonify(response), 500


@app.route('/pods/', methods=['GET'])
def pods():
    """Get pods meta and status data.

    Returns:
        json object:
            [
                {
                    "name": "testapp-423hag423a41-6wha",
                    "namespace": "develop",
                    "pod_ip": "1.1.1.23",
                    "node_ip": "100.100.1.84",
                    "node_name": "awshost-host-100.100.1.84",
                    "status": "Running",
                    "start_time": datetime.datetime(2020, 6, 23, 20, 30, 55, tzinfo=tzlocal()),
                    "labels": {
                        "app": "testapp",
                    },
                },
            ]
    """

    api = client.CoreV1Api()
    data = []
    domain = urlparse(request.url_root).netloc.split(':')[0]

    if strict_namespece_mapping:
        namespace = strict_namespece_mapping.get(domain, None)
        if not namespace:
            namespace = request.args.get('namespace')
    else:
        namespace = request.args.get('namespace')

    try:
        pods = api.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            poddata = {}
            if namespace == pod.metadata.namespace:
                poddata['name'] = pod.metadata.name
                poddata['pod_ip'] = pod.status.pod_ip
                poddata['node_ip'] = pod.status.host_ip
                poddata['node_name'] = pod.spec.node_name
                poddata['namespace'] = pod.metadata.namespace
                poddata['status'] = pod.status.phase
                poddata['start_time'] = pod.status.start_time
                poddata['labels'] = pod.metadata.labels
                data.append(poddata)
            if not namespace:
                poddata['name'] = pod.metadata.name
                poddata['pod_ip'] = pod.status.pod_ip
                poddata['node_ip'] = pod.status.host_ip
                poddata['node_name'] = pod.spec.node_name
                poddata['namespace'] = pod.metadata.namespace
                poddata['status'] = pod.status.phase
                poddata['start_time'] = pod.status.start_time
                poddata['labels'] = pod.metadata.labels
                data.append(poddata)
        return jsonify(data)

    except Exception as e:
        response = {'error': f'Exception. Details: {e}.'}
        return jsonify(response), 500


@app.route('/pod/logs/', methods=['GET'])
def pod_logs():
    """Get pod logs data."""

    api = client.CoreV1Api()
    domain = urlparse(request.url_root).netloc.split(':')[0]

    if strict_namespece_mapping:
        namespace = strict_namespece_mapping.get(domain, None)
        if not namespace:
            namespace = request.args.get('namespace')
        else:
            if namespace != request.args.get('namespace'):
                response = {'error': 'Access to this namespace denied. STRICT_NAMESPACE_MAPPING enabled.'}
                return jsonify(response), 400
    else:
        namespace = request.args.get('namespace')
    pod = request.args.get('pod')
    tail_lines = request.args.get('tail_lines')

    if not pod or not namespace or not tail_lines:
        response = {'error': 'Incorrect request arguments.'}
        return jsonify(response), 400

    try:
        logs = api.read_namespaced_pod_log(
            name=pod,
            namespace=namespace,
            tail_lines=int(tail_lines),
            timestamps=True
        )
        return jsonify(logs)
    except Exception as e:
        response = {'error': f'Exception. Details: {e}.'}
        return jsonify(response), 500


if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=8000
    )

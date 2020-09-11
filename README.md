# k8scontroller-metadata-exporter
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/vfabi/k8scontroller-metadata-exporter)
![GitHub last commit](https://img.shields.io/github/last-commit/vfabi/k8scontroller-metadata-exporter)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Generic badge](https://img.shields.io/badge/hub.docker.com-vfabi/k8scontroller_metadata_exporter-<>.svg)](https://hub.docker.com/repository/docker/vfabi/k8scontroller-metadata-exporter)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/vfabi/k8scontroller-metadata-exporter)
![Docker Pulls](https://img.shields.io/docker/pulls/vfabi/k8scontroller-metadata-exporter)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/vfabi/k8scontroller-metadata-exporter)

Basic Kubernetes controller to get Kubernetes objects metadata (deployments, pods, etc) and export it via HTTP API endpoint as json.  
This web application acting as proxy that **reads only** data from Kubernetes API and provides it for the other external applications as a **reads only** access point to the Kubernetes object's metadata without direct access to Kubernetes API.

## Features
- Reads Kubernetes objects metadata for all namespaces from Kubernetes API and exports it as http/json. Supported methods:  
    - deployments list
    - pods list
    - pod logs
- Strict namespace to domain mapping - allows to output only metadata from namespace mapped to specific domain.
- Data filtering by namespace key.


# Technology stack
- Python 3.6+
- Flask
- kubernetes


# Requirements and dependencies
## Application
Python libs in requirements.txt

## External
Kubernetes instance and Nginx ingress controller installed.


# Configuration
## Environment variables
| Name | Required | Values | Description |
|:----------|:-------------:|:------|:------|
|STRICT_NAMESPACE_MAPPING|False||Strict namespace to domain mapping, example: `'frontend.develop.example.com:develop,frontend.staging.example.com:staging'`|


# Usage
1. Apply Kubernetes RBAC configuration:
```
- - -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: k8scontroller-metadata-exporter
  namespace: test

- - -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  namespace: test
  name: k8scontroller-metadata-exporter
rules:
- apiGroups: ["extensions", "apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list"]
- apiGroups:
  - ""
  resources:
  - pods
  - pods/log
  verbs:
  - get
  - watch
  - list

- - -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: k8scontroller-metadata-exporter
  namespace: test
subjects:
- kind: ServiceAccount
  name: k8scontroller-metadata-exporter
  namespace: test
roleRef:
  kind: ClusterRole
  name: k8scontroller-metadata-exporter
  apiGroup: rbac.authorization.k8s.io
```

2. Apply k8scontroller-metadata-exporter K8S Deployment, Service, ConfigMap and Ingress:
```
- - -
apiVersion: v1
kind: ConfigMap
metadata:
  name: k8scontroller-metadata-exporter
  namespace: test
data:
  # No special chars and spaces for value
  STRICT_NAMESPACE_MAPPING: frontend.develop.example.com:develop,frontend.staging.example.com:staging

- - -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k8scontroller-metadata-exporter
  namespace: test
spec:
  selector:
    matchLabels:
      app: k8scontroller-metadata-exporter
  replicas: 1
  template:
    metadata:
      labels:
        app: k8scontroller-metadata-exporter
    spec:
      serviceAccountName: k8scontroller-metadata-exporter
      containers:
      - name: k8scontroller-metadata-exporter
        image: vfabi/k8scontroller-metadata-exporter:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: k8scontroller-metadata-exporter

- - -
apiVersion: v1
kind: Service
metadata:
  name: k8scontroller-metadata-exporter
  namespace: test
spec:
  type: NodePort
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  selector:
    app: k8scontroller-metadata-exporter

- - -
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: k8scontroller-metadata-exporter
  namespace: test
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
  - host: frontend.develop.example.com
    http:
      paths:
      - path: /kmeta(/|$)(.*)
        backend:
          serviceName: k8scontroller-metadata-exporter
          servicePort: 80
```

> **Note**:  
> Please change host value (frontend.develop.example.com) in the Ingress configuration to yours.  
IMPORTANT! This is a test Kubernetes configuration for k8scontroller-metadata-exporter. You should use HTTPS configuration for your Ingress.

You can access k8scontroller-metadata-exporter at http://frontend.develop.example.com/kmeta/deployments/  

### API endpoints
  - /deployments/ - get Kubernetes deployments list  
  Params, filtering (optional) example: http://frontend.develop.example.com/kmeta/deployments/?namespace=develop  
  If request domain is specified in strict namespace mapping (STRICT_NAMESPACE_MAPPING env variable) this filtering feature won't work.  

  - /pods/ - get Kubernetes pods list  
  Params, filtering (optional) example: http://frontend.develop.example.com/kmeta/pods/?namespace=develop  

  - /pod/logs/ - get Kubernetes specific pod logs  
  Params (required) example: http://frontend.develop.example.com/kmeta/pod/logs/?namespace=develop&pod=application-7fcf8df75d-pr545&tail_lines=100  

> **Note**:  
> Strict namespace mapping feature allow to map request domain only get Kubernetes objects metadata only from specified for it namespace.  
For example, you have 2 domains attached to Kubernetes frontend.develop.example.com and frontend.staging.example.com. You have configured Ingress and would like to provide access for application that serves requests at frontend.develop.example.com for Kubernetes objects metadata from develop namespace only - just put this data in STRICT_NAMESPACE_MAPPING env variable like this: `frontend.develop.example.com:develop`, or for 2 domains/namespaces: `frontend.develop.example.com:develop,frontend.staging.example.com:staging` accordingly.


# Docker
[![Generic badge](https://img.shields.io/badge/hub.docker.com-vfabi/k8scontroller_metadata_exporter-<>.svg)](https://hub.docker.com/repository/docker/vfabi/k8scontroller-metadata-exporter)


# Contributing
Please refer to each project's style and contribution guidelines for submitting patches and additions. In general, we follow the "fork-and-pull" Git workflow.

 1. **Fork** the repo on GitHub
 2. **Clone** the project to your own machine
 3. **Commit** changes to your own branch
 4. **Push** your work back up to your fork
 5. Submit a **Pull request** so that we can review your changes

NOTE: Be sure to merge the latest from "upstream" before making a pull request!


# License
Apache 2.0
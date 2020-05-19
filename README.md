# k8s-controller-objects-metadata
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/vfabi/k8s-controller-objects-metadata)
![GitHub last commit](https://img.shields.io/github/last-commit/vfabi/k8s-controller-objects-metadata)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Generic badge](https://img.shields.io/badge/hub.docker.com-vfabi/k8s_controller_objects_metadata-<>.svg)](https://hub.docker.com/repository/docker/vfabi/k8s-controller-objects-metadata)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/vfabi/k8s-controller-objects-metadata)
![Docker Pulls](https://img.shields.io/docker/pulls/vfabi/k8s-controller-objects-metadata)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/vfabi/k8s-controller-objects-metadata)

K8S controller to get metadata from K8S objects (deployments, pods, etc) and outputs it as http/json.  
This web application acting as proxy that only reads K8S API data and provides it for the other applications as secure access to K8S object's metadata without direct access to K8S API.

## Features
- read K8S objects metadata for all namespaces from K8S API
- outputs metadata for K8S deployment objects as http/json
- strict namespace to domain mapping (ouptuts only metadata mapped to specific domain)
- filtering by namespace


# Status
Pre-production


# Technology stack
- Python 3.6+
- Flask - web framework
- kubernetes - kubernetes client


# Requirements and dependencies
## Application
Python libs requirements in requirements.txt

## External
K8S instance


# Configuration
## Environment variables
| Name | Required | Values | Description |
|----------|:-------------:|------:|------:|
|STRICT_NAMESPACE_MAPPING|False||strict namespace to domain mapping, example: `frontend.develop.example.com:develop,frontend.staging.example.com:staging`|


# Usage
- Apply K8S RBAC configuration:
```
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: k8s-controller-objects-metadata
  namespace: test

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  namespace: test
  name: k8s-controller-objects-metadata
rules:
- apiGroups: ["extensions", "apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: k8s-controller-objects-metadata
  namespace: test
subjects:
- kind: ServiceAccount
  name: k8s-controller-objects-metadata
  namespace: test
roleRef:
  kind: ClusterRole
  name: k8s-controller-objects-metadata
  apiGroup: rbac.authorization.k8s.io
```
- Apply k8s-controller-objects-metadata K8S Deployment, Service and ConfigMap:
```
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: k8s-controller-objects-metadata
  namespace: test
data:
  # No special chars and spaces for value
  STRICT_NAMESPACE_MAPPING: frontend.develop.example.com:develop,frontend.staging.example.com:staging

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k8s-controller-objects-metadata
  namespace: test
spec:
  selector:
    matchLabels:
      app: k8s-controller-objects-metadata
  replicas: 1
  template:
    metadata:
      labels:
        app: k8s-controller-objects-metadata
    spec:
      serviceAccountName: k8s-controller-objects-metadata
      containers:
      - name: k8s-controller-objects-metadata
        image: vfabi/k8s-controller-objects-metadata:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: k8s-controller-objects-metadata

---
apiVersion: v1
kind: Service
metadata:
  name: k8s-controller-objects-metadata
  namespace: test
spec:
  type: NodePort
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  selector:
    app: k8s-controller-objects-metadata
```

Use K8S configuration to reach k8s-controller-objects-metadata service  
For example http://100.100.100.23/deployments/  
Endpoints:
  - /deployments/ - for K8S deployments objects  
  Filtering: http://100.100.100.23/deployments/?namespace=develop.  
  Note: if request domain is specified in strict namespace mapping (STRICT_NAMESPACE_MAPPING env variable) this filtering feature won't work.  

Strict namespace mapping feature allow to map request domain only get K8S objects metadata only from specified for it namespace.  
For example you have 2 domains attached to K8S frontend.develop.example.com and frontend.staging.example.com. You have configured ingress (or other K8S solution) and would like to provide access for application that serves requests at frontend.develop.example.com only for K8S objects metadata from develop namespace - just put this data in STRICT_NAMESPACE_MAPPING env variable `frontend.develop.example.com:develop` or for 2 domains `frontend.develop.example.com:develop,frontend.staging.example.com:staging` accordingly.


# Docker
[![Generic badge](https://img.shields.io/badge/hub.docker.com-vfabi/k8s_controller_objects_metadata-<>.svg)](https://hub.docker.com/repository/docker/vfabi/k8s-controller-objects-metadata)  
Build: `docker build -t k8s-controller-objects-metadata:latest -f ./deploy/Dockerfile .`


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
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    @project: k8s-controller-objects-metadata
    @component: core
    @author: vfabi
    @contact person: vfabi
    @support: vfabi
    @inital date: 2020-05-17 18:30:40
    @license: this file is subject to the terms and conditions defined
        in file 'LICENSE', which is part of this source code package
    @description
        Small utils.
    @todo

    THIS FILE IS PART OF @PROJECT_NAME@ PROJECT.
    PLEASE DO NOT MODIFY THIS FILE.
"""

def strictNamespaceMappingEnvarParse(envar=None):
    """Custom format STRICT_NAMESPACE_MAPPING env variable parsing.

    Note:
        STRICT_NAMESPACE_MAPPING value example: 'frontend.develop.example.com:develop,frontend.staging.example.com:staging'
        No spaces or special chars.
    """
    if envar:                                                                                                                                                    
        items = envar.split(',')                                                                                                                                                                                                                       
        mapdict = {}                                                                                                                                                                                                                                      
        for item in items:                                                                                                                                                                                                                             
            mapdict[item.split(':')[0]] = item.split(':')[1]
        return mapdict
    return None

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'


def get_all_subclasses():
    from dayu_ffmpeg.network import AbstractNode, AbstractEdge, AbstractKnob
    from collections import deque
    queue = deque()
    result = {}
    queue.append(AbstractNode)
    while queue:
        current = queue.popleft()
        result[current.type] = current
        queue.extend(current.__subclasses__())
    queue.append(AbstractEdge)
    while queue:
        current = queue.popleft()
        result[current.type] = current
        queue.extend(current.__subclasses__())
    queue.append(AbstractKnob)
    while queue:
        current = queue.popleft()
        result[current.type] = current
        queue.extend(current.__subclasses__())
    return result


ALL_SUBCLASSES = get_all_subclasses()


def save_script(root_node, ffscript_path):
    import json
    with open(ffscript_path, 'w') as f:
        json.dump(root_node.to_script(), f, encoding='utf-8', indent=4)


def parse_ffscript_data(object):
    if isinstance(object, dict):
        class_type = ALL_SUBCLASSES.get(object.get('type', None), None)
        if class_type:
            instance = class_type.from_script(object)
            return instance

    return object


def relink_nodes(node, parent=None):
    from dayu_ffmpeg.network import BaseGroupNode
    node.parent = parent
    if isinstance(node, BaseGroupNode):
        for n in node.inside_nodes:
            relink_nodes(n, node)


def relink_edges(node, parent=None):
    from dayu_ffmpeg.network import BaseGroupNode, TwoEndPoints

    lookup_node = {n.id: n for n in parent.inside_nodes} if parent else {}
    for i, e in enumerate(node.in_edges):
        if e:
            left = lookup_node.get(e.endpoints.left, None)
            right = lookup_node.get(e.endpoints.right, None)
            if left and right:
                node.in_edges[i].endpoints = TwoEndPoints(left, right)
            else:
                node.in_edges[i] = None

    if isinstance(node, BaseGroupNode):
        for n in node.inside_nodes:
            relink_edges(n, node)


def relink_knobs(node, all_nodes=None):
    if all_nodes is None:
        all_nodes = {n.id: n for n in node.traverse_children(recursive=True)}
        all_nodes[node.id] = node

    for n in all_nodes.values():
        for k in n.knobs:
            if k:
                k.parent = all_nodes.get(k.parent, None)
                k.link = all_nodes.get(k.link, None)


def open_script(ffscipt_path):
    import json
    data = None
    with open(ffscipt_path, 'r') as f:
        data = json.load(f)

    root = parse_ffscript_data(data)
    relink_nodes(root, None)
    relink_edges(root, None)
    relink_knobs(root)

    return root

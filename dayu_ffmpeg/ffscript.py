#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from network import AbstractNode, AbstractEdge


def get_all_subclasses():
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
    return result


ALL_SUBCLASSES = get_all_subclasses()


def save_script(root_node, ffscript_path):
    import json
    with open(ffscript_path, 'w') as f:
        json.dump(root_node.to_script(), f, encoding='utf-8', indent=4)


def _parse_ffscript_data(object):
    if object is None:
        return object

    class_type = ALL_SUBCLASSES.get(object['type'], None)
    instance = class_type.from_script(object)
    return instance


def open_script(ffscipt_path):
    import json
    data = None
    with open(ffscipt_path, 'r') as f:
        data = json.load(f)

    root = _parse_ffscript_data(data)
    return root


if __name__ == '__main__':
    from network import *

    i1 = Input()
    root = RootNode()
    ih1 = root.create_node(InputHolder)
    root.set_input(i1)
    i2 = root.create_node(Input)
    cf = root.create_node(ComplexFilterGroup)
    ih2 = cf.create_node(InputHolder)
    ih3 = cf.create_node(InputHolder)
    cf.set_input(ih1, 0)
    cf.set_input(i2, 1)
    over = cf.create_node(Overlay)
    over.set_input(ih2, 0)
    over.set_input(ih3, 1)
    oh1 = cf.create_node(OutputHolder)
    oh1.set_input(over)
    o1 = root.create_node(Output)
    o1.set_input(cf)

    from pprint import pprint

    # pprint(ALL_SUBCLASSES)
    root = open_script('/Users/andyguo/Desktop/basic.txt')
    pprint(root.__dict__)
    print root.id

    # pprint(root.to_script())
    # save_script(root, '/Users/andyguo/Desktop/basic.txt')

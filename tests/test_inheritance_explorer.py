import pytest

from inheritance_explorer.inheritance_explorer import ChildNode, ClassGraphTree
from inheritance_explorer._testing import ClassForTesting
import collections
import pydot

def test_child():
    child_class = ChildNode
    node = ChildNode(child_class, 1)
    assert(type(node.child_id) == str)


def test_class_graph():

    # map out the structure of SimilarityContainer, track the run method
    cgt = ClassGraphTree(ClassForTesting, "use_this_func")
    assert(cgt._node_list[1].parent_id == "1")
    c = cgt.check_source_similarity()
    assert(isinstance(c, collections.OrderedDict))
    assert(c[3].similarity_fraction < 1.0)

    # make sure the graph builds
    for in_sim in [True, False]:
        cgt = ClassGraphTree(ClassForTesting, "use_this_func")
        cgt.build_graph(include_similarity=in_sim)
        assert isinstance(cgt.graph, pydot.Dot)
    cgt = ClassGraphTree(ClassForTesting, "use_this_func")
    cgt.build_graph(graph_type="graph")
    assert isinstance(cgt.graph, pydot.Dot)


def test_class_graph_no_function():
    cgt = ClassGraphTree(ClassForTesting)
    assert (cgt._node_list[1].parent_id == "1")


def test_source_code_return():
    cgt = ClassGraphTree(ClassForTesting, funcname="use_this_func")

    for node in ['ClassForTesting', 'ClassForTesting2', 'ClassForTesting4']:
        assert isinstance(cgt.get_source_code(node), str)

        node_id = cgt._node_map_r[node]
        assert isinstance(cgt.get_source_code(node_id), str)


    with pytest.raises(ValueError, match="does not override the chosen"):
        _ = cgt.get_source_code('ClassForTesting3')
        _ = cgt.get_source_code(cgt._node_map_r['ClassForTesting3'])


    with pytest.raises(KeyError, match="Could not find node"):
        _ = cgt.get_source_code(10)


def test_multi_source_code():
    cgt = ClassGraphTree(ClassForTesting, funcname="use_this_func")

    test_classes = ["ClassForTesting", "ClassForTesting2", "ClassForTesting4"]
    src_dict = cgt.get_multiple_source_code(test_classes[0],
                                            test_classes[1],
                                            test_classes[2])
    assert len(src_dict) == len(test_classes)
    for src_key in test_classes:
        assert src_key in src_dict

    src_dict_nodes = [cgt._node_map_r[c] for c in test_classes]
    src_dict = cgt.get_multiple_source_code(src_dict_nodes[0], *src_dict_nodes[1:])
    assert len(src_dict) == len(test_classes)

    with pytest.raises(ValueError, match="does not override the chosen"):
        _ = cgt.get_multiple_source_code('ClassForTesting', 'ClassForTesting3')

    with pytest.raises(KeyError, match="Could not find node"):
        _ = cgt.get_multiple_source_code('ClassForTesting', 10)

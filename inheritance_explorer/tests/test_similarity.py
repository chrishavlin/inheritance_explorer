from collections import OrderedDict

import numpy as np
import pytest

from inheritance_explorer.similarity import PycodeSimilarity, ResultsContainer


@pytest.fixture
def sample_source_dict():
    test_source = "def test_func(a, b, c):\n" "    return a * b * c"
    test_source2 = "def test_func(a, b, c):\n" "    a = a * 10\n" "    return a * b * c"
    test_source3 = "def test_func(a, b, c):\n" "    a = a * b\n" "    return a * b * c"
    source_dict = OrderedDict()
    source_dict[0] = test_source
    source_dict[1] = test_source
    source_dict[2] = test_source2
    source_dict[3] = test_source
    source_dict[4] = test_source3

    N = len(source_dict)
    s_matrix = np.ones((N, N))
    s_matrix[2, 0] = 0
    s_matrix[4, 0] = 0
    s_matrix[2, 1] = 0
    s_matrix[4, 1] = 0
    s_matrix[0:2, 2] = 0
    s_matrix[3:, 2] = 0
    s_matrix[2, 3] = 0
    s_matrix[4, 3] = 0
    s_matrix[0:4, 4] = 0

    return source_dict, s_matrix.astype(bool)


def test_pycode_similarity_single_ref(sample_source_dict):

    s_dict, s_matrix = sample_source_dict
    ref = 0
    p = PycodeSimilarity()
    results = p.run(s_dict, reference=ref)
    s_bool = dict(zip(s_dict.keys(), s_matrix[:, 0]))

    for key, _ in s_dict.items():
        if key != ref:
            assert key in results
            f = results[key]
            assert isinstance(f, ResultsContainer)
            if s_bool[key]:
                assert f.similarity_fraction == 1.0
            else:
                assert f.similarity_fraction < 1.0


def test_pycode_similarity_permuted(sample_source_dict):

    s_dict, s_bool = sample_source_dict
    p = PycodeSimilarity(method="permute")
    _, sim_matrix, sim_axis = p.run(s_dict)

    assert isinstance(sim_matrix, np.ndarray)
    assert sim_matrix.shape == s_bool.shape

    bool_matrix = sim_matrix.astype(int).astype(bool)
    assert np.all(bool_matrix == s_bool)

    assert isinstance(sim_axis, tuple)
    assert len(sim_axis) == len(s_dict)
    for k in s_dict.keys():
        assert k in sim_axis


def test_errors():
    with pytest.raises(ValueError, match="Provided method not recognized"):
        _ = PycodeSimilarity(method="badmethod")

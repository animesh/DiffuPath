# -*- coding: utf-8 -*-

"""Sanity checks for input."""

# TODO
# .check_method
# .check_metric

# Check scores sanity
import networkx as nx
import numpy as np

from diffupy.matrix import Matrix
from diffupy.miscellaneous import get_label_list_graph


def _validate_scores(scores: Matrix) -> None:
    """Check scores sanity: Ensures that scores are suitable for diffusion."""


    #  Check labels list
    if not scores.cols_labels:
        raise ValueError("Scores must be a named list but supplied list contains no names.")
    if not scores.rows_labels:
        raise ValueError("Scores must be a named list but supplied list contains no names.")

    #  Check numpy array values type
    if not 'float' and 'int' in str(scores.mat.dtype):
        raise ValueError("The scores in background are not numeric.")

    #  Check each matrix element
    for score, col_label, row_label in iter(scores):
        #  Validate scores
        if score is None:
            raise ValueError("Scores input cannot contain None.")
        elif score is ['NA', 'Nan', 'nan']:
            raise ValueError("Scores input cannot contain NA values.")
        elif not isinstance(score, float) and not isinstance(score, int):
            raise ValueError("The scores in background are not numeric.")

        #  Validate labels
        if col_label in ['Nan', None]:
            raise ValueError("The scores in background must have row names according to the scored nodes.")
        if row_label in ['Nan', None]:
            raise ValueError("The scores in background must have col names to differentiate score sets.")

    std_mat = Matrix(np.std(scores.mat, axis=0), ['sd'], scores.cols_labels)

    for sd, col_label, row_label in iter(std_mat):
        if sd in ['Nan', None]:
            raise ValueError("Standard deviation in background is NA in column:" + str(col_label))
        if sd == 0:
            raise ValueError("Standard deviation in background is 0 in column:" + str(col_label))


def _validate_graph(graph: nx.Graph) -> None:
    """Check graph sanity: Ensures that 'graph' is a valid NetworkX Graph object."""

    if graph in [None, 'NA', 'Nan']:
        raise ValueError("'graph' missing")

    if not isinstance(graph, nx.Graph):
        raise ValueError("'graph' must be an NetworkX graph object")

    nodes_names = get_label_list_graph(graph, 'name')
    if nodes_names in [None, 'NA', 'Nan']:
        raise ValueError("'graph' must have node names.")

    if any(nodes_names) is None:
        raise ValueError("'graph' cannot have NA as node names")

    if len(np.unique(nodes_names)) != len(nodes_names):
        raise ValueError("'graph' has non-unique names! Please check that the names are unique.")

    if nx.is_directed(graph):
        raise Warning("graph' should be an undirected NetworkX graph object.")

    edge_weights = nx.get_edge_attributes(graph, 'weight')
    if edge_weights:
        if any(edge_weights) is None:
            raise ValueError("'graph' cannot contain NA edge weights, all must have weights.")
        if any(edge_weights) < 0:
            raise Warning("'graph' should not contain negative edge weights.")


def _validate_K(k: Matrix) -> None:
    """Check kernel sanity: Ensures that 'k' is a formally valid kernel. Does not check for spd"""

    if not isinstance(k, Matrix):
        raise ValueError("'k' must be a matrix")

    # Check numeric type.
    if not 'float' and 'int' in str(k.mat.dtype):
        raise ValueError("'k' must be a numeric matrix, but it is not numeric.")

    n_rows = k.mat.shape[0]
    n_cols = k.mat.shape[1]
    if n_rows != n_cols:
        raise ValueError(
            "'k' must be a square matrix, but it has " + str(n_rows) + " rows and " + str(n_cols) + " columns.")

    if k.cols_labels == []:
        raise ValueError("'k' kernel must have row names.")

    if k.rows_labels == []:
        raise ValueError("'k' kernel must have column names.")

    if k.rows_labels != k.cols_labels:
        raise ValueError("'k' rownames and colnames must coincide.")

    for score, col_label, row_label in iter(k):
        if not isinstance(score, float) and not isinstance(score, int):
            raise ValueError("'k' must be a numeric matrix, but it is not numeric.")

        if score in ['Nan', None]:
            raise ValueError("Scores input cannot contain NA. But background .")

        if col_label in ['Nan', None] or row_label in ['Nan', None]:
            raise ValueError("'k' dimnames cannot be NA.")

    if len(np.unique(k.rows_labels)) != len(k.rows_labels):
        raise ValueError("'k' cannot contain duplicated row names.")

    if len(np.unique(k.cols_labels)) != len(k.cols_labels):
        raise ValueError("'k' cannot contain duplicated column names.")

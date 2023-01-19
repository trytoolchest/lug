import lug
import pytest
import numpy as np
import sklearn.linear_model


@lug.run(
    image="alpine:3.16.2",
    remote=True,
    serialize_dependencies=True,
)
def sklearn_getting_started():
    reg = sklearn.linear_model.LinearRegression()
    reg.fit([[0, 0], [1, 1], [2, 2]], [0, 1, 2])
    return reg.coef_


@pytest.mark.integration
def test_sklearn_getting_started():
    result = sklearn_getting_started()
    assert np.allclose(np.array([0.5, 0.5]), result)

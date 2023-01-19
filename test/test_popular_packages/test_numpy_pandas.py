import lug
import numpy as np
import pandas as pd
import pytest


@lug.run(
    image="alpine:3.16.2",
    remote=True,
    serialize_dependencies=True,
)
def pandas_getting_started():
    return pd.Series([1, 3, 5, np.nan, 6, 8])


@pytest.mark.integration
def test_pandas_getting_started():
    result = pandas_getting_started()
    assert result.equals(pd.Series([1, 3, 5, np.nan, 6, 8]))

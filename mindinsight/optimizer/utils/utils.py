# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Utils for optimizer."""
import numpy as np

_DEFAULT_HISTOGRAM_BINS = 5


def calc_histogram(np_value: np.ndarray, bins=_DEFAULT_HISTOGRAM_BINS):
    """
    Calculates histogram.

    This is a simple wrapper around the error-prone np.histogram() to improve robustness.
    """
    ma_value = np.ma.masked_invalid(np_value)

    valid_cnt = ma_value.count()
    if not valid_cnt:
        max_val = 0
        min_val = 0
    else:
        # Note that max of a masked array with dtype np.float16 returns inf (numpy issue#15077).
        if np.issubdtype(np_value.dtype, np.floating):
            max_val = ma_value.max(fill_value=np.NINF)
            min_val = ma_value.min(fill_value=np.PINF)
        else:
            max_val = ma_value.max()
            min_val = ma_value.min()

    range_left = min_val
    range_right = max_val

    if range_left >= range_right:
        range_left -= 0.5
        range_right += 0.5

    with np.errstate(invalid='ignore'):
        # if don't ignore state above, when np.nan exists,
        # it will occur RuntimeWarning: invalid value encountered in less_equal
        counts, edges = np.histogram(np_value, bins=bins, range=(range_left, range_right))

    histogram_bins = [None] * len(counts)
    for ind, count in enumerate(counts):
        histogram_bins[ind] = [float(edges[ind]), float(edges[ind + 1] - edges[ind]), float(count)]

    return histogram_bins


def is_simple_numpy_number(dtype):
    """Verify if it is simple number."""
    if np.issubdtype(dtype, np.integer):
        return True

    if np.issubdtype(dtype, np.floating):
        return True

    return False
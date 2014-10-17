# -*- coding: utf-8 -*-

import numpy as np
import pytest


@pytest.fixture
def shift():
    return np.array([1., 5., 7.])


@pytest.fixture
def data():
    return np.arange(100).reshape(10, 10)


@pytest.fixture
def metadata(data):
    shift = np.zeros(data.shape[1])
    clouds = np.zeros(data.shape[1])
    airmass = np.ones(data.shape[1])
    ccdx = np.ones(data.shape[1]) * 1024
    ccdy = np.ones(data.shape[1]) * 1024

    return data, (shift, clouds, airmass, ccdx, ccdy)


def test_low_shift_index(shift):
    from qa_common.filter_objects import low_shift_index
    assert (low_shift_index(shift) == np.array([True, False, False])).all()


def test_low_shift_index_change_shift_pofnt(shift):
    from qa_common.filter_objects import low_shift_index
    assert (low_shift_index(shift, initial_bad_shift_point=10) ==
            np.array([True, True, True])).all()


def test_good_measurement_indices_all_good(metadata):
    from qa_common.filter_objects import good_measurement_indices
    data = metadata[0]
    per_object, per_image = good_measurement_indices(*metadata[1])
    assert np.all(per_object) & np.all(per_image)

def test_bad_images(metadata):
    from qa_common.filter_objects import good_measurement_indices
    data, conditions = metadata
    index = data.shape[1] / 2
    conditions[0][index] = 100.

    per_object, per_image = good_measurement_indices(*conditions)

    expected = np.ones_like(per_image, dtype=bool)
    expected[index] = False
    assert np.all(per_object) & (per_image == expected).all()

def test_bad_objects(metadata):
    from qa_common.filter_objects import good_measurement_indices
    data, conditions = metadata
    index = data.shape[1] / 2
    conditions[3][index] = -50.0

    per_object, per_image = good_measurement_indices(*conditions)

    expected = np.ones_like(per_object, dtype=bool)
    expected[index] = False
    assert np.all(per_image) & (per_object == expected).all()


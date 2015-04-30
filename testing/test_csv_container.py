import pytest
import csv
import numpy as np
import sys
sys.path.insert(0, '.')


def test_csv_container_sort_my_mjd(tmpdir):
    from qa_common.csv_container import CSVContainer
    outfile_name = tmpdir.join('data.csv')
    with open(str(outfile_name), 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['mjd', 'value'])
        writer.writeheader()

        mjd = [1, 5, 2]
        value = [1, 2, 3]

        for (a, b) in zip(mjd, value):
            writer.writerow({'mjd': a, 'value': b})

    container = CSVContainer.from_filename(str(outfile_name))

    assert np.all(container.mjd == [1, 2, 5]) and np.all(container.value == [1, 3, 2])


def test_no_mjd(tmpdir):
    from qa_common.csv_container import CSVContainer
    outfile_name = tmpdir.join('data.csv')
    with open(str(outfile_name), 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['time', 'value'])
        writer.writeheader()

        time = [1, 5, 2]
        value = [1, 2, 3]

        for (a, b) in zip(time, value):
            writer.writerow({'time': a, 'value': b})

    container = CSVContainer.from_filename(str(outfile_name))
    assert (np.all(container.time == [1, 5, 2]) and
            np.all(container.value == [1, 2, 3]))

    container = CSVContainer.from_filename(str(outfile_name), sort_key='time')
    assert (np.all(container.time == [1, 2, 5]) and
            np.all(container.value == [1, 3, 2]))

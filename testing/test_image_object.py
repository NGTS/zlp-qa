import sys
sys.path.insert(0, 'view')
import build_html as b
import pytest
from collections import defaultdict


@pytest.mark.parametrize('filename,title',
                         [('/tmp/01_test.png', 'Test'),
                          ('/tmp/01_test_another_thing.png', 'Test another thing'),])
def test_image_title(filename, title):
    assert b.Image(filename).title == title


@pytest.mark.parametrize('filename,anchor',
                         [('/tmp/01_test.png', 'test'),
                          ('/tmp/01_test_another_thing.png', 'test-another-thing'),])
def test_image_anchor(filename, anchor):
    assert b.Image(filename).anchor == anchor


def test_multiple_same_anchors():
    files = ['/tmp/01-test.png', '/tmp/02-test.png', '/tmp/03-test.png']
    b.Image.counter = defaultdict(int)
    anchors = [b.Image(filename).anchor for filename in files]
    assert anchors == ['test', 'test-01', 'test-02']

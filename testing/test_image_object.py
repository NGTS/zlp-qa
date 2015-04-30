import sys
sys.path.insert(0, 'view')
import build_html as b
import pytest


@pytest.mark.parametrize('filename,title',
                         [('/tmp/01_test.png', 'Test'),
                          ('/tmp/01_test_another_thing.png', 'Test another thing'),])
def test_image_title(filename, title):
    assert b.Image(filename).title == title

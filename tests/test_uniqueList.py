import pytest
from dayu_ffmpeg.network.node.base import UniqueList

class TestUniqueList(object):
    def test_append(self):
        a = UniqueList()
        a.append(1)
        assert len(a) == 1 and a[0] == 1
        a.append(1)
        assert len(a) == 1 and a[0] == 1
        a.append(2)
        assert len(a) == 2 and a[0] == 1 and a[1] == 2
        a.append(None)
        assert len(a) == 3 and a[0] == 1 and a[1] == 2 and a[2] == None
        a.append(None)
        assert len(a) == 4 and a[0] == 1 and a[1] == 2 and a[2] == None and a[3] == None

    def test_extend(self):
        a = UniqueList()
        a.extend([1,2])
        assert len(a) == 2 and a[0] == 1 and a[1] == 2
        a.extend([1,2])
        assert len(a) == 2 and a[0] == 1 and a[1] == 2
        a.extend([2,3])
        assert len(a) == 3 and a[0] == 1 and a[1] == 2 and a[2] == 3
        a.extend([None, None])
        assert len(a) == 5 and a[0] == 1 and a[1] == 2 and a[2] == 3 and a[3] is None and a[4] is None

    def test_insert(self):
        a = UniqueList([1,2])
        assert len(a) == 2 and a[0] == 1 and a[1] == 2
        a.insert(0, 0)
        assert len(a) == 3 and a[0] == 0 and a[1] == 1 and a[2] == 2
        a.insert(1, 1)
        assert len(a) == 3 and a[0] == 0 and a[1] == 1 and a[2] == 2
        a.insert(2, 1)
        assert len(a) == 3 and a[0] == 0 and a[1] == 1 and a[2] == 2
        a.insert(0, None)
        assert len(a) == 4 and a[0] == None and a[1] == 0 and a[2] == 1 and a[3] == 2

    def test_remove(self):
        a = UniqueList([1,2,3])
        a.remove(3)
        assert len(a) == 2 and a[0] == 1 and a[1] == 2
        try:
            a.remove(6)
        except:
            pytest.fail()




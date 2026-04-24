from repocompare.compare import compare_packages


def test_compare_basic():
    a = {'pkg1': '1.0', 'pkg2': '2.0'}
    b = {'pkg2': '2.0', 'pkg3': '3.0'}
    res = compare_packages(a, b)
    assert 'pkg3' in res['missing_in_a']
    assert 'pkg1' in res['missing_in_b']
    assert any(item['package'] == 'pkg2' for item in res['same_versions'])

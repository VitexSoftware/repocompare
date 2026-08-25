from repocompare.compare import compare_packages, normalize_version


def test_compare_basic():
    a = {'pkg1': '1.0', 'pkg2': '2.0'}
    b = {'pkg2': '2.0', 'pkg3': '3.0'}
    res = compare_packages(a, b)
    assert 'pkg3' in res['missing_in_a']
    assert 'pkg1' in res['missing_in_b']
    assert any(item['package'] == 'pkg2' for item in res['same_versions'])


def test_compare_ignores_build_number():
    a = {'abraflexi-cashier': '0.1.0.87~trixie'}
    b = {'abraflexi-cashier': '0.1.0.22~trixie'}
    res = compare_packages(a, b)
    assert res['different_versions'] == []
    assert any(item['package'] == 'abraflexi-cashier' for item in res['same_versions'])


def test_compare_still_flags_real_differences():
    a = {'abraflexi-cashier': '0.1.0.87~trixie'}
    b = {'abraflexi-cashier': '0.2.0.22~trixie'}
    res = compare_packages(a, b)
    assert any(item['package'] == 'abraflexi-cashier' for item in res['different_versions'])
    assert res['same_versions'] == []


def test_normalize_version():
    assert normalize_version('2.12.0.152~trixie') == '2.12.0~trixie'
    assert normalize_version('1.0.0') == '1.0.0'
    assert normalize_version(None) is None
    assert normalize_version('') == ''

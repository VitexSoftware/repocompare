from repocompare.parser import parse_packages_text


def test_parse_packages_sample():
    text = open('tests/fixtures/Packages.sample', 'r', encoding='utf-8').read()
    mapping = parse_packages_text(text)
    assert mapping['samplepkg'] == '1.0.0'
    assert mapping['otherpkg'] == '2.3.4'

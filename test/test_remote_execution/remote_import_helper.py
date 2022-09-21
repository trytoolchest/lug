import idna


def encode_an_example_string():
    """Encodes an example string via the idna (non-stdlib) module.
    Expected output is the bytestring b'xn--eckwd4c7c.xn--zckzah'.
    """
    return idna.encode('ドメイン.テスト')

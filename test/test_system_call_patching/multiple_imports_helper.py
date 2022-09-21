import math

import idna


def function_that_uses_imported_modules(x):
    return int(math.pi * x), idna.encode('ドメイン.テスト')

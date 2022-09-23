import sys

STDLIB_MODULE_NAMES = set()

if sys.version_info.minor >= 10:
    # sys.stdlib_module_names is only available post Python 3.10
    STDLIB_MODULE_NAMES = sys.stdlib_module_names
else:
    # This is the result of sys.stdlib_module_names in Python 3.10. It's not exact, but we don't need it to be – it's
    # used to skip over builtins when deciding which pickle-by-values to skip.
    STDLIB_MODULE_NAMES = frozenset(
        {'subprocess', '_lzma', '_codecs_jp', '_multiprocessing', '_contextvars', 'keyword', '_posixsubprocess', '_bz2',
         'pkgutil', '_signal', 'tkinter', '_winapi', 'html', 'pprint', 'resource', 'trace', 'doctest', 'grp',
         'symtable', 'tracemalloc', 'http', 'contextvars', 'dis', 'logging', 'modulefinder', 'builtins', 'idlelib',
         'tty', '_sha512', 'typing', '_ast', 'reprlib', 'tempfile', 'plistlib', 'fcntl', '_tkinter', '_compat_pickle',
         'codeop', 'gc', 'cgitb', '_json', 'gzip', 'random', 'errno', '_bootsubprocess', 'bdb', 'bisect', 'sndhdr',
         '_codecs_tw', 'ntpath', '_thread', 'contextlib', 'faulthandler', 'socket', 'crypt', 'types', 'zipapp',
         'poplib', '_socket', 'hmac', 'nis', 'runpy', 'traceback', '_codecs_cn', 'msvcrt', 'stat', '_locale',
         'winsound', '_multibytecodec', 'queue', 'sunau', 'py_compile', 'sys', 'cProfile', 'configparser', '_msi',
         'profile', '_decimal', 'fractions', 'rlcompleter', 'shutil', 'mimetypes', 'aifc', 'sqlite3', 'uuid', '_heapq',
         'zipimport', 'zoneinfo', 'msilib', 'copyreg', 'string', 'calendar', 'chunk', '_collections_abc', '_scproxy',
         'zlib', 'asynchat', 'multiprocessing', 'operator', '_stat', '_abc', 'pickle', 'functools', 'distutils',
         'asyncore', '_crypt', 'cgi', '_sqlite3', 'graphlib', 'timeit', '_weakref', 'opcode', 'io', 'tabnanny',
         '_strptime', 'pyexpat', 'codecs', 'genericpath', '_threading_local', 'stringprep', 'tarfile', '_hashlib',
         'enum', 'webbrowser', 'platform', 'atexit', '_operator', 'telnetlib', 'sre_constants', 'ast', 'spwd',
         '_frozen_importlib_external', '_sre', 'pwd', 'dataclasses', 'pyclbr', '_osx_support', 'termios', 'token',
         'mailbox', 'wave', 'itertools', 'audioop', 'bz2', 'json', 'tokenize', '_datetime', 'collections', '_py_abc',
         'numbers', 'encodings', 'concurrent', 'csv', 'selectors', 'turtle', 'urllib', '_codecs', 'dbm', 'xdrlib',
         'sched', 'winreg', 'imp', '_sha3', 'smtplib', 'antigravity', 'socketserver', '_collections', 'difflib',
         'netrc', 'ensurepip', '_curses', 'sre_parse', '_frozen_importlib', '_ssl', '_queue', 'binhex', 'code',
         'quopri', '_curses_panel', '_warnings', 'secrets', 'time', 'warnings', 'posix', 'curses', 'pipes',
         '_elementtree', 'pydoc_data', 'readline', 'smtpd', '_aix_support', 'struct', 'this', 'lib2to3', 'xml',
         'ossaudiodev', 'glob', 'select', '_codecs_kr', '_dbm', '_random', '_functools', 'cmd', 'compileall', '_io',
         'wsgiref', '_ctypes', 'abc', 'ctypes', 'email', 'fnmatch', 'ftplib', 'optparse', 'ipaddress', '_zoneinfo',
         'venv', '_lsprof', 'gettext', '_string', 'asyncio', '_codecs_hk', 'syslog', '_tracemalloc', '_compression',
         '_markupbase', 'mailcap', '_asyncio', 'unicodedata', 'shlex', 'ssl', '_sha256', '_md5', 'base64', 'inspect',
         'sysconfig', '_bisect', 'unittest', 'statistics', 'hashlib', 'array', 'pty', '_sitebuiltins', '_symtable',
         'datetime', 'signal', 'textwrap', 'turtledemo', 'posixpath', 'weakref', '_weakrefset', 'pdb', '_sha1',
         'pstats', 'filecmp', 'threading', '_gdbm', 'cmath', 'locale', '_pickle', 'decimal', 'site', 'uu', 'zipfile',
         'imaplib', '_blake2', 'nturl2path', 'pydoc', '_csv', '_statistics', 'copy', 'shelve', '_pydecimal', '_struct',
         'colorsys', '_posixshmem', 'mmap', 're', 'os', 'linecache', 'math', '_uuid', 'xmlrpc', '_codecs_iso2022',
         '__future__', '_pyio', 'nntplib', 'binascii', 'getopt', '_imp', 'marshal', '_opcode', 'imghdr', 'heapq',
         'importlib', 'nt', 'pathlib', '_overlapped', 'pickletools', 'getpass', 'lzma', 'sre_compile', 'fileinput',
         'argparse'})

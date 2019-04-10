Description
===========
vsc-install provides shared setuptools functions and classes for python libraries developed by UGent's HPC group

Common pitfalls
=========
bdist_rpm will fail if your install_requires = 'setuptools' because it will fail to find a setuptools rpm.
```
export VSC_RPM_PYTHON=1
```
will make sure the `python-` prefix is added to the packages in install_requires for building RPM's so python-setuptools will be used.

Add tests
=========

Test are python modules in the `test` directory which have subclass of `TestCase`
and at least one method that has a name starting with `test_`

You are advised to use
```python
from vsc.install.testing import TestCase
```
(instead of basic `TestCase` from `unittest`).

And any `__main__` or `suite()` is not needed (anymore).

Initialise the test directory with

```bash
mkdir -p test
echo '' > test/__init__.py
echo 'from vsc.install.commontest import CommonTest' > test/00-import.py
```

When the tests are run, `test`, `lib` and `bin` (if relevant) are added to `sys.path`,
so no need to do so in the tets modules.

Run tests
=========

```bash
python setup.py test
```

Filter tests with `-F` (test module names) and `-f` (test method names)

See also

```bash
python setup.py test --help
```

The dependencies are installed automatically in the `.eggs` directory. It will first try
`github.ugent.be` and then `github.com` to install them. The same method is used as through
which the original repository was cloned (http, ssh, ...). In case you need private
dependencies, always clone with ssh.

In case following error occurs, it means there is a test module `XYZ` that cannot be imported.

```txt
File "setup.py", line 499, in loadTestsFromModule
    testsuites = ScanningLoader.loadTestsFromModule(self, module)
File "build/bdist.linux-x86_64/egg/setuptools/command/test.py", line 37, in loadTestsFromModule
File "/usr/lib64/python2.7/unittest/loader.py", line 100, in loadTestsFromName
    parent, obj = obj, getattr(obj, part)
AttributeError: 'module' object has no attribute 'XYZ'
```

You can try get the actual import error for fixing the issue with
```bash
python -c 'import sys;sys.path.insert(0, "test");import XYZ;'
```

Fix failing tests
=================

* Missing / incorrect `LICENSE`

 * Copy the appropirate license file under `known_licenses` in the project directory and name the file `LICENSE`

* Missing `README.md`

 * Create a `README.md` file with at least a `Description` section

* Fix license headers as described in https://github.com/hpcugent/vsc-install/blob/master/lib/vsc/install/headers.py

  ```
  cd <project dir with .git folder>
  REPO_BASE_DIR=$PWD python -m vsc.install.headers path/to/file script_or_not
  ```

  Fix them all at once using find

  ```
  find ./{lib,test} -type f -name '*.py' | REPO_BASE_DIR=$PWD xargs -I '{}' python -m vsc.install.headers '{}'
  find ./bin -type f -name '*.py' | REPO_BASE_DIR=$PWD xargs -I '{}' python -m vsc.install.headers '{}' 1
  ```

  Do not forget to check the diff.
  Modules/scripts without docstring (or magic comment '### END OF HEADER') (incl. test modules)
  will get correct header appended to existing one. Add a docstring (or magic comment) to resolve this.
* Python scripts (i.e. with a python shebang and installed as scripts in setup) have to use `#!/usr/bin/env python` as shebang
* Remove any `build_rpms_settings.sh` leftovers
* The `TARGET` dict in `setup.py` should be minimal unless you really know what you are doing (i.e. if it is truly different from defaults)

 * Remove `name`, `scripts`, ...

* `Exception: vsc namespace packages do not allow non-shared namespace`

 * Add to the `__init__.py`

 ```python
 """
 Allow other packages to extend this namespace, zip safe setuptools style
 """
 import pkg_resources
 pkg_resources.declare_namespace(__name__)
 ```


bare-except
-----------
```python
try:
   # something
except:
```
This is bad, because this except will also catch sys.exit() or Keyboardinterupts, something you
typically do not want, if you catch these the program will be in a weird state and then continue on,
whilst the person who just pressed ctrl+c is wondering what is going on and why it is not stopping.

so at the very least make this
except Exception (which doesn't catch sys.exit and KeyboardInterupt)
and it would be appreciated if you could actually figure out what exceptions to expect and only catch those
and let your program crash if something you did not intend happens
because it helps developers catch weird errors on their side better.

if you do something like
```python
try:
    open(int(somestring)).write('important data')
except Exception:
    pass # if somestring is not an integer, we didn't need to write anyway, but otherwise we do
```
because you know sometimes this string does not contain an integer, so the int() call can fail
you should really only catch ValueError, because this will also fail when your disk is full, or you don't have permissions
or xxx other reasons, and the important data will not be written out and nobody will notice anything!



if not 'a' in somelist -> if 'a' not in somelist
-------------------------------------------------

this isn't that big of a deal, but if everyone is consistent it's less likely to introduce bugs when a not is added or removed where it didn't need to.
Also helps code review, not in reads better, like english.


arguments-differ
-----------------

this will give you errors if you override a function of a superclass but don't use the same amount of arguments,
using less will surely give you errors, so the linter catches this for you now

unused-argument
-----------------
if you have a function definition witch accepts an argument that is never used in the function body this will now give an error.
clean up your function definition, or fix the error where you actually do need to take this argument into account

unused-variable
----------------
defining a variable and then not using it anymore smells bad, why did you do that?
sometimes you do things like
```python
out, exit_code = run_command(something)
```
but you are not interested in the out, only in the exit code,
in this case, write
```python
_, exit_code = run_command(something)
```

using _ as a variable name lets pylint and other readers know you do not intend to use that output in the first place.


reimported
-------------
when you re import a name somewhere else,
usually this is just an import to much, or 2 imports with the same name, pay attention.
```python
import six
from django import six
```
=>
```python
import six
from django import six as django_six
```

redefinition of unused name
----------------------------
this usually also points to something you did not expect
```python
from vsc.accountpageclient import VscGroup
<snip>

class VscGroup(object):
    pass
```

=> do you need the import? use import as
did you mean to use the same name? ...

Redefined builtin
-----------------
use different name, for example change

```python
def filter(b_b):
    """Function filter"""
    return b_b
```
=>
```python
def new_filter(b_b):
    """Function filter"""
    return b_b
```

Fix Python 3 failing tests
==========================

* We try to follow https://docs.python.org/3/howto/pyporting.html
* some useful info can be found here as well https://portingguide.readthedocs.io/en/latest/index.html

unpacking-in-except / redefine-in-handler
-----------------------------------------

Multiple exception have to be grouped in a tuple like

```python
    ...
except (ExceptionOne, ExceptionTwo) ...
    ...
```

(espcially when used like `except A, B:` which should be `except (A, B):`.

Fixing print statement
----------------------

Use the oneliner:
```bash
find lib bin -name '*.py' | xargs futurize -w -f libfuturize.fixes.fix_print_with_import -n
```
Note: You need to install `python(2)-future` if you want to use `futurize` (or you have to have the `future` Python package).

Metaclass assignment
--------------------

```python
class Foo(Bar):

    __metaclass__ = Baz
```
=>
```python
from future.utils import with_metaclass

class Foo(with_metaclass(Baz,Bar):
```

Old raise syntax
----------------
Python 2’s **raise** statement was designed at a time when exceptions weren’t classes, and an exception’s _type_, _value_, and _traceback_ components were three separate objects. In Python 3, one single object includes all information about an exception.

```python
raise NameError, "Error"
```
=>
```python
raise NameError("Error")
```

or change
```python
raise NameError, "Error", some_traceback
```
=>
```python
raise NameError("Error")

e = NameError("Error")
e.__traceback__ = some_traceback
```

backtick
--------

```python
A = 2
B = `A`
```
=>
```python
A = 2
B = str(A)
```

Old ne operator
---------------

```python
if 2 <> 3:
```
=>
```python
if 2 != 3:
```

Octal literal
-------------

```python
os.chmod(foo, 0700)
```
=>
```python
os.chmod(foo, 0o700)
```

Import star module level
------------------------
Do not import \*, be more specific. If it is impossible, import it in the top level (and suppress the pyflakes error F403.)
```python
def coords(angle, distance):
    """Function coords"""
    from math import *
    return distance * cos(angle), distance * sin(angle)
```
=>
```python
from math import *  # noqa: F403
def coords(angle, distance):
    """Function coords"""
    return distance * cos(angle), distance * sin(angle)
```

Raising string
--------------
```python
raise ValueError, 'message'
```
=>
```python
raise ValueError('message')
```

Indexing exception
------------------
```python
except IndexError as err:
    err[0]
```
=>
```python
except IndexError as err:
    IndexError.args[0]
```

turning off these errors
-------------------------

If in any of these cases you think: yes, I really needed to do this,
I'm monkeypatching things, I'm adding extra functionality that does indeed have an extra(default) paramenter, etc, etc
you can let pylint know to ignore this error in this one specific block of code
by adding e.g. the comment `# pylint: disable=<name or numeric id of pylint code>`

```python
class Something(object):
    def dosomething(self, some, thing):
        # do something

class MyFancyThing(SomeThing):
    # pylint: disable=arguments-differ
    def dosomething(self, some, thing, fancy=None):
         # do something fancy
```

Full list with all codes is available at http://pylint-messages.wikidot.com/all-codes

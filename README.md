# TagStr

Tagged template literals for Python.

This project seeks to implement an [early stage PEP][tagstr-pep] for adding "tag
strings", also known as [tagged template literals][tagged-template-literals], using
[import hooks][import-hook-pep]. Tag strings, are a natural extension of
[f-strings][fstr-pep] which enable Python developers to create custom string
interpolation logic.

# Installation

```bash
$ pip install tagstr
```

# At a Glance

Here's a simple hello world example:

```python
# tagstr: on
name = "world"
print @ f"Hello, {name!r}!"
```

In the code above, `print` is knows as a "tag function", `@` is the "tag operator",
`f"Hello, {name!r}!"` is the "tag string", and `name` is one of its interpolated values:

```python
print @ f"Hello, {name!r}!"
# │   │  │         └── interpolated value
# │   │  │
# │   |  └── tag string
# │   │
# │   └── tag operator
# │
# └── tag function
```

When run, the example above prints:

```
Hello,  (<function <lambda> at 0x7f918e063380>, 'name', 'r', None) !
```

This happens because `tagstr` sees the `tagstr: on` comment and rewrites it as:

```python
# tagstr: on
name = "world"
print("Hello, ", (lambda: name, "name", "r", None), "!")
```

Not that the tag function (in this case `print`) gains access to the original string as
well as a tuple with information about the interpolated `{name!r}` called a
["thunk"][thunk]. In particular, this thunk contains a lambda for lazily retrieving that
value.

# Examples

While the example above isn't especially useful,

<!--
Link References
===============
-->

[tagstr-pep]: https://github.com/jimbaker/tagstr
[fstr-pep]: https://peps.python.org/pep-0498/
[tagged-template-literals]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates
[import-hook-pep]: https://peps.python.org/pep-0302/
[thunk]: https://en.wikipedia.org/wiki/Thunk

| Changes |
|---------|
| Name    |


# Changes
Give a previous code example:
```python
# module: new.py
def new() -> None:
    return 1

# module: hello.py
from new import new


def hello() -> None:
    while True:
        print(new())
```

# Checklist:

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] New and existing unit tests pass locally with my changes

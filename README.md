# PyMyGekko

Python Library to access the myGEKKO Query API.

[![PyPI - Version](https://img.shields.io/pypi/v/pymygekko.svg)](https://pypi.org/project/pymygekko)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymygekko.svg)](https://pypi.org/project/pymygekko)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install pymygekko
```

## Usage

```python
from aiohttp import ClientSession

from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.Lights import LightState

async with ClientSession() as session:
    api = MyGekkoApiClient(
        "USERNAME",
        "APIKEY",
        "GEKKOID",
        session,
    )

    await api.read_data()

    # Read lights
    lights = api.get_lights()
    # assuming there is a light...
    await lights[0].set_state(LightState.ON)
```

## License

`pymygekko` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

---

[buymecoffee]: https://www.buymeacoffee.com/stephanu
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge

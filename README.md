# Convex Contracts

![](https://github.com/DEX-Company/convex-contracts/workflows/testing/badge.svg)
[![GitHub contributors](https://img.shields.io/github/contributors/DEX-Company/convex-contracts.svg)](https://github.com/DEX-Company/convex-contracts/graphs/contributors)

---


## Maintainers

 [Developer Dex team][developer@dex.sg]

## Deploy Contracts

To deploy contracts you need to run the `./tools/convex_contract_tool.py`.

```bash

./tools/convex_contract_tool.py --keyword="secret keywords you get from a private store which is not stored in git" deploy

```

## Contract owner address

**Contract owner address: 0x1de659d38a129e2358cd3c4af906bc5ee48b33f27915539897f9fd66813e2beb**

## Contract Names

+   starfish-ddo-registry
+   starfish-provenance

## Getting contract addresses

Using the convex api to get the contract address based on the contract name and owner address.

```python
    # Example to get the starfish-ddo-registry address
    convex = ConvexAPI('https://convex.world')
    starfish_ddo_contract_address = convex.get_address('starfish-ddo-registry', '0x1de659d38a129e2358cd3c4af906bc5ee48b33f27915539897f9fd66813e2beb')
```

## License

```
Copyright 2018-2020 DEX Pte. Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

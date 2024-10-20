# Logical Reasoning-Enhanced Interactive Clustering: An Efficient Algorithm for Large-Scale Datasets

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Datasets](#datasets)
- [Usage](#usage)
- [Related Efforts](#related-efforts)
- [Contact](#contact)
- [License](#license)

## Background

To address the challenges of high user involvement and low time efficiency in handling large datasets, we propose an
enhanced interactive clustering algorithm called LR-COBRAS, which integrates logical reasoning. By applying logical
rules, the algorithm autonomously infers new relationships between data points from user-provided constraints,
significantly reducing the need for user interaction. Furthermore, LR-COBRAS introduces a dynamic super-instance
refinement process and custom data structures to adaptively adjust clustering granularity, enhancing flexibility,
accuracy, and overall time efficiency. Extensive experiments on benchmarks such as CIFAR100, ImageNet, and UCI datasets
demonstrate that LR-COBRAS not only reduces user interaction but also significantly improves query efficiency and time
efficiency while maintaining high clustering quality. This work presents a novel approach that leverages logical
reasoning to optimize interactive clustering, particularly for complex and large-scale datasets.The source code for our
implementation is available on https://github.com/cjw-bbxc/LR-COBRAS.

## Install

We are using Python 3, and for specific environment configuration, please refer to `environment.yml`. Additionally, for
using Prolog, we are utilizing SWI-Prolog. Due to version differences, please follow the guidance on the official
website for downloading and installation.

## Datasets

Caltech 256: https://www.kaggle.com/datasets/jessicali9530/caltech256

CIFAR100: https://www.kaggle.com/datasets/melikechan/cifar100/data

ImageNet: https://www.kaggle.com/datasets/lijiyu/imagenet

## Usage

After installing and configuring all environments, please use the following command to run the program example

```shell
cobras_ts --visual --images datasets/test-cufar
```

## Related Efforts

Original COBRAS code: https://github.com/ML-KULeuven/cobras

## Contact

If you have any questions, feel free to raise an issue or contact me at my email: lkx.bbxc@gmail.com.

## License

[MIT](LICENSE)

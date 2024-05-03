# Installation and basic usage

## Local installation

BoNesis requires [Python](https://www.python.org) ≥ 3.9.

### Installation using pip

```
pip install bonesis
```

### Installation Using conda

```
conda install -c potassco -c colomoto bonesis
```

## Docker and online versions

BoNesis is shipped with the [CoLoMoTo Docker distribution](https://colomoto.org/notebook), which provides a pre-installed Jupyter notebook environment together with many tools related to modeling, simulation, and analysis of Boolean networks. See prior link for usage instructions.

You can try BoNesis without any installation on https://mybinder.org/v2/gh/colomoto/colomoto-docker/mybinder/latest, thanks to myBinder services.
Note that the computing resources are limited and the storage is not persistent.

## Main usage

BoNesis is primarily a Python module, named `bonesis`, intended to be used in scripts and
notebooks.

For a first glance at BoNesis features, see [](../tutorials/tour.md) and [](overview.md).


## Command-line tools

Alongside the Python API, the following command-line tools are provided. Use `--help` option for usage detail.

`bonesis-reprogramming`
: Marker reprogramming of minimal trap spaces (attractors of most permissive dynamics).

    *Example.* identifying permanent reprogramming strategies involving at most 3
    combined mutations to enforce that all attractors (minimal trap spaces) have
    components `PhA` fixed to 1 and `PhB` fixed to 0.
    ```shell
    $ bonesis-reprogramming model.bnet '{"PhA": 1, "PhB": 0}' 3
    ```

    See `bonesis-reprogramming --help` for complete documentation.

`bonesis-attractors`
: Listing of fixed points and minimal trap spaces from ensembles of Boolean networks: a configuration or subspace is outputted if there exists at least one Boolean network in the ensemble for which it is a minimal trap space.

    *Example*
    ```shell
    $ bonesis-attractors partial_bn.aeon
    ```

    See `bonesis-attractors --help` for complete documentation.

    ```{note}
    For enumerating fixed points or minimal trap spaces of a *single* Boolean
    network, it is much more efficient to use [`mpbn`](https://mpbn.readthedocs.io/).
    ```

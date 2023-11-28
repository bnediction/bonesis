# BoNesis - Boolean Network synthesis

Synthesis of Most Permissive Boolean Networks from network architecture and dynamical properties

This software is distributed under the [CeCILL v2.1](http://www.cecill.info/index.en.html) free software license (GNU GPL compatible).

## Main related publications

### Synthesis/Inference

* **Synthesis of Boolean Networks from Biological Dynamical Constraints using Answer-Set Programming** (S Chevalier, C Froidevaux, L Paulevé, A Zinovyev). *In 2019 IEEE 31st International Conference on Tools with Artificial Intelligence (ICTAI), 34–41. Portland, Oregon, United States, 2019. IEEE.* [doi:10.1109/ICTAI.2019.00014](https://doi.org/10.1109/ICTAI.2019.00014)
*  **Synthesis and Simulation of Ensembles of Boolean Networks for Cell Fate Decision** (S Chevalier, V Noël, L Calzone, A Zinovyev, L Paulevé) *In 18th International Conference on Computational Methods in Systems Biology (CMSB). Online, Germany, 2020.* Preprint at https://hal.archives-ouvertes.fr/hal-02898849/file/cmsb2020.pdf

### Control/Reprogramming

* **Tackling universal properties of minimal trap spaces of Boolean networks**
  (S Riva, J-M Lagniez, G Magaña López, L Paulevé), *CMSB*, 2023 [doi:10.1007/978-3-031-42697-1_11](https://doi.org/10.1007/978-3-031-42697-1_11) [arXiv:2305.02442](http://arxiv.org/abs/2305.02442)
* **Marker and source-marker reprogramming of Most Permissive Boolean networks and ensembles with BoNesis** (L Paulevé), *Peer Community Journal*, 2023
[doi:10.24072/pcjournal.255](https://doi.org/10.24072/pcjournal.255)

## Installation

### Using pip
```
pip install bonesis
```

### Using conda
```
conda install -c potassco -c colomoto bonesis
```

## Usage

### Python API

- [Tutorial](https://nbviewer.org/github/bnediction/bonesis/blob/master/examples/Tutorial.ipynb)

### Command line tools

* `bonesis-reprogramming`: marker reprogramming of minimal trap spaces (attractors of most permissive dynamics)
* `bonesis-attractors`: listing of minimal trap spaces (MP attractors) from ensembles of BNs

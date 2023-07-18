# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_UtilClasses.ipynb.

# %% auto 0
__all__ = ['InnerConfig', 'OuterConfig', 'InnerResults', 'OuterResults']

# %% ../nbs/02_UtilClasses.ipynb 3
from dataclasses import dataclass

# %% ../nbs/02_UtilClasses.ipynb 4
@dataclass
class InnerConfig:
    test_train_split: float
    input_dim: int
    output_dim: int
    hidden_layer_sizes: list
    batch_size: int
    epochs: int
    lr: float
    mu: float
    n_fns: int
    l2_reg: float
    seed: int
    base_act: str = 'sin'


# %% ../nbs/02_UtilClasses.ipynb 5
@dataclass
class OuterConfig:
    input_dim: int
    output_dim: int
    hidden_layer_sizes: list
    batch_size: int
    steps: int
    print_every: int
    lr: float
    mu: float
    seed: int

# %% ../nbs/02_UtilClasses.ipynb 6
@dataclass
class InnerResults:
    """
    dataclass to store inner loop results
    """
    train_loss: list
    test_loss: list
    grad_norm: list


# %% ../nbs/02_UtilClasses.ipynb 7
@dataclass
class OuterResults:
    """
    dataclass to store outer loop results
    """
    inner_test_loss: list
    train_loss: list
    inner_afuncs: list
    grad_norm: list

# jaxDiversity

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

![CI](https://github.com/NonlinearArtificialIntelligenceLab/jaxDiversity/actions/workflows/test.yaml/badge.svg)
![Docs](https://github.com/NonlinearArtificialIntelligenceLab/jaxDiversity/actions/workflows/deploy.yaml/badge.svg)

This is an updated implementation for Neural networks embrace diversity
paper

## Authors

Anshul Choudhary, Anil Radhakrishnan, John F. Lindner, Sudeshna Sinha,
and William L. Ditto

## Link to paper

- [arXiv](https://arxiv.org/abs/2204.04348)

## Key Results

- We construct neural networks with learnable activation functions and
  sere that they quickly diversify from each other under training.
- These activations subsequently outperform their *pure* counterparts on
  classification tasks.
- The neuronal sub-networks instantiate the neurons and meta-learning
  adjusts their weights and biases to find efficient spanning sets of
  nonlinear activations.
- These improved neural networks provide quantitative examples of the
  emergence of diversity and insight into its advantages.

## Install

``` sh
pip install jaxDiversity
```

## How to use

The codebase has 4 main components: \* dataloading: Contains tools for
loading the datasets mentioned in the manuscript. We use pytorch
dataloaders with a custom numpy collate function to use this data in
jax.

- losses: We handle both traditional mlps and hamiltonian neural
  networkss with minimal changes with our loss implementations.

- mlp: Contains custom mlp that takes in multiple activations and uses
  them *intralayer* to create a diverse network. Also contains the
  activation neural networks.

- loops: Contains the inner and outer loops for metalearning to optimize
  the activation functions in tandem with the supervised learning task

### Minimum example

``` python
import jax
import optax

from jaxDiversity.utilclasses import (
    InnerConfig,
    OuterConfig,
)  # simple utility classes for configuration consistency
from jaxDiversity.dataloading import NumpyLoader, DummyDataset
from jaxDiversity.mlp import (
    mlp_afunc,
    MultiActMLP,
    init_linear_weight,
    xavier_normal_init,
    save,
)
from jaxDiversity.baseline import compute_loss as compute_loss_baseline
from jaxDiversity.hnn import compute_loss as compute_loss_hnn
from jaxDiversity.loops import inner_opt, outer_opt
```

#### inner optimzation or standard training loop with the baseline activation

``` python
dev_inner_config = InnerConfig(
    test_train_split=0.8,
    input_dim=2,
    output_dim=2,
    hidden_layer_sizes=[18],
    batch_size=64,
    epochs=2,
    lr=1e-3,
    mu=0.9,
    n_fns=2,
    l2_reg=1e-1,
    seed=42,
)
key = jax.random.PRNGKey(dev_inner_config.seed)
model_key, init_key = jax.random.split(key)
afuncs = [lambda x: x**2, lambda x: x]
train_dataset = DummyDataset(
    1000, dev_inner_config.input_dim, dev_inner_config.output_dim
)
test_dataset = DummyDataset(
    1000, dev_inner_config.input_dim, dev_inner_config.output_dim
)
train_dataloader = NumpyLoader(
    train_dataset, batch_size=dev_inner_config.batch_size, shuffle=True
)
test_dataloader = NumpyLoader(
    test_dataset, batch_size=dev_inner_config.batch_size, shuffle=True
)

opt = optax.rmsprop(
    learning_rate=dev_inner_config.lr,
    momentum=dev_inner_config.mu,
    decay=dev_inner_config.l2_reg,
)
model = MultiActMLP(
    dev_inner_config.input_dim,
    dev_inner_config.output_dim,
    dev_inner_config.hidden_layer_sizes,
    model_key,
    bias=False,
)
baselineNN, opt_state, inner_results = inner_opt(
    model=model,
    train_data=train_dataloader,
    test_data=test_dataloader,
    afuncs=afuncs,
    opt=opt,
    loss_fn=compute_loss_baseline,
    config=dev_inner_config,
    training=True,
    verbose=True,
)
```

#### metalearning with Hamiltonian Neural Networks

``` python
inner_config = InnerConfig(
    test_train_split=0.8,
    input_dim=2,
    output_dim=1,
    hidden_layer_sizes=[32],
    batch_size=64,
    epochs=5,
    lr=1e-3,
    mu=0.9,
    n_fns=2,
    l2_reg=1e-1,
    seed=42,
)
outer_config = OuterConfig(
    input_dim=1,
    output_dim=1,
    hidden_layer_sizes=[18],
    batch_size=1,
    steps=2,
    print_every=1,
    lr=1e-3,
    mu=0.9,
    seed=24,
)
train_dataset = DummyDataset(1000, inner_config.input_dim, 2)
test_dataset = DummyDataset(1000, inner_config.input_dim, 2)
train_dataloader = NumpyLoader(
    train_dataset, batch_size=inner_config.batch_size, shuffle=True
)
test_dataloader = NumpyLoader(
    test_dataset, batch_size=inner_config.batch_size, shuffle=True
)

opt = optax.rmsprop(
    learning_rate=inner_config.lr, momentum=inner_config.mu, decay=inner_config.l2_reg
)
meta_opt = optax.rmsprop(learning_rate=outer_config.lr, momentum=outer_config.mu)

HNN_acts, HNN_stats = outer_opt(
    train_dataloader,
    test_dataloader,
    compute_loss_hnn,
    inner_config,
    outer_config,
    opt,
    meta_opt,
    save_path=None,
)
```

Link to older pytorch codebase with classification problem:
[DiversityNN](https://github.com/NonlinearArtificialIntelligenceLab/DiversityNN)

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_MLP.ipynb.

# %% auto 0
__all__ = ['trunc_init', 'deterministic_init', 'xavier_normal_init', 'xavier_uniform_init', 'init_linear_weight', 'MultiActMLP',
           'save', 'make_mlp', 'load', 'mlp_afunc']

# %% ../nbs/03_MLP.ipynb 4
import jax
import jax.numpy as jnp
import equinox as eqx
import json

# %% ../nbs/03_MLP.ipynb 5
def trunc_init(weight: jax.Array, key: jax.random.PRNGKey) -> jax.Array:
    """truncated normal initialization"""
    out, in_ = weight.shape
    stddev = jnp.sqrt(1 / in_)
    return stddev * jax.random.truncated_normal(key, lower=-2, upper=2)


def deterministic_init(weight: jax.Array, key: jax.random.PRNGKey) -> jax.Array:
    """constant initialization
    parameters only for consistency with other initializations"""
    return jnp.ones(weight.shape) * 1e-3


def xavier_normal_init(weight: jax.Array, key: jax.random.PRNGKey) -> jax.Array:
    """xavier normal initialization"""
    out, in_ = weight.shape
    stddev = jnp.sqrt(2 / in_)
    return stddev * jax.random.normal(key, shape=weight.shape)


def xavier_uniform_init(weight: jax.Array, key: jax.random.PRNGKey) -> jax.Array:
    """xavier uniform initialization"""
    out, in_ = weight.shape
    bound = jnp.sqrt(6 / in_)
    return bound * jax.random.uniform(key, shape=weight.shape, minval=-1, maxval=1)

# %% ../nbs/03_MLP.ipynb 6
def init_linear_weight(model, init_fn, key):
    """initialize linear weights of a model with a given init_fn"""

    def is_linear(x):
        return isinstance(x, eqx.nn.Linear)

    def get_weights(m):
        return [
            x.weight
            for x in jax.tree_util.tree_leaves(m, is_leaf=is_linear)
            if is_linear(x)
        ]

    weights = get_weights(model)
    new_weights = [
        init_fn(weight, subkey)
        for weight, subkey in zip(weights, jax.random.split(key, len(weights)))
    ]
    new_model = eqx.tree_at(get_weights, model, new_weights)
    return new_model

# %% ../nbs/03_MLP.ipynb 7
class MultiActMLP(eqx.Module):
    input_dim: int
    output_dim: int
    hidden_layer_sizes: list
    layers: list
    bias: bool  # whether to include bias in the linear layers

    def __init__(self, input_dim, output_dim, hidden_layer_sizes, key, bias=True):
        super().__init__()
        self.bias = bias
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_layer_sizes = [input_dim] + hidden_layer_sizes + [output_dim]
        self.layers = []
        keys = jax.random.split(key, len(self.hidden_layer_sizes))
        for i in range(len(self.hidden_layer_sizes) - 1):
            layer = eqx.nn.Linear(
                self.hidden_layer_sizes[i],
                self.hidden_layer_sizes[i + 1],
                key=keys[i],
                use_bias=bias,
            )
            self.layers.append(layer)

    def __call__(self, x, afuncs):
        """
        x: input data
        afuncs: activation functions
        splits the layers into sections and applies the activation function
        """
        activity = []
        for layer in self.layers[:-1]:
            split_idx = int(layer.weight.shape[0] / len(afuncs))
            x = layer(x)
            activity.append(x)
            for i, afunc in enumerate(afuncs):
                # applies activation functions to each split of layer
                x = x.at[i * split_idx : (i + 1) * split_idx].set(
                    afunc(x[i * split_idx : (i + 1) * split_idx])
                )

        # return self.apply_linear(x, self.layers[-1]), activity
        return self.layers[-1](x), activity

# %% ../nbs/03_MLP.ipynb 9
def save(filename, hyperparams, model):
    """save model and hyperparameters to file"""
    with open(filename, "wb") as f:
        hyperparam_str = json.dumps(hyperparams)
        f.write((hyperparam_str + "\n").encode())
        eqx.tree_serialise_leaves(f, model)

# %% ../nbs/03_MLP.ipynb 11
def make_mlp(config_dict):
    """initialize MLP using hyperparameters from config_dict"""
    key = jax.random.PRNGKey(config_dict["seed"])
    model_key, init_key = jax.random.split(key)
    model = eqx.nn.MLP(
        in_size=config_dict["input_dim"],
        out_size=config_dict["output_dim"],
        width_size=config_dict["hidden_layer_sizes"][0],
        depth=1,
        key=model_key,
        use_bias=True,
    )
    return model

# %% ../nbs/03_MLP.ipynb 12
def load(filename, make=make_mlp):
    """load model and hyperparameters from file"""
    with open(filename, "rb") as f:
        hyperparams = json.loads(f.readline().decode())
        model = make(hyperparams)
        return eqx.tree_deserialise_leaves(f, model)

# %% ../nbs/03_MLP.ipynb 14
def mlp_afunc(x, model, base_act):
    """
    MLP that behaves like an activation function
    """
    new_x = x.reshape(-1, 1)
    out = jax.vmap(model)(new_x)
    return base_act(x) + out.reshape(x.shape)

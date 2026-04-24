# Local Tooling

This repo pins the local CLI toolchain with `mise.toml` so macOS and Linux shells use the same versions for day-to-day operations.

## First-time Setup

Install `mise`, then install the pinned tools:

```sh
curl https://mise.run | sh
~/.local/bin/mise trust mise.toml
~/.local/bin/mise install
```

After that, either activate `mise` in your shell or run commands through it:

```sh
eval "$(mise activate bash)"
mise exec -- task validate
```

For zsh on macOS:

```sh
eval "$(mise activate zsh)"
```

If you already have `task` available, this wrapper does the same install:

```sh
task tools:install
```

## Validation

Run the local validation path before pushing Kubernetes changes:

```sh
task validate
```

That runs:

- `kubectl kustomize` against every app and Flux repository kustomization root
- `flux-local test --all-namespaces --enable-helm --path kubernetes/flux/cluster --verbose`

If you need GHCR auth for private images, export either `RENOVATE_GHCR_TOKEN` or `GITHUB_TOKEN` before running validation. The task writes a temporary Docker registry config under `.tmp/`.

## Notes

The Talos template path needs `op`, `talosctl`, `jq`, `yq`, and `minijinja-cli`. Those are included in `mise.toml`, because relying on whatever random-ass version is already on PATH is how these workflows rot.

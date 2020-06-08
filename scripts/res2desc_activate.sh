# This file should be source to activate tab completion.
# can be placed at $CONDA_PREFIX/etc/conda/activate.d/ to work with conda
# supports zsh and bash
if [ -z "$BASH_VERSION" ]; then
	eval "$(_RES2DESC_COMPLETE=source_zsh res2desc)"
else
	eval "$(_RES2DESC_COMPLETE=source_bash res2desc)"
fi

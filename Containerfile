# A container for Woodpecker CI
# This it NOT meant to be used in any other context

FROM debian:trixie-slim

ENV UV_LINK_MODE=copy
ENV PATH=.venv/bin:$PATH

RUN apt update && apt install cargo gpg -y

COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/

# install different python versions and populate the pypi cache,
# this way woodpecker does not have to make network calls unless
# we change the dependencies

COPY pyproject.toml uv.lock .

RUN for VER in 3.9 3.10 3.11 3.12 3.13; do \
        uv python install $VER ; \
        uv python pin $VER ; \
        uv sync --frozen --all-groups --no-install-project ; \
	done

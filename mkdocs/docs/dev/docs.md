# Documentation

## Structure of the docs

The documentation is split into three parts:

1. Tutorials

    Self-contained guides that walk the reader through making a small project.
    Don't explain too much, and use very simple language: take a look at the
    [Plain English](https://www.plainenglish.co.uk/free-guides.html) guides.

2. Reference

    Function, classes, modules and their interfaces. Describe in a precise way
    how to interact with a particular thing.

3. For contributors

    Guides for people who want to contribute to Lanim

## Build the docs

1. Activate the virtual environment (probably with `poetry shell`)
2. `mkdocs build -f mkdocs/mkdocs.yml`

This will create a `site` directory in `lanim/mkdocs/site` with the HTML, CSS and JS files, ready to deploy.

## Serve the docs

1. Activate the virtual environment (probably with `poetry shell`)
2. `mkdocs serve -f mkdocs/mkdocs.yml`

This will let you browse the docs at `127.0.0.1:8000`. It will also reload if it detects a change in the docs.

## Deploy docs on github

1. Activate the virtual environment (probably with `poetry shell`)
2. `mkdocs gh-deploy -f mkdocs/mkdocs.yml`

This will build the docs and push them to the `gh-pages` branch, so that GitHub Pages can serve it.
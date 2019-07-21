# Livewires website

## Hosted with Netlify

[![Netlify Status](https://api.netlify.com/api/v1/badges/d9d0950d-631a-4018-8684-4ee29cf95e1e/deploy-status)](https://app.netlify.com/sites/livewires/deploys)

<https://livewires.org.uk>

When a pull request is merged, Netlify will automatically rebuild and deploy the website.

## Local development

When you open a pull request, Netlify will automatically build a "deploy preview" containing your changes.

### To set up a virtual Python environment

Make sure you have Python 3 installed (e.g. via Homebrew).

Make sure you have Virtualenv installed, e.g.
```console
$ pip3 install virtualenv
```

```console
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### To build the site

```console
$ venv/bin/python build.py
```

It will output into `_site/`.

### To watch for file changes

```console
$ venv/bin/python build.py -w
```

The builder will rebuild each file when it is requested.




## To set up a virtual Python environment

Make sure you have Python 3 installed (e.g. via Homebrew).

Make sure you have Virtualenv installed, e.g.
```console
sudo pip3 install virtualenv
```

```console
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## To build the site

```console
$ venv/bin/python build.py
```

It will output into `_site/`.

## To watch for file changes

```console
$ venv/bin/python build.py -w
```

The builder will rebuild each file when it is requested.


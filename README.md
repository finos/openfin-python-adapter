# Python Openfin

[![Build Status](https://travis-ci.com/jpmorganchase/openfin-python-adapter.svg?token=ocjHWzxvxkyiafiXyepz&branch=master)](https://travis-ci.com/jpmorganchase/openfin-python-adapter)

A Python OpenFin adapter for communicating across the OpenFin message-bus. 

<div style="text-align:center;">
  <img style="max-width: 450px; margin: 0 auto;" src="example.gif">
</div>

## Installation

Install as normal by calling 

    python setup.py install

On Windows, this requires the pywin32 module. This is
included in the extras_require, but at the time of writing pip support for pywin32 was experimental, and you may have better
results going to the [official pywin32 repo](https://github.com/mhammond/pywin32) and following instructions there.

## Getting started

A simple example is available in the example folder. Open a pair of terminals. Run this in the first to open an OpenFin window.

    openfin -l -c example/app.json -u example/index.html

This should have created a blank window. Now in a second, run this:

    python example/example.py

This should start sending messages from the python process to the OpenFin process.
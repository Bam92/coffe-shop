#!/bin/bash

export FLASK_APP=src/api.py
export FLASK_DEBUG

flask run --reload
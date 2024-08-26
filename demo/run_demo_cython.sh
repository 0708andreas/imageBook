#!/usr/bin/env bash

../cython/generator.py -o output.jpg -bs 32 --select random --seed 10 image.jpg mindre_billeder/*

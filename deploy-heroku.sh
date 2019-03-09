#!/bin/sh

git push heroku `git subtree split --prefix web web-cra`:master --force

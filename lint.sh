#!/bin/sh -xe

# ignoring empty except b/c we're rethrowing
lint8 --web --exclude=.*/tests,.*/runtests performant_pagination
lint8 --ignore=L007 performant_pagination/tests/ performant_pagination/runtests/ setup.py

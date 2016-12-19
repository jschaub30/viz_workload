#! /bin/bash

## example of a preprocessor.
## log on to each HOST to see if there are JUNK.$$ files with zero size in /tmp

touch /tmp/JUNK.$$

## real cleaning task can be anything
## e.g., \rm -rf /tmp/*
## or better yet: \rm -rf /             :-) 

## end

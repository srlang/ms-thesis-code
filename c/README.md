Code from this directory has been added for the purpose of making the processing
behind the database population more low-level, and therefore (hopefully) faster.

This is mostly based on old code I thankfully was just playing around with a few
months ago.
The original code can be found on NCSU's github:
[code](https://github.ncsu.edu/srlang/Cribbage)

It has been shown that two sqlite3 databases can be merged without too much
trouble.
As a result, the next thing to do would be to parallelize the crap out of the
file I/O portion of the code to no longer use blocks on a single database file,
but to write to separate databases in each thread.
One test gave a 5-second improvement (on 2:35ish time), so further testing will
be needed to see if this improvement was a fluke or holds.
Furthermore, this will need to be tested on Ukko to see if more parallelization,
etc. benefits this code or if we've basically reached the local ceiling (I'm not
rewriting this again for a minor improvement. What we need now is hardware, not
software).

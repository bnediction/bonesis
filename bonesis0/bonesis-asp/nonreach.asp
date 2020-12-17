mcfg((nr,X,Y,1..K),N,V) :- nonreach(X,Y,K), cfg(X,N,V).
clamped((nr,X,Y,1..K),N,V) :- nonreach(X,Y,K), clamped(X,N,V).

ext((nr,X,Y,I),N,V) :- eval((nr,X,Y,I),N,V), not locked((nr,X,Y,I),N).

nr_bad(X,Y,I,N) :- cfg(X,N,V), cfg(Y,N,V),
                    ext((nr,X,Y,I),N,-V), not ext((nr,X,Y,I),N,V).
locked((nr,X,Y,I+1..K),N) :- nr_bad(X,Y,I,N), nonreach(X,Y,K), I < K.

% K is too small
nr_overflow(X,Y) :- nonreach(X,Y,K), not nr_ok(X,Y), nbnode(M), K < M, nr_bad(X,Y,K,_).
:- nr_overflow(X,Y).

nr_ok(X,Y) :- nonreach(X,Y,K), cfg(Y,N,V), not mcfg((nr,X,Y,K),N,V).
:- nonreach(X,Y,K), not nr_ok(X,Y).

#const bounded_nonreach=0.
nonreach(X,Y,K) :- nonreach(X,Y), cfg(X,_,_), cfg(Y,_,_), nbnode(K), bounded_nonreach <= 0.
nonreach(X,Y,bounded_nonreach) :- nonreach(X,Y), cfg(X,_,_), cfg(Y,_,_), bounded_nonreach > 0.
nonreach(_bofake,_bofake).

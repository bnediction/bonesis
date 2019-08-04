mcfg(X,N,V) :- is_fp(X), cfg(X,N,V).
:- is_fp(X), cfg(X,N,V), eval(X,N,-V).

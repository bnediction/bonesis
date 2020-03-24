is_tp(X,N) :- is_tp(X), obs(X,N,_), node(N).
mcfg((ts,X),N,V) :- cfg(X,N,V), is_tp(X,_).
mcfg((ts,X),N,V) :- eval((ts,X),N,V).
:- is_tp(X,N), cfg(X,N,V), mcfg((ts,X),N,-V).

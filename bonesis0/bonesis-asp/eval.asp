eval(X,N,C,-1) :- clause(N,C,L,-V), mcfg(X,L,V).
eval(X,N,C,1) :- mcfg(X,L,V): clause(N,C,L,V); clause(N,C,_,_), mcfg(X,_,_).
eval(X,N,1) :- eval(X,N,C,1), clause(N,C,_,_).
eval(X,N,-1) :- eval(X,N,C,-1): clause(N,C,_,_); clause(N,_,_,_), mcfg(X,_,_).
eval(X,N,V) :- constant(N,V), mcfg(X,_,_).
mcfg(X,N,V) :- ext(X,N,V).

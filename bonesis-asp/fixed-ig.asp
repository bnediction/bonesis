edge(L,N,S) :- clause(N,_,L,S).
:- X = #count { L,N,S: edge(L,N,S)}, Y = #count { L,N,S: in(L,N,S)}, X != Y.

{clause(N,1..C,L,S): in(L,N,S), maxC(N,C), node(N), node(L)}.
:- clause(N,_,L,S), clause(N,_,L,-S).
1 {constant(N,(-1;1)) } 1 :- node(N), not clause(N,_,_,_).
constant(N) :- constant(N,_).

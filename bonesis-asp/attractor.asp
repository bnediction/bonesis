mcfg((at,X),N,V) :- is_at(X); cfg(X,N,V).
mcfg((at,X),N,V) :- eval((at,X),N,V).

2{cfg((a0,X),N,V);cfg((a1,X),N,V)}2 :- mcfg((at,X),N,V), not mcfg((at,X),N,-V).
%cfg((a1,X),N,V) :- mcfg((at,X),N,V), not mcfg((at,X),N,-V).
2{cfg((a0,X),N,0);cfg((a1,X),N,1)}2 :- mcfg((at,X),N,V), mcfg((at,X),N,-V).
%cfg((a1,X),N,1) :- mcfg((at,X),N,V), mcfg((at,X),N,-V).

reach((a0,X),(a1,X)) :- is_at(X).
reach((a1,X),(a0,X)) :- is_at(X).

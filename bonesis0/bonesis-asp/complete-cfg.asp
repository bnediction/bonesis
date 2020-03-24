cfg(X,N,V) :- obs(X,N,V), node(N).
1 {cfg(X,N,(-1;1))} 1 :- obs(X,_,_), node(N), not obs(X,N,_).

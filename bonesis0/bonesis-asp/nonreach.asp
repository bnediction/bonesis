%% maxreach iterations to check the neg reach
#const bounded_nonreach=-1.
iter(1..bounded_nonreach) :- bounded_nonreach >= 0.
iter(1..M) :- bounded_nonreach < 0, nbnode(M).
:- locked(X,Y,bounded_nonreach,N); not locked(X,Y,bounded_nonreach-1,N);
    bounded_nonreach < M; nbnode(M); bounded_nonreach >= 0.

locked(X,Y,I+1,N) :- cfg(X,N,V); cfg(Y,N,V); iter(I+1);
                        ext((nr,X,Y,I),N,-V); not ext((nr,X,Y,I),N,V).
locked(X,Y,I+1,N) :- locked(X,Y,I,N), iter(I+1).

mcfg((nr,X,Y,I),N,V) :- nonreach(X,Y); cfg(X,N,V); iter(I).
ext((nr,X,Y,I),N,V) :- eval((nr,X,Y,I),N,V); not locked(X,Y,I,N).
nr_ok(X,Y) :- nonreach(X,Y); cfg(Y,N,V); not mcfg((nr,X,Y,K),N,V); nbnode(K);
    bounded_nonreach < 0.
nr_ok(X,Y) :- nonreach(X,Y); cfg(Y,N,V); not mcfg((nr,X,Y,bounded_nonreach),N,V);
    bounded_nonreach >= 0.
:- not nr_ok(X,Y), nonreach(X,Y).

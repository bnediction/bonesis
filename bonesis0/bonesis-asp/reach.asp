mcfg((pr,X,Y),N,V) :- reach(X,Y), cfg(X,N,V).
ext((pr,X,Y),N,V) :- reach(X,Y), eval((pr,X,Y),N,V), cfg(Y,N,V),
                        not locked((pr,X,Y),N).
{ext((pr,X,Y),N,V)} :- reach(X,Y), eval((pr,X,Y),N,V), cfg(Y,N,-V),
                        not locked((pr,X,Y),N).
:- reach(X,Y), cfg(Y,N,V), not mcfg((pr,X,Y),N,V).
:- reach(X,Y), cfg(Y,N,V), ext((pr,X,Y),N,-V), not ext((pr,X,Y),N,V).

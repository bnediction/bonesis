size(N,C,X) :- X = #count {L,S: clause(N,C,L,S)}; clause(N,C,_,_).
:- clause(N,C,_,_); not clause(N,C-1,_,_); C > 1.
:- size(N,C1,X1); size(N,C2,X2); X1 < X2; C1 > C2.
:- size(N,C1,X); size(N,C2,X); C1 > C2; mindiff(N,C1,C2,L1) ; mindiff(N,C2,C1,L2) ; L1 < L2.
clausediff(N,C1,C2,L) :- clause(N,C1,L,_);not clause(N,C2,L,_);clause(N,C2,_,_), C1 != C2.
mindiff(N,C1,C2,L) :- clausediff(N,C1,C2,L); L <= L' : clausediff(N,C1,C2,L'), clause(N,C1,L',_), C1!=C2.
:- size(N,C1,X1); size(N,C2,X2); C1 != C2; X1 <= X2; clause(N,C2,L,S) : clause(N,C1,L,S).

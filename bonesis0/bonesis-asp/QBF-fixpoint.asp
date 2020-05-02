%%%%%%%%%%%%%
% CONSTRAINT:
% Each fixpoint of the network is compatible with (one of) the set of markers defined as X.
% Several states X can be precised.
%%%%%%%%%%%%%

% disjunctive rule: to explore all configurations
cfg(_z_,N,-1) ; cfg(_z_,N,1) :- node(N).

% check properties:
%% either the configuration is not a fixpoint
mcfg(_z_,N,V) :- cfg(_z_,N,V).
valid :- cfg(_z_,N,V) ; eval(_z_,N,-V).
%% or the configuration has at least the same markers than X
valid :- cfg(_z_,N,V):obs(X,N,V); is_global_fp((obs,X)).

%TODO: valid -> valid_all_fixpoints?

% saturation of the predicate under disjunctive rule
% (to benefit from the subset minimality semantics to consider each subset - so each configuration)
cfg(_z_,N,-V) :- cfg(_z_,N,V) ; valid.

% a solution has to respect at least one of the above properties
:- not valid.

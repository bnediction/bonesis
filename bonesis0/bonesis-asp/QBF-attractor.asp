%%%%%%%%%%%%%
% CONSTRAINT:
% Each attractor of the network is compatible with (one of) the set of markers defined as X.
% Several states X can be precised.
%%%%%%%%%%%%%

% disjunctive rule: to explore all configurations
cfg(_za_,N,-1) ; cfg(_za_,N,1) :- node(N).

% check properties:
%% either the configuration is not a fixpoint and all markers have to be in its maximal configuration,
%% or the configuration is a fixpoint and has at least the same markers than X.
%% Finally, in the 2 cases, it's ensured by checking the presence of the markers in the maximal configuration.
mcfg(_za_,N,V) :- cfg(_za_,N,V).
mcfg(_za_,N,V) :- eval(_za_,N,V).
valid_all_attractors :- mcfg(_za_,N,V):obs(X,N,V); is_global_at((obs,X)).

% saturation of the predicate under disjunctive rule
% (to benefit from the subset minimality semantics to consider each subset - so each configuration)
cfg(_za_,N,-V) :- cfg(_za_,N,V) ; valid_all_attractors.

% a solution has to respect at least one of the above properties
:- not valid_all_attractors.

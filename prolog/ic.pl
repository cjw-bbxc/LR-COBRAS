:- dynamic must_link/2.
:- dynamic cannot_link/2.


symmetrical_must_link(X, Y) :-
    must_link(X, Y);
    must_link(Y, X).

symmetrical_cannot_link(X, Y) :-
    cannot_link(X, Y);
    cannot_link(Y, X).

...

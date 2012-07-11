
likes( john, curry ).
likes( sandy, mushrooms ).

dislikes( X, Y ) :- not( likes( X, Y ) ).

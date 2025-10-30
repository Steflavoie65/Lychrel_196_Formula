1. Cadre Algébrique Fondamental
1.1 Système de Contraintes de Palindromicitée
Pour tout entier 
n
n soumis à l'itération 
T
(
n
)
=
n
+
rev
(
n
)
T(n)=n+rev(n), la condition de palindromicitée se formalise comme un système d'équations polynomiales :

F
(
x
)
=
x
+
R
x
−
N
≡
0
(
m
o
d
p
)
F(x)=x+Rx−N≡0(modp)
où 
R
R est la matrice de renversement et 
N
N le vecteur des digits cibles.

1.2 Découverte Structurelle Clé : La Nilpotence
Théorème (Nilpotence du Jacobien) :

J
=
I
+
R
⇒
J
2
≡
0
(
m
o
d
2
)
J=I+R⇒J 
2
 ≡0(mod2)
Preuve :

J
2
=
(
I
+
R
)
2
=
I
+
2
R
+
R
2
=
2
(
I
+
R
)
=
2
J
⇒
J
2
≡
0
(
m
o
d
2
)
J 
2
 =(I+R) 
2
 =I+2R+R 
2
 =2(I+R)=2J⇒J 
2
 ≡0(mod2)
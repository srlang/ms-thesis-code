
MESSAGE PROTOCOL
===============================

Hand: Card1 Card2 Card3 Card4

Statuses
-------------------
A(live)
X(Exit)
K(ill)

Strategies
-------------------
S(tanley)
H(ighest)
C(rib)
P(eg)

Miscellany
-------------------
R(esults)



Protocols
-------------------

Server:
1. A
2. X
3. K
4. <Strategy> <Hand> [Hand2]

Client:
1. A
2. <ReturnCode>
3. <ReturnCode>
4. R <Strategy> <Hand> [Hand2] <Score>

Can use alive functionality in a separate python process to keep pinging for
alive status.
Need to figure out a way to have changes in server status recognized by
program:
	- use an external file of server locations/names
	- have a trigger when the file changes to reload file contents
		- better, build in a protocol for that on server side


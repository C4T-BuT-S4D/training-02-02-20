all:
	rm -rf legacy
	mkdir legacy
	gcc -Wall -c keygen.c -o keygen.o
	ar -cq legacy/keygen.a keygen.o
	rm keygen.o

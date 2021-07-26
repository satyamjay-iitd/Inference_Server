install: sem.c
	gcc -shared -o libsem.so -fPIC sem.c
	cp libsem.so ../../../city/Assets/Plugins
run: sem.c
	gcc sem.c -o sem -lpthread -lrt
	./sem



GCC=gcc
OPT_LEVEL=-O2
C_FLAGS=
CPP_FLAGS=-std=c++11
C_LIBS=-lc
CPP_LIBS=-lc -lstdc++

# all: for.c.out for_pre.cpp.out for_post.cpp.out while.cpp.out for_ranges.cpp.out for.py.out
all: for.c.out for_pre.cpp.out for_post.cpp.out while.cpp.out for_ranges.cpp.out

%.c.out: %.c
	$(GCC) -o $<.o $< -c $(OPT_LEVEL) $(C_FLAGS)
	$(GCC) -o $@ $<.o $(C_LIBS) $(OPT_LEVEL)

%.cpp.out: %.cpp
	$(GCC) -o $<.o $< -c $(OPT_LEVEL) $(CPP_FLAGS)
	$(GCC) -o $@ $<.o $(CPP_LIBS) $(OPT_LEVEL)

%.py.out: %.py
	cp $< $@
	chmod +x $@ 

clean:
	rm -f *.o
	rm -f *.out

#! /usr/bin/env python3

import os, sys, time, re
print("Welcome to the Alex-Shell, enter 'exit' to exit")
while 1:
    print(">>>", end='')
    command = input("")
    if command == "exit":
        sys.exit(1)
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                     (os.getpid(), pid)).encode())
        args = command.split(' ')
        os.close(1)                 # redirect child's stdout
        sys.stdout = open("output.txt", "w")
        fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
        os.set_inheritable(fd, True)
        os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 
        sys.exit(1)             
    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())


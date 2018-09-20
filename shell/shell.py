#! /usr/bin/env python3

import os, sys, time, re, fileinput

redirections = ['>', '>>', '<', '|']

print("Welcome to the Alex-Shell, enter 'exit' to exit")

while 1:
    print(">>>", end='')
    command = input("")
    if command == "exit":
        sys.exit(1)

    pid = os.getpid()
    user_input = command.split(' ')
    redirection_locations = [-1]
    # store the location of redirection characters, start and end points
    for i, item in enumerate(user_input):
        if any(r in item for r in redirections):
            redirection_locations.append(i)
    redirection_locations.append(len(user_input)-1)
        # Go through each redirection and resolve it from left to right
    for i in range(1, len(redirection_locations) - 1):
        args = user_input[redirection_locations[i-1] + 1:redirection_locations[i+1] + 1]
        if '>' in user_input[redirection_locations[i]]:
            rc = os.fork()
            if rc == 0:
                os.close(1)           
                os.write(2, (str(args) + str(i) + str(redirection_locations[i]) + str(user_input)).encode())
                sys.stdout = open(args[i+1], "w") if '>' is user_input[redirection_locations[i]] else open(args[i+1], "a")
                fd = sys.stdout.fileno()
                os.set_inheritable(fd, True)
                for dir in re.split(":", os.environ['PATH']): # try each directory in path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args[i-1:i], os.environ) # try to exec program         
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly 
            else:                           # parent (forked ok)
                os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                             (pid, rc)).encode())
                childPidCode = os.wait()
                os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                             childPidCode).encode())
        elif user_input[redirection_locations[i]] is '<':
            os.write(2, (str(args)).encode()) 
            fd = sys.stdin.fileno()
            os.set_inheritable(fd, True)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args[i-1:i], os.environ) # try to exec program
                    sys.stdin = open(args[i+1])
                    
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 
        
        elif '|' is user_input[redirection_locations[i]]:
            pid = os.getpid()               # get and remember pid

            pr,pw = os.pipe()

            for f in (pr, pw):
                os.set_inheritable(f, True)

            rc = os.fork()

            if rc < 0:
                print("fork failed, returning %d\n" % rc, file=sys.stderr)
                sys.exit(1)

            elif rc == 0:                   #  child - will write to pipe
                os.close(1)                 # redirect child's stdout
                os.dup(pr)
                for fd in (pr, pw):
                    os.close(fd)
#                print('output.txt')
                os.execve('/usr/bin/ls', ['/usr/bin/ls'], os.environ)
            else:
   #             os.write(2, (str(i) + str(redirection_locations) + 'THE ARGUMENTS: ' + str(args[redirection_locations[i-1]+1:redirection_locations[i]])).encode())
                '''
 #               for dir in re.split(":", os.environ['PATH']): # try each directory in path
                   program = "%s/%s" % (dir, args[0])
                    try:
                        
                        #os.execve('/usr/bin/ls', ['/usr/bin/ls', '-l'], os.environ) # try to exec program
                        #os.execve(program, args[redirection_locations[i-1] + 1:redirection_locations[i]], os.environ) # try to exec program
                        #os.write(os.execve(program, args[i-1:i], os.environ))
                        break
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly 
                '''
#            else:                     # parent (forked ok)
                print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
                os.close(0)
                os.dup(pr)
                for fd in (pw, pr):
                    os.close(fd)
                args = [args[i+2]]

                for line in fileinput.input():
                    args.append(line[:-1])
                os.write(2, (str(args)).encode())
                
                os.write(2, ('THE ARGUMENTS: ' + str(args)).encode())
                for dir in re.split(":", os.environ['PATH']): # try each directory in path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                        os.write(2, 'success'.encode())
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly 
                exit(1)

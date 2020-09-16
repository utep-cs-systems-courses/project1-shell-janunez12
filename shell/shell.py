# Author: Jehu Alejandro Nunez
# Date: 9/06/2020
# CS4375 Theory of Operating Systems
# Eric Freudenthal
# Project 1

import os, sys, re

def fork(args):
    # Get and remember pid
    pid = os.getpid()
    # Set rc to fork
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    # Child
    elif rc == 0:
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())
        sys.exit(1)

    else:
        # Wait for child to fork
        childPid = os.wait()

def redirectIn(args):
    pid = os.getpid()  # get pid

    rc = os.fork()  # ready to fork

    if rc < 0:  # return error message if fork fails
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        del args[1]
        fd = sys.stdout.fileno()  # set file descriptor output

        try:
            os.execve(args[0], args, os.environ)  # execute program
        except FileNotFoundError:
            pass
        for dir in re.split(":", os.environ['PATH']):  # check for environment variables
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, ("%s: command not found\n" % args[0]).encode()) # return error
        
        sys.exit(1)

    else:
        childPid = os.wait()

def redirectOut(args):
    # Check index ouput '>'
    fileIndex = args.index('>') + 1
    # Array index input
    fileName = args[fileIndex]

    args = args[:fileIndex - 1]

    # Get pid
    pid = os.getpid()
    # Ready to fork
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        os.close(1)
        sys.stdout = open(fileName, "w")
        os.set_inheritable(1, True)

        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)
            except FileNotFoundError:
                pass
            else:
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(args[0], args, os.environ)
                    except FileNotFoundError:
                        pass

                os.write(2, ("%s: command not found\n" % args[0]).encode())
                sys.exit(1)
    else:
        childPid = os.wait()
    

def pipe(args):
    pid = os.getpid() # get pid
    pipe = args.index("|") # check for pipe

    # Read input / Write output
    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)

    rc = os.fork()

    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)

    elif rc == 0:  # write to pipe from child
        args = args[:pipe]

        os.close(1)

        fd = os.dup(pw)  # duplicate file descriptor output
        os.set_inheritable(fd, True)
        for fd in (pr, pw):
            os.close(fd)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)  # execute program
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):  # Check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # execute program
                except FileNotFoundError:
                    pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())

        sys.exit(1)

    else:
        args = args[pipe + 1:]

        os.close(0)

        fd = os.dup(pr)  # duplicate file descriptor for output
        os.set_inheritable(fd, True)
        for fd in (pw, pr):
            os.close(fd) 

        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)  # execute program
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):  # Check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # execute program
                except FileNotFoundError:
                    pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())  # return error

        sys.exit(1)


while True:
    # Prompt string to shell
    if 'PS1' in os.environ:
        promptShell = os.environ['PS1']
        if promptShell != "$ ":
            os.write(1, "$ ".encode())
        os.write(1, os.environ['PS1'].encode())
    try:
        userInput = input()
    except EOFError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)

    # Split input
    args = userInput.split()

    # Exit Command
    if "exit" in userInput:
        sys.exit(0)

    # Change directory
    if "cd" in args[0]:
        try:
            os.chdir(args[1])
        except FileNotFoundError:
            os.write(1, ("cd: %s: No such file or directory\n" % args[1]).encode())
            pass

    # Redirection Output
    elif  ">" in userInput: 
        redirectOut(args)

    # Redirection Input
    elif "<" in userInput: 
        redirectIn(args)

    # Pipe
    elif "|" in userInput: 
        pipe(args)

        # Handle Commands

    else:
        fork(args) 

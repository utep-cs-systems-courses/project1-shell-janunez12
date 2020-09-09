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


while True:
    # Prompt string to shell
    if 'PS1' in os.environ:
        os.write(1, os.environ['PS1'].encode())
    try:
        userInput = input()
    except EOFError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)

    # Split input
    args = userInput.split()

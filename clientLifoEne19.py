# uncompyle6 version 3.3.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Mar  4 2019, 09:01:38) 
# [GCC 4.2.1 Compatible Apple LLVM 10.0.0 (clang-1000.11.45.5)]
# Embedded file name: clientLifoEne19.py
# Compiled at: 2019-05-18 11:28:48
import socket, sys, time, random
politica = sys.argv[1]
seed = sys.argv[2]
messages = [
 (0.0, 'RealMemory 1'), (0.1, 'SwapMemory 1'), (0.2, 'PageSize 16'), (0.3, 'Pol\xc3\xadticaMemory RND'), (1, 'P 32 1'),
 (2, 'P 48 2'), (3, 'P 63 3'), (4, 'L 2'), (5, 'P 80 4'), (6, 'P 704 5'), (7, 'P 96 6'), (8, 'A 16 1 0'), (9, 'A 62 3 1'),
 (10, 'A 1 3 1'), (11, 'P 128 7'), (12, 'A 36 7 0'), (13, 'A 52 7 0'), (14, 'L 6'), (15, 'A 700 5 0'), (16, 'L 7'),
 (17, 'L 1'), (18, 'L 3'),
 (19, 'L 4'),
 (20, 'L 5'), (21, 'F'), (22, 'E')]
messages[3] = (
 0.3, 'PoliticaMemory ' + politica)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
print >> sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
try:
    previousMsgTime = 0.0
    debug1 = False
    firstTime = True
    for m in messages:
        timestamp = float(m[0])
        msg = m[1]
        initialMsg = timestamp < 1.0
        if firstTime:
            firstTime = False
            thisMsgTime = 0.0
            initialTime = time.time()
            if seed != '0':
                random.seed(int(seed))
        else:
            thisMsgTime = timestamp
            if not initialMsg:
                if seed != '0':
                    thisMsgTime += random.uniform(-1, 1)
                    if thisMsgTime < 0.0:
                        thisMsgTime = timestamp
                    if debug1:
                        print >> sys.stderr, 'randomised', thisMsgTime
            if thisMsgTime > previousMsgTime:
                sleepTime = thisMsgTime - previousMsgTime
                if debug1:
                    print >> sys.stderr, 'sleeptime', sleepTime
                time.sleep(sleepTime)
            else:
                thisMsgTime = previousMsgTime
        if debug1:
            print >> sys.stderr, 'antes de calcular timedM', thisMsgTime
        timedM = msg
        print >> sys.stderr, 'client sending "%s"' % timedM
        sock.sendall(timedM)
        previousMsgTime = thisMsgTime
        respuesta = sock.recv(256)
        print >> sys.stderr, 'client received "%s"' % respuesta
        timestamp1 = time.time() - initialTime
        if debug1:
            print >> sys.stderr, 'timestamp', timestamp1

    sock.close()
finally:
    print >> sys.stderr, 'closing socket'
    sock.close()

def main(args):
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
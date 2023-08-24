import socket
import pickle
import numpy as np

RECV_BUFSIZE = 65536
DAC_SAMPLE_DT = 1/8.e9 # 8 GHz DAC sample rate

class SimClient:

    def __init__(self, host='localhost', port=9100):
        self.host = host
        self.port = port

    def run_program(self, asm_prog, sim_time):
        """
        """
        dumpdict = {'asm_prog': asm_prog, 'nsamples': sim_time//DAC_SAMPLE_DT}
        progdump = pickle.dumps(dumpdict)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(progdump)
            data = bytes()
            while True:
                newdata = sock.recv(RECV_BUFSIZE)
                if not newdata:
                    break
                data += newdata                

            self.dacout = pickle.loads(data)

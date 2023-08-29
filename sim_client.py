import socket
import pickle
import numpy as np

RECV_BUFSIZE = 65536
DAC_SAMPLE_DT = 1/8.e9 # 8 GHz DAC sample rate

class SimClient:
    """
    Simple class for interfacing with the cocotb/verilator simulation server. Usage:
        client = Simclient(host, port)
        client.run_program(asm_prog, 300.e-9)

        # plot dac out
        plt.plot(client.dacout[dac_ch])

        # run another program
        client.run_program(asm_prog2, 400.e-9)
        # etc...
    """

    def __init__(self, host='localhost', port=9100):
        self.host = host
        self.port = port

    def run_program(self, asm_prog, sim_time):
        """
        Run a program in the cocotb/verilator simulator. Resulting DAC 
        output is stored in self.dacout (numpy array with shape (ndacs, nsamples).

        Parameters
        ----------
        asm_prog : dict
            compiled qubic program
        sim_time : float
            total simulation runtime (not including memory loads) in seconds
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

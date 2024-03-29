import socket
import pickle
import numpy as np
import matplotlib.pyplot as plt

RECV_BUFSIZE = 65536
DAC_SAMPLE_DT = 1/8.e9 # 8 GHz DAC sample rate
ADC_SAMPLE_DT = 1/2.e9 # 2 GHz ADC sample rate

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

    def run_program(self, asm_prog, sim_time, adc_stream=None, adc_delay=0, capture_demod=False):
        """
        Run a program in the cocotb/verilator simulator. Resulting DAC 
        output is stored in self.dacout (numpy array with shape (ndacs, nsamples)).

        Parameters
        ----------
        asm_prog : dict
            compiled qubic program
        sim_time : float
            total simulation runtime (not including memory loads) in seconds
        """
        dumpdict = {'asm_prog': asm_prog, 
                    'nsamples': sim_time//DAC_SAMPLE_DT,
                    'capture_demod': capture_demod}
        if adc_stream is not None:
            assert np.all(adc_stream <= 1)
            adc_stream *= (2**15 - 1)
            if adc_delay > 0:
                adc_stream = np.append(np.zeros(int(adc_delay//ADC_SAMPLE_DT)), adc_stream)
            adc_stream = np.append(adc_stream, np.zeros(4))
            dumpdict['adc_stream'] = adc_stream

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

            output_dict = pickle.loads(data)
            if isinstance(output_dict, Exception):
                raise output_dict
            else:
                self.dac_out = output_dict['dac_out']
                self.dac_timesteps = np.arange(0, self.dac_out.shape[1]*DAC_SAMPLE_DT, DAC_SAMPLE_DT)
                self.adc_timesteps = np.arange(0, self.dac_out.shape[1]*ADC_SAMPLE_DT, ADC_SAMPLE_DT)
                self.acc = output_dict['acc']
                self.adc_stream = adc_stream
                if capture_demod:
                    self.rdlo = output_dict['rdlo']
                    self.rdlo_x_adc = output_dict['rdlo_x_adc']

    def plot_dac_out(self, channel, start_time=0, end_time=None):
        start_ind = int(start_time//DAC_SAMPLE_DT)
        if end_time is None:
            end_ind = self.dac_out.shape[1]
        else:
            end_ind = int(end_time//DAC_SAMPLE_DT)

        plt.plot(self.dac_timesteps[start_ind:end_ind], self.dac_out[channel, start_ind:end_ind]/(2**15-1))
        plt.xlabel('time (s)')
        plt.ylabel('DAC level')
        plt.title(f'DAC channel {channel}')
        plt.show()

    def plot_rdlo(self, channel, start_time, end_time=None):
        start_ind = int(start_time//ADC_SAMPLE_DT)
        if end_time is None:
            end_ind = self.rdlo.shape[1]
        else:
            end_ind = int(end_time//ADC_SAMPLE_DT)

        plt.plot(self.adc_timesteps[start_ind:end_ind], self.rdlo[channel, start_ind:end_ind].real/(2**15-1), label='I (real)')
        plt.plot(self.adc_timesteps[start_ind:end_ind], self.rdlo[channel, start_ind:end_ind].imag/(2**15-1), label='Q (imag)')
        plt.legend()
        plt.xlabel('time (s)')
        plt.ylabel('signal level')
        plt.title(f'rdlo channel {channel}')
        plt.show()

    def plot_rdlo_x_adc(self, channel, start_time, end_time=None):
        start_ind = int(start_time//ADC_SAMPLE_DT)
        if end_time is None:
            end_ind = self.rdlo_x_adc.shape[1]
        else:
            end_ind = int(end_time//ADC_SAMPLE_DT)

        plt.plot(self.adc_timesteps[start_ind:end_ind], self.rdlo_x_adc[channel, start_ind:end_ind].real/(2**15-1), label='I (real)')
        plt.plot(self.adc_timesteps[start_ind:end_ind], self.rdlo_x_adc[channel, start_ind:end_ind].imag/(2**15-1), label='Q (imag)')
        plt.legend()
        plt.xlabel('time (s)')
        plt.ylabel('signal level')
        plt.title(f'rdlo channel {channel}')
        plt.show()


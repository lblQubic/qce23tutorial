import qubic.toolchain as tc
import qubitconfig.qchip as qc
import qubic.rfsoc.hwconfig as hw

import numpy as np
import bqplot as plt


# FPGA timing information for the scheduler
fpga_config = hw.FPGAConfig(**{'fpga_clk_period': 2.e-9,
                               'alu_instr_clks': 5,
                               'jump_cond_clks': 5,
                               'jump_fproc_clks': 5,
                               'pulse_regwrite_clks': 3})

# mapping of programmatic labels to actual channels
channel_configs = hw.load_channel_configs('channel_config.json')

# gate definitions and qubit calibration data
qchip = qc.QChip('qubitcfg.json')


class WaveCalculator:
    def __init__(self, host='localhost', port=9100):
        self.dacout = np.array([])

    def run_program(self, asm_prog, sim_time=None, adc_stream=None, adc_delay=0):
        # helper to calculate pulses, etc.
        elem = hw.RFSoCElementCfg()
        samples_per_clock = elem.samples_per_clk//elem.interp_ratio
        fpga_clk_freq = channel_configs['fpga_clk_freq']

        # for plotting purposes, skip any initial delay/reset
        first_pulse = 2**31

        # some basic info for constructing the output array
        qubits = set()
        calc_sim_time = sim_time is None
        if calc_sim_time: sim_time = 0
        for targets, ops in asm_prog.program.items():
            qubits.add(int(targets[0][1]))
            if calc_sim_time:
                for op in ops:
                    if op['op'] == 'pulse' and not 'rdlo' in op['dest']:
                        pulse_start = int(op['start_time'])
                        pulse_len = op['env']['paradict']['twidth']
                        first_pulse = min(first_pulse, pulse_start)
                        pulse_end = pulse_start + elem.length_nclks(pulse_len)
                        sim_time = max(sim_time, pulse_end)

        # total time simulated
        if calc_sim_time:
            nsamples = (sim_time-first_pulse)*samples_per_clock
        else:
            nsamples = elem.length_nclks(sim_time)*samples_per_clock

        # output array
        self.dacout = np.zeros((max(qubits)+1, nsamples))

        # helper to calculate pulses
        elem = hw.RFSoCElementCfg()

        # actually runs on compiled programs, not assembled programs
        last_readout = 0
        for targets, ops in asm_prog.program.items():
            qubit = int(targets[0][1])
            for op in ops:
                if op['op'] == 'pulse' and not 'rdlo' in op['dest']:
                    start_sample = int((op['start_time']-first_pulse)*samples_per_clock)
                    if 'rdrv' in op['dest']:
                        last_readout = max(last_readout, start_sample)
                    scale = op['amp']/2**31
                    phase = op['phase'] + op['start_time'] * (op['freq'] / fpga_clk_freq)
                    penv = elem.get_env_buffer(op['env'])*scale
                    bins = 2*np.pi*np.arange(0, len(penv))/samples_per_clock
                    mod = np.cos(op['freq']*bins + phase)
                    penv *= mod
                    self.dacout[qubit,start_sample:start_sample+len(penv)] = penv

        return self.dacout, last_readout

simulator = WaveCalculator()


def simulate(circuit, sim_time=None):
    # compile and assemble circuit
    circuit_compiled  = tc.run_compile_stage(circuit, fpga_config, qchip)
    circuit_assembled = tc.run_assemble_stage(circuit_compiled, channel_configs)

    # use the compiled circuit here for the in-process simulator; use the
    # assembled circuit for the real thing
    circuit = circuit_compiled
    if not isinstance(simulator, WaveCalculator):
        circuit = circuit_assembled
        if sim_time is None:
            sim_time = 1E-6

    dacout, readout_start = simulator.run_program(circuit, sim_time)

    return dacout, readout_start


def plot_wave(sim_result, qubit=0, lower=None, upper=None, down_sample=0):
    dac_out = sim_result[0][qubit]
    if lower is None:
        lower = 0
    if upper is None:
        upper = min(sim_result[1]+3000, len(dac_out))

    dac_out = dac_out[lower:upper]

    if down_sample:
        dac_out = dac_out[::down_sample]

    x_sc = plt.LinearScale()
    y_sc = plt.LinearScale()

    ax_x = plt.Axis(scale=x_sc)
    ax_y = plt.Axis(scale=y_sc, orientation="vertical")

    x_data = np.arange(lower, upper, down_sample and down_sample or 1)
    y_data = dac_out
    scatter = plt.Lines(
        x=x_data,
        y=y_data,
        scales={"x": x_sc, "y": y_sc},
    )

    fig = plt.Figure(axes=[ax_x, ax_y], marks=[scatter])
    fig.interaction = plt.PanZoom(scales={"x": [x_sc]})#, "y": [y_sc]})

    return fig, scatter

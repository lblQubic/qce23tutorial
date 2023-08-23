FROM nfruitwala/cocotb-verilator:0.4

#clone all repos
RUN git clone https://gitlab.com/nfruitwala/qubic-gateware.git --recursive -b tutorial
RUN git clone https://gitlab.com/lbl-qubic/software.git -b rfsoc
RUN git clone https://gitlab.com/lbl-qubic/distributed_processor.git
RUN git clone https://gitlab.com/lbl-qubic/experiments/qubitconfig.git

#pip install them
RUN pip install -e distributed_processor/python
RUN pip install -e software
RUN pip install -e qubitconfig 

#start server
RUN cd /qubic-gateware/top/zcu216_8_2; make pre
#RUN make pre
RUN cd /qubic-gateware/dsp/cocotb/tutorial_demo; make
#RUN make

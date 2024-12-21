I used https://github.com/merldsu/RISCV_Pipeline_Core as a reference, improved it, 
and converted the 32-bit RISC-V pipeline to 16-bit with a custom instruction set 
(see Prompt___Mini-RISCV-Pipeline.pdf). I added stalling, flushing, and a jump 
signal. The only missing feature is forwarding when a store occurs; otherwise, 
it is fully functional. A custom test bench is also included.

To simulate on Linux:
  iverilog -o smile pipeline_tb.v Pipeline_Top.v
  vvp smile
  gtkwave dump.vcd &

Instructions:
  • iverilog compiles the Verilog source into an executable (smile).  
  • vvp runs the simulation.  
  • gtkwave opens the waveform (dump.vcd).  

Each custom instruction follows a shortened 16-bit format with opcode, 
register fields, and immediate values. Look into the PDF for specifics.

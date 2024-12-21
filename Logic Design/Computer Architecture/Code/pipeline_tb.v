module tb();
    reg clk;
    reg rst;
    
    // Initialize signals
    initial begin
        clk = 0;
        rst = 0;
    end
    
    // Clock generation with faster frequency
    always begin
        #5 clk = ~clk;    
    end

    // Reset sequence with much longer simulation time
    initial begin
        rst = 0;         
        #10;            // Longer reset
        rst = 1;         
        #20000;         // Much longer simulation time
        $finish;    
    end

    // Enhanced waveform dumping and monitoring
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb);

    end

    Pipeline_top dut (.clk(clk), .rst(rst));

endmodule
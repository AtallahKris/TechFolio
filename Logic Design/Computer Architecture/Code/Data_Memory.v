module Data_Memory(clk,rst,WE,WD,A,RD);

    input clk,rst,WE;
    input [15:0]A,WD;
    output [15:0]RD;

    reg [15:0] mem [1023:0];

    always @ (posedge clk)
    begin
        if(WE)
            mem[A] <= WD;
    end

    assign RD = (~rst) ? 16'd0 : mem[A];

    initial begin
        mem[0] = 16'h0000;
    end


endmodule
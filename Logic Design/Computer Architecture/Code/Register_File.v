module Register_File(clk,rst,WE3,WD3,A1,A2,A3,RD1,RD2);

    input clk,rst,WE3;
    input [2:0]A1,A2,A3;
    input [15:0]WD3;
    output [15:0]RD1,RD2;
    
    reg [15:0] Register [7:0];

    always @ (posedge clk)
    begin
        if(WE3 & (A3 != 3'h0))
            Register[A3] <= WD3;
    end

    assign RD1 = (rst==1'b0) ? 16'd0 : Register[A1];
    assign RD2 = (rst==1'b0) ? 16'd0 : Register[A2];

    integer i;
    initial begin
    for (i = 0; i < 8; i = i + 1) begin
        Register[i] = 16'h0000;
    end
end

endmodule
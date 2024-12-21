module PC_Module(
    input clk,
    input rst,
    input stall,
    input [15:0] PC_Next,
    output reg [15:0] PC
);

    always @(posedge clk or negedge rst) begin
        if (rst == 1'b0) begin
            PC <= 16'h0000;
        end else if (!stall) begin
            PC <= PC_Next;
        end
    end
endmodule
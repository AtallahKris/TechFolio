module Instruction_Memory(rst,A,RD);
    input rst;
    input [15:0]A;
    output [15:0]RD;
    
    reg [15:0] mem [0:255];  
    
    // Add bounds checking and address limiting
    wire [15:0] safe_addr;
    assign safe_addr = (A[15:0] < 24552) ? A[15:0] : 16'd0;
    
    // Monitor address access
    always @(A) begin
        if (A[15:0] >= 24552)
            $display("Warning: Address %h exceeds memory bounds", A);
    end
    
    assign RD = (rst == 1'b0) ? 16'h0000 : mem[safe_addr];

    initial begin
        $readmemh("memfile.hex", mem);
        $display("Memory loaded with size: %d words", 24552);
    end
endmodule
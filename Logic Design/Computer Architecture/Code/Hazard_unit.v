module hazard_unit(
    input rst,
    input RegWriteM,
    input RegWriteW,
    input PCSrcE,
    input ResultSrcE,
    input [2:0] RD_M,
    input [2:0] RD_W,
    input [2:0] RD_E,
    input [2:0] Rs1_E,
    input [2:0] Rs2_E,
    input [2:0] Rs1_D,
    input [2:0] Rs2_D,
    output [1:0] ForwardAE,
    output [1:0] ForwardBE,
    output StallF,
    output StallD,
    output FlushD,
    output FlushE
);

    // Forwarding logic remains the same
    assign ForwardAE = (rst == 1'b0) ? 2'b00 :
                       ((RegWriteM == 1'b1) && (RD_M != 3'h0) && (RD_M == Rs1_E)) ? 2'b10 :
                       ((RegWriteW == 1'b1) && (RD_W != 3'h0) && (RD_W == Rs1_E)) ? 2'b01 : 2'b00;
                       
    assign ForwardBE = (rst == 1'b0) ? 2'b00 : 
                       ((RegWriteM == 1'b1) && (RD_M != 3'h0) && (RD_M == Rs2_E)) ? 2'b10 :
                       ((RegWriteW == 1'b1) && (RD_W != 3'h0) && (RD_W == Rs2_E)) ? 2'b01 : 2'b00;

    // Hazard detection for stalls and flushes
    wire lw_stall;
    assign lw_stall = (ResultSrcE == 1'b1) && ((RD_E == Rs1_D) || (RD_E == Rs2_D));

    assign StallF = lw_stall;
    assign StallD = lw_stall;
    assign FlushD = PCSrcE; // Flush Decode stage on branch taken
    assign FlushE = lw_stall || PCSrcE; // Flush Execute stage on stall or branch taken

endmodule
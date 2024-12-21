module fetch_cycle(
    input clk,
    input rst,
    input PCSrcE,
    input StallF,
    input [15:0] PCTargetE,
    output [15:0] InstrD,
    output [15:0] PCD,
    output [15:0] PCPlus4D
);

    wire [15:0] PC_F, PCF, PCPlus4F;
    wire [15:0] InstrF;

    reg [15:0] InstrF_reg;
    reg [15:0] PCF_reg, PCPlus4F_reg;


    // Initiation of Modules
    // Declare PC Mux
    Mux PC_MUX (.a(PCPlus4F),
                .b(PCTargetE),
                .s(PCSrcE),
                .c(PC_F)
                );

    // Declare PC Counter
    PC_Module Program_Counter (
        .clk(clk),
        .rst(rst),
        .stall(StallF),
        .PC(PCF),
        .PC_Next(PC_F)
    );


    // Declare Instruction Memory
    Instruction_Memory IMEM (
                .rst(rst),
                .A(PCF),
                .RD(InstrF)
                );

    // Declare PC adder
    PC_Adder PC_adder (
                .a(PCF),
                .b(16'h0001),
                .c(PCPlus4F)
                );

    // Fetch Cycle Register Logic
    always @(posedge clk or negedge rst) begin
        if(rst == 1'b0) begin
            InstrF_reg <= 16'h0000;
            PCF_reg <= 16'h0000;
            PCPlus4F_reg <= 16'h0000;
        end
        else begin
            InstrF_reg <= InstrF;
            PCF_reg <= PCF;
            PCPlus4F_reg <= PCPlus4F;
        end
    end


    // Assigning Registers Value to the Output port
    assign  InstrD = (rst == 1'b0) ? 16'h0000 : InstrF_reg;
    assign  PCD = (rst == 1'b0) ? 16'h0000 : PCF_reg;
    assign  PCPlus4D = (rst == 1'b0) ? 16'h0000 : PCPlus4F_reg;


endmodule

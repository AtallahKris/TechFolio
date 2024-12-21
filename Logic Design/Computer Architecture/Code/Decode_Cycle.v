module decode_cycle(
    input clk,
    input rst,
    input [15:0] InstrD,
    input [15:0] PCD,
    input [15:0] PCPlus4D,
    input RegWriteW,
    input [2:0] RDW,
    input [15:0] ResultW,
    input StallD,
    input FlushD,
    output RegWriteE,
    output ALUSrcE,
    output MemWriteE,
    output ResultSrcE,
    output BranchE,
    output JumpE,
    output [2:0] ALUControlE,
    output [15:0] RD1_E,
    output [15:0] RD2_E,
    output [15:0] Imm_Ext_E,
    output [2:0] RD_E,
    output [15:0] PCE,
    output [15:0] PCPlus4E,
    output [2:0] RS1_E,
    output [2:0] RS2_E
);


    // Declare Interim Wires
    wire RegWriteD,ALUSrcD,MemWriteD,ResultSrcD,BranchD,JumpD;
    wire [1:0] ImmSrcD;
    wire [2:0] ALUControlD;
    wire [15:0] RD1_D, RD2_D, Imm_Ext_D;

    // Declaration of Interim Register
    reg RegWriteD_r,ALUSrcD_r,MemWriteD_r,ResultSrcD_r,BranchD_r,JumpD_r;
    reg [2:0] ALUControlD_r;
    reg [15:0] RD1_D_r, RD2_D_r, Imm_Ext_D_r;
    reg [2:0] RD_D_r, RS1_D_r, RS2_D_r;
    reg [15:0] PCD_r, PCPlus4D_r;


    // Initiate the modules
    // Control Unit
    Control_Unit_Top control (
                            .Op(InstrD[2:0]),
                            .RegWrite(RegWriteD),
                            .ImmSrc(ImmSrcD),
                            .ALUSrc(ALUSrcD),
                            .MemWrite(MemWriteD),
                            .ResultSrc(ResultSrcD),
                            .Branch(BranchD),
                            .Jump(JumpD),
                            .funct3(InstrD[8:7]),
                            .funct7(InstrD[16:15]),
                            .ALUControl(ALUControlD)
                            );

    // Register File
    Register_File rf (
                        .clk(clk),
                        .rst(rst),
                        .WE3(RegWriteW),
                        .WD3(ResultW),
                        .A1(InstrD[11:9]),
                        .A2(InstrD[14:12]),
                        .A3(RDW),
                        .RD1(RD1_D),
                        .RD2(RD2_D)
                        );

    // Sign Extension
    Sign_Extend extension (
                        .In(InstrD[15:0]),
                        .Imm_Ext(Imm_Ext_D),
                        .ImmSrc(ImmSrcD)
                        );

    // Declaring Register Logic
    always @(posedge clk or negedge rst) begin
        if (rst == 1'b0 || FlushD) begin
            // Flush the pipeline registers
            RegWriteD_r <= 1'b0;
            ALUSrcD_r <= 1'b0;
            MemWriteD_r <= 1'b0;
            ResultSrcD_r <= 1'b0;
            BranchD_r <= 1'b0;
            JumpD_r <= 1'b0;
            ALUControlD_r <= 3'b000;
            RD1_D_r <= 16'h0000;
            RD2_D_r <= 16'h0000;
            Imm_Ext_D_r <= 16'h0000;
            RD_D_r <= 3'h0;
            PCD_r <= 16'h0000;
            PCPlus4D_r <= 16'h0000;
            RS1_D_r <= 3'h0;
            RS2_D_r <= 3'h0;
        end else if (!StallD) begin
            // Normal operation
            RegWriteD_r <= RegWriteD;
            ALUSrcD_r <= ALUSrcD;
            MemWriteD_r <= MemWriteD;
            ResultSrcD_r <= ResultSrcD;
            BranchD_r <= BranchD;
            JumpD_r <= JumpD;
            ALUControlD_r <= ALUControlD;
            RD1_D_r <= RD1_D;
            RD2_D_r <= RD2_D;
            Imm_Ext_D_r <= Imm_Ext_D;
            RD_D_r <= InstrD[11:7];
            PCD_r <= PCD;
            PCPlus4D_r <= PCPlus4D;
            RS1_D_r <= InstrD[11:9];
            RS2_D_r <= InstrD[14:12];
        end
    end

    // Output asssign statements
    assign RegWriteE = RegWriteD_r;
    assign ALUSrcE = ALUSrcD_r;
    assign MemWriteE = MemWriteD_r;
    assign ResultSrcE = ResultSrcD_r;
    assign BranchE = BranchD_r;
    assign JumpE = JumpD_r;
    assign ALUControlE = ALUControlD_r;
    assign RD1_E = RD1_D_r;
    assign RD2_E = RD2_D_r;
    assign Imm_Ext_E = Imm_Ext_D_r;
    assign RD_E = RD_D_r;
    assign PCE = PCD_r;
    assign PCPlus4E = PCPlus4D_r;
    assign RS1_E = RS1_D_r;
    assign RS2_E = RS2_D_r;

endmodule
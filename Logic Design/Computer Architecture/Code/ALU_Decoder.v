module ALU_Decoder(ALUOp,funct3,funct7,op,ALUControl);

    input [1:0] ALUOp;
    input [1:0] funct3, funct7;
    input [2:0] op;
    output reg [2:0] ALUControl;

    always @(*) begin
        if (ALUOp == 2'b10) begin
            // R-type instructions
            case (funct7)
                2'b00: begin
                    case (funct3)
                        2'b00: ALUControl = 3'b000; // ADD
                        2'b01: ALUControl = 3'b001; // SUB
                        2'b10: ALUControl = 3'b010; // AND
                        2'b11: ALUControl = 3'b011; // OR
                        default: ALUControl = 3'b000;
                    endcase
                end
                2'b01: begin
                    case (funct3)
                        2'b00: ALUControl = 3'b100; // XOR
                        2'b01: ALUControl = 3'b101; // SLT
                        2'b10: ALUControl = 3'b110; // SLTU
                        2'b11: ALUControl = 3'b111; // ROR
                        default: ALUControl = 3'b000;
                    endcase
                end
                default: ALUControl = 3'b000;
            endcase
        end else if (ALUOp == 2'b00) begin
            // I-type instructions
            if (op == 3'b001) begin
                case (funct3)
                    2'b00: ALUControl = 3'b000; // LD (uses ADD)
                    2'b01: ALUControl = 3'b000; // ADDI
                    2'b10: ALUControl = 3'b010; // ANDI
                    2'b11: ALUControl = 3'b011; // ORI
                    default: ALUControl = 3'b000;
                endcase
            end else if (op == 3'b010) begin
                case (funct3)
                    2'b00: ALUControl = 3'b100; // XORI
                    2'b01: ALUControl = 3'b101; // SLTI
                    2'b10: ALUControl = 3'b110; // SLTIU
                    2'b11: ALUControl = 3'b111; // RORI
                    default: ALUControl = 3'b000;
                endcase
            end else begin
                ALUControl = 3'b000;
            end
        end else if (ALUOp == 2'b01) begin
            // Branch instructions
            ALUControl = 3'b001; // Use SUB for comparison
        end else begin
            ALUControl = 3'b000; // Default to ADD
        end
    end

endmodule
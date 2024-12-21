module Main_Decoder(Op,funct3,RegWrite,ALUSrc,MemWrite,ResultSrc,Branch,Jump,ImmSrc,ALUOp);
    input [2:0]Op;
    input [1:0]funct3;
    output RegWrite,ALUSrc,MemWrite,ResultSrc,Branch,Jump;
    output [1:0]ImmSrc,ALUOp;

    // RegWrite is enabled for:
    // - R-type Instructions: add, sub, and, or, xor, slt, sltu, ror (Opcode: 000)
    // - I-type Instructions: ld, addi, andi, ori (Opcode: 001)
    // - I-type Instructions: xori, slti, sltiu, rori (Opcode: 010)
    // - JL-type Instruction: jal (Opcode: 110)
    assign RegWrite = (Op == 3'b000 || Op == 3'b001 || Op == 3'b010 || Op == 3'b110) ? 1'b1 : 1'b0;
    
    // ImmSrc determines the type of immediate value extension:
    // - I-type Instruction:  → ImmSrc = 01
    // - SB-type Instructions: st (Opcode: 011), beq (Opcode: 100), bne (Opcode: 101) → ImmSrc = 10
    // - JL-type Instruction: jal (Opcode: 110) → ImmSrc = 11
    // - Default for R-type Instructions → ImmSrc = 00
    assign ImmSrc = (Op == 3'b001 || Op == 3'b010) ? 2'b01 :  // I-type
                    (Op == 3'b011 || Op == 3'b100 || Op == 3'b101) ? 2'b10 : // SB-type (branch) or S-type (store)
                    (Op == 3'b110) ? 2'b11 : // JL-type (jump and link)
                    2'b00; // Default (R-type)

    // ALUSrc selects the second ALU operand:
    // - I-type Instructions: ld, addi, andi, ori (Opcode: 001)
    // - I-type Instructions: xori, slti, sltiu, rori (Opcode: 010)
    // - S-type Instruction: st (Opcode: 011)
    // - ALUSrc = 1 selects the immediate value as the second operand
    assign ALUSrc = (Op == 3'b001 || Op == 3'b010 || Op == 3'b011) ? 1'b1 : 1'b0;

    // MemWrite enables writing to memory for:
    // - S-type Instruction: st (Opcode: 011)
    assign MemWrite = (Op == 3'b011) ? 1'b1 : 1'b0;

    // ResultSrc selects the data source for writing back to the register:
    // - Load Instruction: ld (Opcode: 001) with funct3 indicating 'ld' → ResultSrc = 1
    // - Other I-type Instructions: addi, andi, ori, etc. → ResultSrc = 0
    assign ResultSrc = (Op == 3'b001 && funct3 == 2'b00) ? 1'b1 : 1'b0;

    // Branch is enabled for:
    // - SB-type Instructions: beq (Opcode: 100), bne (Opcode: 101)
    // - Jump Instructions: jal (Opcode: 110), jr (Opcode: 111)
    assign Branch = (Op == 3'b100 || Op == 3'b101 || Op == 3'b110 || Op == 3'b111) ? 1'b1 : 1'b0;

    // ALUOp determines the type of ALU operation:
    // - R-type Instructions: add, sub, and, or, xor, slt, sltu, ror (Opcode: 000) → ALUOp = 10
    // - SB-type Instructions: beq (Opcode: 100), bne (Opcode: 101) → ALUOp = 01 (for comparison)
    // - Default for I-type and others → ALUOp = 00
    assign ALUOp = (Op == 3'b000) ? 2'b10 : // R-type instructions
                (Op == 3'b100 || Op == 3'b101) ? 2'b01 : // SB-type (branch) instructions
                2'b00; // Default (I-type and others)

    // Jump is activated for:
    // - JL-type Instruction: jal (Opcode: 110)
    // - JR-type Instruction: jr (Opcode: 111)
    assign Jump = (Op == 3'b110 || Op == 3'b111) ? 1'b1 : 1'b0;

endmodule
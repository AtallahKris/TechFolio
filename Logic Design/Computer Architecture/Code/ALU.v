module ALU(A,B,Result,ALUControl,OverFlow,Carry,Zero,Negative);

    input [15:0] A, B;
    input [2:0] ALUControl;
    output Carry, OverFlow, Zero, Negative;
    output [15:0] Result;

    wire Cout;
    wire [15:0] Sum;
    wire [15:0] ROR_Result;
    wire [3:0] ShiftAmount;

    assign Sum = (ALUControl[0] == 1'b0) ? A + B :
                                          (A + ((~B)+1));

    assign ShiftAmount = B[3:0]; // Use least significant 4 bits for shift amount

    assign ROR_Result = (A >> ShiftAmount) | (A << (16 - ShiftAmount));

    assign {Cout, Result} = (ALUControl == 3'b000) ? {1'b0, Sum} : // ADD
                            (ALUControl == 3'b001) ? {1'b0, Sum} : // SUB
                            (ALUControl == 3'b010) ? {1'b0, A & B} : // AND
                            (ALUControl == 3'b011) ? {1'b0, A | B} : // OR
                            (ALUControl == 3'b100) ? {1'b0, A ^ B} : // XOR
                            (ALUControl == 3'b101) ? {1'b0, {15'b0, $signed(A) < $signed(B)}} : // SLT
                            (ALUControl == 3'b110) ? {1'b0, {15'b0, A < B}} : // SLTU
                            (ALUControl == 3'b111) ? {1'b0, ROR_Result} : // ROR
                            {17{1'b0}};

    assign OverFlow = ((ALUControl == 3'b000 || ALUControl == 3'b001) &&
                       ((Sum[15] ^ A[15]) & (~(ALUControl[0] ^ B[15] ^ A[15]))));

    assign Carry = ((ALUControl == 3'b000 || ALUControl == 3'b001) && Cout);

    assign Zero = &(~Result);
    assign Negative = Result[15];

endmodule
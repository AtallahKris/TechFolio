module PC_Adder (a,b,c);

    input [15:0]a,b;
    output [15:0]c;

    assign c = a + b;
    
endmodule
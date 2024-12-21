module Mux (a,b,s,c);

    input [15:0]a,b;
    input s;
    output [15:0]c;

    assign c = (~s) ? a : b ;
    
endmodule

module Mux_3_by_1 (a,b,c,s,d);
    input [15:0] a,b,c;
    input [1:0] s;
    output [15:0] d;

    assign d = (s == 2'b00) ? a : (s == 2'b01) ? b : (s == 2'b10) ? c : 16'h0000;
    
endmodule
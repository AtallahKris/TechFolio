module Sign_Extend (In,ImmSrc,Imm_Ext);
    input [15:0] In;
    input [1:0] ImmSrc;
    output [15:0] Imm_Ext;

    assign Imm_Ext =    (ImmSrc == 2'b01) ? {{11{In[15]}},In[15:11]} : //I-type 
                        (ImmSrc == 2'b10) ? {{11{In[15]}},In[15:14],In[5:3]} : //SB-type
                        (ImmSrc == 2'b11) ? {{7{In[15]}},In[10:6],In[14:11]}: //JL-type
                        16'h0000; 

endmodule
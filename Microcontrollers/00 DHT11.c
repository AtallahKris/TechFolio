#include    <p18cxxx.h>
#include    <LCD4PICDEM2.h>
#include    <string.h>

#pragma config FOSC = INTIO67
#pragma config WDTEN = OFF
#pragma config MCLRE = EXTMCLR                      

#define     ValidResponse       FLAGS.B0
#define     SF                  2                   

char Line1[] = "R. Humidity -- %";
char Line2[] = "Temperature -- C";

unsigned char DataPacket[5];
unsigned char Temp, RH;

void Setup(void);
void MeasureHT(void);
void StartSignal(void);
void CheckResponse(void);
char ReadData(void);

void main(void) {
    Setup();
 
    while (1) {
        MeasureHT(); 
        Delay10KTCYx(50 * SF);                       
    }
}

void Setup(void) {
    OSCCON = 0b01100000;                    
    ANSELBbits.ANSB0 = 0;                   
    InitLCD();
    Line2[14] = 0xDF;
}

void MeasureHT(void) {
    unsigned char i, Checksum;
    
    StartSignal();
    CheckResponse();
    
    if (ValidResponse) {
        for (i = 0; i < 5; i++)
            DataPacket[i] = ReadData();

        for (i = 0, Checksum = 0; i < 4; i++)
            Checksum += DataPacket[i];
        
        if (Checksum == DataPacket[4])  {
            RH = DataPacket[0];
            Line1[12] = RH / 10 + '0';
            Line1[13] = RH % 10 + '0';
            
            Temp = DataPacket[2];
            Line2[12] = (Temp / 10)  + '0';
            Line2[13] = (Temp % 10) + '0';

            DispRamStr(Ln1Ch0, Line1);
            DispRamStr(Ln2Ch0, Line2);
        }         
        else {
            DispRomStr(Ln1Ch0, (ROM *) "Checksum Error !");
            DispRomStr(Ln2Ch0, (ROM *) "Check the sensor");
        }
    }
    else {
        DispRomStr(Ln1Ch0, (ROM *) "  No response   ");
        DispRomStr(Ln2Ch0, (ROM *) "from the sensor!");
    }           
}

void StartSignal(void) {
    PORTBbits.RB0 = 0;                      
    TRISBbits.TRISB0 = 0;                   
    Delay1KTCYx(18 * SF);                   
    PORTBbits.RB0 = 1;                      
    Delay10TCYx(3 * SF);                    
    TRISBbits.TRISB0 = 1;                   
}

void CheckResponse(void) {
    Delay10TCYx(4 * SF);                    
    if (PORTBbits.RB0 == 0) {
        Delay10TCYx(8 * SF);                
        ValidResponse = PORTBbits.RB0;
        Delay10TCYx(4 * SF);                
    }
}

 char ReadData(void) {
    char data, i;
    
    for (i = 0; i < 8; i++) {
        while (!PORTBbits.RB0);             
        Delay10TCYx(3 * SF);                
        if (PORTBbits.RB0 == 0)
            data &= ~(1 << (7 - i));        
        else {
            data |= (1 << (7 - i));         
            while (PORTBbits.RB0);          
        }
    }
    return data;
 }
   

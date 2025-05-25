#include <p18cxxx.h>
#include <BCDlib.h>

char SScodes[] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F, 0x63, 0x39, 0x71};
unsigned char i, Qstate;
float temp;
enum {degree = 10, C, F};
char digits[5] = {0, 0, 0, degree, C};

#define LO PORTBbits.RB5
#define MID PORTBbits.RB6
#define HI PORTBbits.RB7

void setup(void);
void measureT(void);
void controlLamp(void);

void main(void) {
    setup();
    while(1) {
        measureT();
    }
}

void setup(void) {
    ANSELD = TRISD = 0x00;
    TRISA &= 0xF0;
    ANSELA &= 0xF0;
    TRISBbits.RB0 = 1;
    TRISBbits.RB5 = TRISBbits.RB6 = TRISBbits.RB7 = 0;
    ANSELBbits.ANSB0 = ANSELBbits.ANSB5 = 0;
    INTCON2bits.RBPU = 0;
    WPUB = 0b00000001;
    TRISEbits.RE2 = ANSELEbits.ANSE2 = 1;
    ADCON0 = 0b00011101;
    ADCON1 = 0x08;
    ADCON2 = 0b00001001;
    VREFCON0 = 0b10010000;
    INTCONbits.T0IE = 1;
    INTCONbits.GIE = 1;
    T0CON = 0b11010100;
    TMR0L = 256 - 125;
    i = 1;
    Qstate = 0b00001000;
    HI = 0;
    MID = 0;
    LO = 0;
}

#pragma code ISR = 0x0008
#pragma interrupt ISR

void ISR(void) {
    INTCONbits.T0IF = 0;
    TMR0L = 256 - 125;
    PORTD = 0x00;
    PORTA = Qstate;
    PORTD = SScodes[digits[i++]];
    Qstate >>= 1;
    if(i == 5) {
        i = 1;
        Qstate = 0b00001000;
    }
}

void measureT(void) {
    ADCON0bits.GO_DONE = 1;
    while(ADCON0bits.NOT_DONE);
    temp = (ADRESH * (102.4 / 256));
    
    if(INTCONbits.INT0IF) {
        INTCONbits.INT0IF = 0;
        if(digits[4] == C)
            digits[4] = F;
        else
            digits[4] = C;
    }
    
    if(digits[4] == F)
        temp = 1.8 * temp + 32;
    
    Bin2Bcd((unsigned char) temp, digits);
    
    if(ADRESH >= 75 && ADRESH < 250) {
        LO = 0;
        MID = 0;
        HI = 1;
    }
    else if(ADRESH >= 50 && ADRESH < 75) {
        LO = 0;
        MID = 1;
        HI = 0;
    }
    else if(ADRESH >= 0 && ADRESH < 50) {
        LO = 1;
        MID = 0;
        HI = 0;
    }
    else {
        LO = 0;
        MID = 0;
        HI = 0;
    }
}
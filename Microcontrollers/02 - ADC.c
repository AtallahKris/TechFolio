#include <p18cxxx.h>
#include <BCDlib.h>

char SScodes[] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F};
unsigned char i, Qstate;
unsigned int voltage;
char digits[5];

void setup(void);
void measureV(void);

void main(void) {
    setup();
    while(1) {
        measureV();
    }
}

void setup(void) {
    ANSELD = TRISD = 0x00;
    TRISA &= 0xF8;
    ANSELA &= 0xF8;
    TRISBbits.RB0 = ANSELBbits.ANSB0 = 1;
    ADCON0 = 0b00110001;
    ADCON1 = 0x00;
    ADCON2 = 0b10001001;
    INTCONbits.T0IE = 1;
    INTCONbits.GIE = 1;
    T0CON = 0b11010100;
    TMR0L = 256 - 125;
    i = 2;
    Qstate = 0b00000100;
}

#pragma code ISR = 0x0008
#pragma interrupt ISR

void ISR(void) {
    INTCONbits.T0IF = 0;
    TMR0L = 256 - 125;
    PORTD = 0x00;
    PORTA = Qstate;
    if(i == 2) {
        PORTD = (SScodes[digits[i++]] | 0x80);
    }
    else
        PORTD = SScodes[digits[i++]];
    Qstate >>= 1;
    if(i == 5) {
        i = 2;
        Qstate = 0b00000100;
    }
}

void measureV(void) {
    ADCON0bits.GO_DONE = 1;
    while(ADCON0bits.NOT_DONE);
    voltage = (((short long) ADRES * 500) / 1024);
    Bin2BcdE(voltage, digits);
}
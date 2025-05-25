#include <p18cxxx.h>

char SScodes[] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F};

unsigned char intcount, Qstates, i;
unsigned char counter;
char digits[3];

void Setup(void);

void main(void) {
    Setup();
    while(1);
}

void Setup(void) {
    TRISD = 0X00;
    ANSELD = 0X00;
    
    TRISA &= 0xF8;
    ANSELA &= 0XF8;
    
    INTCONbits.GIE = 1;
    INTCONbits.T0IE = 1;
    
    i = 0;
    intcount = 250;
    T0CON = 0b11010100;
    TMR0L = 256 - 125;
    
    Qstates = 0b00000100;
    
    digits[2] = counter % 10;
    digits[1] = (counter / 10) % 10;
    digits[0] = (counter / 100);
}

#pragma code ISR = 0x0008
#pragma interrupt ISR

void ISR(void) {
    INTCONbits.T0IF = 0;
    TMR0L = 256 - 125;
    
    PORTD = 0x00;
    PORTA = Qstates;
    PORTD = SScodes[digits[i]];

    Qstates >>= 1;
    i++;
    
    if(i == 3) {
        i = 0;
        Qstates = 0b00000100;
    }
    
    intcount--;
    if(intcount == 0) {
        intcount = 250;
        counter++;
        
        digits[2] = counter % 10;
        digits[1] = (counter / 10) % 10;
        digits[0] = (counter / 100);
    }
}

#include <p18cxxx.h>

char SScodes[] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F};

unsigned char intcount, Qstates, i;
unsigned int counter;
char digits[4];

void Setup(void);

void main(void) {
    Setup();
    while(1);
}

void Setup(void) {
    TRISD = 0X00;
    ANSELD = 0X00;
    
    TRISA &= 0xF0;
    ANSELA &= 0XF0;
    
    INTCONbits.GIE = 1;
    INTCONbits.T0IE = 1;
    
    i = 0;
    intcount = 250;
    T0CON = 0b11010100;
    TMR0L = 256 - 125;
    
    Qstates = 0b00001000;
    
    digits[3] = counter % 10;
    digits[2] = (counter / 10) % 10;
    digits[1] = (counter / 100) % 10;
    digits[0] = (counter / 1000);
}

#pragma code ISR = 0x0008
#pragma interrupt ISR

void ISR(void) {
    INTCONbits.T0IF = 0;
    TMR0L = 256 - 125;
    
    PORTD = 0x00;
    PORTA = Qstates;
    PORTD = SScodes[digits[i]];

    Qstates >>= 1;
    i++;
    
    if(i == 4) {
        i = 0;
        Qstates = 0b00001000;
    }
    
    intcount--;
    if(intcount == 0) {
        if(counter == 9999) {
            counter = 65535;
        }
        
        intcount = 250;
        counter++;
        
        digits[3] = counter % 10;
        digits[2] = (counter / 10) % 10;
        digits[1] = (counter / 100) % 10;
        digits[0] = (counter / 1000);
    }
}

#include <p18cxxx.h>
#include <delays.h>
#include <LCD4lib.h>
#include <EEPROM.h>

#define eeseconds 0x00
#define DEVICE PORTCbits.RC7
#define START PORTCbits.RC0
#define BUZZER PORTEbits.RE1

char seconds;
char digits[3];
unsigned int S, j;
unsigned char k;

void setup(void);
void IncDec(void);
void TurnOn(void);
void Beep(unsigned int S);

void main(void) {
    setup();
    IncDec();
    TurnOn();
}

void setup(void) {
    InitLCD();
    ANSELAbits.ANSA0 = 1;
    ANSELEbits.ANSE1 = 0;
    ANSELC &= 0x7E;
    TRISAbits.RA0 = 1;
    TRISCbits.RC0 = 1;
    TRISCbits.RC7 = 0;
    TRISEbits.RE1 = 0;
    ADCON0 = 0x01;
    ADCON1 = 0x00;
    ADCON2 = 0b00001001;
    DispRomStr(Ln1Ch0, (ROM)"Set T then start");
    DispRomStr(Ln2Ch0, (ROM)"Dev.Time:");
    ReadEE(eeseconds, &seconds);
    Bin2Asc(seconds, digits);
    DispVarStr(digits, Ln2Ch10, 3);
    DEVICE = 0;
    BUZZER = 0;
}

void Beep(unsigned int S) {
    for(j = 0; j < S; j++) {
        BUZZER = 1;
        Delay1KTCYx(1);
        BUZZER = 0;
        Delay1KTCYx(1);
    }
}

void TurnOn(void) {
    DEVICE = 1;
    Wrt2EE(seconds, eeseconds);
    DispRomStr(Ln1Ch0, (ROM)"Left time:");
    
    while(1) {
        Bin2Asc(seconds, digits);
        DispVarStr(digits, Ln1Ch10, 3);
        if(seconds == 0) {
            for(k = 0; k <= 2; k++) {
                Beep(500);
                Delay10KTCYx(100);
            }
            break;
        }
        seconds--;
        Delay10KTCYx(100);
        Wrt2EE(seconds, eeseconds);
    }
    DEVICE = 0;
    ReadEE(eeseconds, &seconds);
    Reset();
}

void IncDec(void) {
    while(1) {
        ADCON0bits.GO_DONE = 1;
        while(ADCON0bits.NOT_DONE);
        seconds = ADRESH;
        if(START) {
            if(seconds != 0) {
                while(START);
                break;
            }
        }
        Delay1KTCYx(5);
        Bin2Asc(seconds, digits);
        DispVarStr(digits, Ln2Ch10, 3);
    }
}
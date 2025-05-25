#include <p18f45k22.h>
#include <delays.h>

#define MOTOR_LEFT_FWD     LATDbits.LATD0
#define MOTOR_LEFT_REV     LATDbits.LATD1
#define MOTOR_RIGHT_FWD    LATDbits.LATD2
#define MOTOR_RIGHT_REV    LATDbits.LATD3

#define trigger            LATCbits.LATC0
#define echo               PORTCbits.RC3
#define IRR                PORTCbits.RC4
#define IRL                PORTCbits.RC5

#define RLR                LATAbits.LATA0
#define RLL                LATAbits.LATA1
#define BUZZER             LATAbits.LATA2
#define FWD_R              LATAbits.LATA3
#define FWD_L              LATAbits.LATA4

#define STOP_DISTANCE      20
#define SLOW_DISTANCE      40
#define MAX_SPEED          100
#define MIN_SPEED          60

#define SERVO_PIN          LATBbits.LATB5
#define SERVO_TRIS         TRISBbits.TRISB5

#pragma config FOSC = INTIO67

void setup(void);
void configureIO(void);
void configurePWM(void);
void delay_us(unsigned int us);
void delay_ms(unsigned int ms);
void delay_mss(unsigned int ms);
void setPWMDuty(unsigned char left, unsigned char right);
void setServoDegree(unsigned char angle);
void moveForward(unsigned char speed);
void moveBackward(unsigned char speed);
void turnLeft(unsigned char speed);
void turnRight(unsigned char speed);
void stopMotors(void);
unsigned int measureDistance(void);

unsigned int distance = 0;
unsigned int j = 0;

void main(void) {
    setup();
    stopMotors();
    delay_ms(1000);

    while (1) {
        setServoDegree(90);
        distance = measureDistance();

        if (distance < 4) {
            distance = 255;
        } else if (distance < 90 && distance > 5) {
            stopMotors();
            delay_ms(200);
            moveBackward(100);
            RLR = 1;
            RLL = 1;
            BUZZER = 1;
            delay_ms(150);

            stopMotors();
            delay_ms(200);

            for (j = 0; j < 20; j++) {
                setServoDegree(0);
                delay_mss(20);
            }

            distance = measureDistance();
            if (distance > 70 && IRR) {
                setServoDegree(90);
                turnRight(100);
                delay_ms(180);
                moveForward(100);
                delay_ms(200);
                RLL = 0;
            } else {
                setServoDegree(180);
                delay_mss(200);
                setServoDegree(180);
                delay_mss(200);
                distance = measureDistance();
                if (distance > 70 && IRL) {
                    setServoDegree(90);
                    turnLeft(100);
                    delay_ms(260);
                    moveForward(100);
                    delay_ms(200);
                    RLR = 0;
                } else {
                    turnRight(MAX_SPEED);
                    delay_ms(550);
                    stopMotors();
                    delay_ms(300);
                }
            }
            BUZZER = 0;
        } else if (distance >= 90 && distance < 300 && IRL && IRR) {
            moveForward(40);
        } else if (distance >= 90 && distance < 300 && IRL && IRR) {
            moveForward(40);
        } else if (!IRR) {
            turnLeft(100);
            delay_ms(130);
        } else if (!IRL) {
            turnRight(100);
            delay_ms(130);
        } else {
            RLR = 0;
            RLL = 0;
            moveForward(100);
        }
    }
}

void setup(void) {
    OSCCON = 0b01110000;
    OSCTUNEbits.PLLEN = 0;
    while (!OSCCONbits.HFIOFS);

    configureIO();
    configurePWM();

    T1CONbits.T1CKPS = 0b00;
    T1CONbits.TMR1CS = 0b00;
    T1CONbits.T1RD16 = 1;
    T1CONbits.TMR1ON = 0;

    SERVO_TRIS = 0;
    SERVO_PIN = 0;
}

void configureIO(void) {
    ANSELC = 0x00;
    TRISCbits.TRISC0 = 0;
    TRISCbits.TRISC3 = 1;
    TRISCbits.TRISC1 = 0;
    TRISCbits.TRISC2 = 0;
    ANSELCbits.ANSC2 = 0;
    TRISCbits.TRISC4 = 1;
    TRISCbits.TRISC5 = 1;

    TRISD &= 0xF0;
    LATD &= 0xF0;

    TRISB = 0x00;
    LATB = 0x00;
    LATA = 0x00;
    ANSELB = 0x00;

    TRISAbits.TRISA0 = 0;
    TRISAbits.TRISA1 = 0;
    TRISAbits.TRISA2 = 0;
    TRISAbits.TRISA3 = 0;
    TRISAbits.TRISA4 = 0;
}

void configurePWM(void) {
    PR2 = 199;
    T2CON = 0b00000101;

    CCPTMRS0bits.C1TSEL = 0b00;
    CCPTMRS0bits.C2TSEL = 0b00;

    CCP1CON = 0b00001100;
    CCP2CON = 0b00001100;

    CCPR1L = 0;
    CCP1CONbits.DC1B = 0;

    CCPR2L = 0;
    CCP2CONbits.DC2B = 0;
}

void delay_us(unsigned int us) {
    unsigned int i;
    for (i = 0; i < us; i++) {
        Nop();
    }
}

void delay_ms(unsigned int ms) {
    unsigned int i = 0;
    for (i = 0; i < ms; i++) {
        Delay1KTCYx(4);
    }
}

void delay_mss(unsigned int ms) {
    unsigned int i, j;
    for (i = 0; i < ms; i++) {
        for (j = 0; j < 1000; j++) {
            Nop();
        }
    }
}

void setPWMDuty(unsigned char left, unsigned char right) {
    unsigned int dutyR = 0;
    unsigned int dutyL = 0;
    if (left == 40 && right == 40) {
        dutyL = ((unsigned int) left * (PR2 + 1) * 4) / 9;
        CCPR1L = dutyL >> 2;
        CCP1CONbits.DC1B = dutyL & 0x03;

        dutyR = ((unsigned int) right * (PR2 + 1) * 4) / 9;
        CCPR2L = dutyR >> 2;
        CCP2CONbits.DC2B = dutyR & 0x03;
    } else {
        dutyL = ((unsigned int) left * (PR2 + 1) * 4) / 5;
        CCPR1L = dutyL >> 2;
        CCP1CONbits.DC1B = dutyL & 0x03;

        dutyR = ((unsigned int) right * (PR2 + 1) * 4) / 5;
        CCPR2L = dutyR >> 2;
        CCP2CONbits.DC2B = dutyR & 0x03;
    }
}

void setServoDegree(unsigned char angle) {
    unsigned int pulse_us = 0;

    if (angle == 0) {
        pulse_us = 90;
    } else if (angle == 90) {
        pulse_us = 270;
    } else if (angle == 180) {
        pulse_us = 365;
    }

    SERVO_PIN = 1;
    delay_us(pulse_us);
    SERVO_PIN = 0;
    delay_us(3625 - pulse_us);
}

void moveForward(unsigned char s) {
    MOTOR_LEFT_FWD = 1;
    MOTOR_LEFT_REV = 0;
    MOTOR_RIGHT_FWD = 1;
    MOTOR_RIGHT_REV = 0;
    setPWMDuty(s, s);
}

void moveBackward(unsigned char s) {
    MOTOR_LEFT_FWD = 0;
    MOTOR_LEFT_REV = 1;
    MOTOR_RIGHT_FWD = 0;
    MOTOR_RIGHT_REV = 1;
    setPWMDuty(s, s);
}

void turnLeft(unsigned char s) {
    MOTOR_LEFT_FWD = 0;
    MOTOR_LEFT_REV = 1;
    MOTOR_RIGHT_FWD = 1;
    MOTOR_RIGHT_REV = 0;
    setPWMDuty(s, s);
}

void turnRight(unsigned char s) {
    MOTOR_LEFT_FWD = 1;
    MOTOR_LEFT_REV = 0;
    MOTOR_RIGHT_FWD = 0;
    MOTOR_RIGHT_REV = 1;
    setPWMDuty(s, s);
}

void stopMotors(void) {
    MOTOR_LEFT_FWD = 0;
    MOTOR_LEFT_REV = 0;
    MOTOR_RIGHT_FWD = 0;
    MOTOR_RIGHT_REV = 0;
    setPWMDuty(0, 0);
}

unsigned int measureDistance(void) {
    unsigned int pulse_ticks = 0;
    unsigned int ddistance = 0;

    TMR1H = 0;
    TMR1L = 0;
    PIR1bits.TMR1IF = 0;
    trigger = 0;
    Nop();
    Nop();

    trigger = 1;
    Delay10TCYx(10);
    trigger = 0;

    while (!echo) {
    };

    T1CONbits.TMR1ON = 1;

    while (echo) {
    };

    T1CONbits.TMR1ON = 0;
    pulse_ticks = 0;

    pulse_ticks = (unsigned int) TMR1L;
    pulse_ticks = pulse_ticks | ((unsigned int) TMR1H << 8);

    return ddistance = pulse_ticks / 58;
}

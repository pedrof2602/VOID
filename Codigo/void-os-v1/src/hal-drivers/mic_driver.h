#pragma once
#include <Arduino.h>

class MicDriver {
public:
    void init();
    // Lee datos del mic y los guarda en tu buffer de 16 bits
    int read(int16_t* buffer, int length);
};
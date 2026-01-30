#include <Arduino.h>
#include "config.h"
#include "hal-drivers/mic_driver.h"

MicDriver microphone;
int16_t audioBuffer[BUFFER_SIZE];

void setup() {
    Serial.begin(115200);
    delay(2000);
    Serial.println("--- VOID OS: INTENTO 32 BITS ---");

    microphone.init();
}

void loop() {
    // Pedimos 64 muestras (buffer pequeño para probar)
    int bytes = microphone.read(audioBuffer, 64);

    if (bytes > 0) {
        // Solo imprimimos si NO es cero (para detectar vida)
        int16_t muestra = audioBuffer[0];
        
        if (muestra != 0 && muestra != -1) {
            Serial.print("SONIDO DETECTADO: ");
            Serial.println(muestra);
        } else {
            // Imprime un punto para saber que el loop corre
            Serial.print("."); 
        }
    }
    // Sin delay para no perder sincronía
}
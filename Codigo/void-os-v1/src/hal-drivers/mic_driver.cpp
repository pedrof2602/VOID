#include "mic_driver.h"
#include <driver/i2s.h>
#include "../config.h"

#define I2S_PORT I2S_NUM_0

void MicDriver::init() {
    // 1. Configuración FIX 32 BITS (Truco de Reddit)
    const i2s_config_t i2s_config = {
        .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        // OBLIGAMOS AL ESP32 A MANDAR 64 PULSOS DE RELOJ:
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, 
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT, // Si sigue en 0, cambia a ONLY_RIGHT aquí
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 64,
        .use_apll = true, // Reloj estable activado
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    const i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK,
        .ws_io_num = I2S_WS,
        .data_out_num = -1,
        .data_in_num = I2S_SD
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);
    
    Serial.println("[HAL] Micrófono (Modo 32-bit Hack) Inicializado");
}

int MicDriver::read(int16_t* output_buffer, int length) {
    size_t bytesIn = 0;
    
    // Buffer temporal de 32 bits (4 bytes por muestra)
    // Como queremos devolver 'length' muestras de 16 bits, leemos 'length' de 32 bits.
    int32_t temp_buffer[length]; 

    // Leemos del hardware en 32 bits
    esp_err_t result = i2s_read(I2S_PORT, temp_buffer, length * sizeof(int32_t), &bytesIn, portMAX_DELAY);
    
    if (result == ESP_OK && bytesIn > 0) {
        int muestras_leidas = bytesIn / sizeof(int32_t);

        // CONVERSIÓN: 32 bits -> 16 bits
        for (int i = 0; i < muestras_leidas; i++) {
            // El INMP441 pone los datos en los bits altos. 
            // Desplazamos 14 bits a la derecha para bajar el volumen y que quepa en 16 bits.
            output_buffer[i] = (int16_t)(temp_buffer[i] >> 14);
        }
        
        // Devolvemos la cantidad de bytes ÚTILES (16 bits) que generamos
        return muestras_leidas * sizeof(int16_t);
    } 
    
    return -1;
}
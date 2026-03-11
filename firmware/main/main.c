#include <stdio.h>
#include <stdlib.h>
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "PHASE1_ADC";

// Cấu hình ADC
#define ADC_UNIT            ADC_UNIT_1
#define ADC_CHAN            ADC_CHANNEL_3 //GPIO 4
#define SAMPLE_COUNT        200           //Số mẫu cho mỗi cửa sổ AI

void app_main(void) {
    //Khởi tạo ADC Unit
    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t init_cfg = { .unit_id = ADC_UNIT };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_cfg, &adc_handle));

    //Cấu hình Channel
    adc_oneshot_chan_cfg_t chan_cfg = {
        .bitwidth = ADC_BITWIDTH_12, //12-bit (0-4095)
        .atten = ADC_ATTEN_DB_12,    //Đo dải 0-3.3V
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, ADC_CHAN, &chan_cfg));

    //Cấp phát bộ nhớ
    int *raw_audio_data = (int *)malloc(SAMPLE_COUNT * sizeof(int));
    
    if (raw_audio_data == NULL) {
        ESP_LOGE(TAG, "Lỗi cấp phát bộ nhớ!");
        return;
    }

    ESP_LOGI(TAG, "Đã khởi tạo vùng nhớ tại địa chỉ: %p", raw_audio_data);

    while (1) {
        //Thu thập dữ liệu vào vùng nhớ mà con trỏ đang trỏ tới
        for (int i = 0; i < SAMPLE_COUNT; i++) {
            adc_oneshot_read(adc_handle, ADC_CHAN, &raw_audio_data[i]);
            
            //In ra định dạng đơn giản để Edge Impulse thu thập sau này
            printf("%d\n", raw_audio_data[i]);
            
            //Tần số lấy mẫu khoảng 1kHz để demo
            vTaskDelay(pdMS_TO_TICKS(1)); 
        }
        
        ESP_LOGD(TAG, "Đã thu thập xong 1 batch dữ liệu.");
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
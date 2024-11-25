void task1(void *pvParameter) {
while(1) {
gpio_set_level(GPIO_NUM_2, 1); // Светодиод 1
vTaskDelay(500 / portTICK_PERIOD_MS);
gpio_set_level(GPIO_NUM_2, 0);
vTaskDelay(500 / portTICK_PERIOD_MS);
}
}

void task2(void *pvParameter) {
while(1) {
gpio_set_level(GPIO_NUM_4, 1); // Светодиод 2
vTaskDelay(1000 / portTICK_PERIOD_MS);
gpio_set_level(GPIO_NUM_4, 0);
vTaskDelay(1000 / portTICK_PERIOD_MS);
}
}

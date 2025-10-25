package com.example.weather_app.service;

import com.example.weather_app.model.WeatherData;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class WeatherService {

    @Value("${openweather.api.key}") // Используем ваше имя свойства
    private String apiKey;

    @Value("${openweather.api.url}") // Используем ваше имя свойства
    private String apiUrl;

    private final WebClient webClient;

    public WeatherService() {
        this.webClient = WebClient.builder().build();
    }

    public Mono<WeatherData> getWeatherByCity(String city, String countryCode) {
        String url = String.format(
                "%s/weather?q=%s,%s&appid=%s&units=metric&lang=ru",
                apiUrl, city, countryCode, apiKey
        );

        return webClient.get()
                .uri(url)
                .retrieve()
                .bodyToMono(WeatherData.class);
    }
}
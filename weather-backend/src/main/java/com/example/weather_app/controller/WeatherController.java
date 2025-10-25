package com.example.weather_app.controller;

import com.example.weather_app.model.WeatherData;
import com.example.weather_app.service.WeatherService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/weather")
@CrossOrigin(origins = "*")
public class WeatherController {

    private final WeatherService weatherService;

    public WeatherController(WeatherService weatherService) {
        this.weatherService = weatherService;
    }

    @GetMapping("/{city},{countryCode}")
    public Mono<ResponseEntity<Map<String, Object>>> getWeather(
            @PathVariable String city,
            @PathVariable String countryCode) {

        return weatherService.getWeatherByCity(city, countryCode)
                .map(weather -> ResponseEntity.ok(createWeatherResponse(weather)))
                .onErrorResume(error -> {
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("error", "Не удалось получить данные о погоде для: " + city + "," + countryCode + ". " + error.getMessage());
                    return Mono.just(ResponseEntity.badRequest().body(errorResponse));
                });
    }

    @GetMapping("/")
    public String home(@RequestParam(required = false) String user) {
        return "Welcome " + (user != null ? user : "Guest") + " to Weather Service!";
    }

    @GetMapping("/test")
    public Map<String, String> test() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "Weather service is running");
        response.put("timestamp", java.time.LocalDateTime.now().toString());
        return response;
    }

    @GetMapping("/current")
    public Mono<ResponseEntity<Map<String, Object>>> getCurrentWeather(
            @RequestParam String city,
            @RequestParam String countryCode) {

        return weatherService.getWeatherByCity(city, countryCode)
                .map(weather -> ResponseEntity.ok(createWeatherResponse(weather)))
                .onErrorResume(error -> {
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("error", "Не удалось получить данные о погоде");
                    return Mono.just(ResponseEntity.badRequest().body(errorResponse));
                });
    }

    private Map<String, Object> createWeatherResponse(WeatherData weather) {
        Map<String, Object> response = new HashMap<>();

        // Безопасный доступ к данным
        response.put("city", weather.getName() != null ? weather.getName() : "Unknown");

        if (weather.getMain() != null) {
            response.put("temperature", Math.round(weather.getMain().getTemp()));
            response.put("humidity", weather.getMain().getHumidity());
            response.put("pressure", weather.getMain().getPressure());
        } else {
            response.put("temperature", 0);
            response.put("humidity", 0);
            response.put("pressure", 0);
        }

        if (weather.getWeather() != null && weather.getWeather().length > 0) {
            response.put("description", weather.getWeather()[0].getDescription());
            response.put("icon", weather.getWeather()[0].getIcon());
        } else {
            response.put("description", "No data");
            response.put("icon", "01d");
        }

        if (weather.getWind() != null) {
            response.put("windSpeed", weather.getWind().getSpeed());
        } else {
            response.put("windSpeed", 0.0);
        }

        if (weather.getSys() != null) {
            response.put("country", weather.getSys().getCountry());
        } else {
            response.put("country", "N/A");
        }

        return response;
    }
}
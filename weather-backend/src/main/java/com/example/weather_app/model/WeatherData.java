package com.example.weather_app.model;


import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WeatherData {
    private String name;

    @JsonProperty("main")
    private MainData main;

    @JsonProperty("weather")
    private WeatherDescription[] weather;

    @JsonProperty("wind")
    private Wind wind;

    @JsonProperty("sys")
    private Sys sys;

    // Геттеры и сеттеры
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public MainData getMain() { return main; }
    public void setMain(MainData main) { this.main = main; }

    public WeatherDescription[] getWeather() { return weather; }
    public void setWeather(WeatherDescription[] weather) { this.weather = weather; }

    public Wind getWind() { return wind; }
    public void setWind(Wind wind) { this.wind = wind; }

    public Sys getSys() { return sys; }
    public void setSys(Sys sys) { this.sys = sys; }

    // ВНУТРЕННИЕ СТАТИЧЕСКИЕ КЛАССЫ
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class MainData {
        @JsonProperty("temp")
        private Double temp;

        @JsonProperty("humidity")
        private Integer humidity;

        @JsonProperty("pressure")
        private Double pressure;

        public Double getTemp() {
            return temp != null ? temp : 0.0;
        }
        public void setTemp(Double temp) { this.temp = temp; }

        public Integer getHumidity() {
            return humidity != null ? humidity : 0;
        }
        public void setHumidity(Integer humidity) { this.humidity = humidity; }

        public Double getPressure() {
            return pressure != null ? pressure : 0.0;
        }
        public void setPressure(Double pressure) { this.pressure = pressure; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class WeatherDescription {
        @JsonProperty("main")
        private String main;

        @JsonProperty("description")
        private String description;

        @JsonProperty("icon")
        private String icon;

        public String getMain() {
            return main != null ? main : "N/A";
        }
        public void setMain(String main) { this.main = main; }

        public String getDescription() {
            return description != null ? description : "N/A";
        }
        public void setDescription(String description) { this.description = description; }

        public String getIcon() {
            return icon != null ? icon : "01d";
        }
        public void setIcon(String icon) { this.icon = icon; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Wind {
        @JsonProperty("speed")
        private Double speed;

        public Double getSpeed() {
            return speed != null ? speed : 0.0;
        }
        public void setSpeed(Double speed) { this.speed = speed; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Sys {
        @JsonProperty("country")
        private String country;

        public String getCountry() {
            return country != null ? country : "N/A";
        }
        public void setCountry(String country) { this.country = country; }
    }
}
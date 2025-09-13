package com.fooddelivery;

import java.util.ArrayList;
import java.util.List;

public class Restaurant {
    private String name;
    private String cuisine;
    private float rating;
    private String address;
    private double latitude;
    private double longitude;

    public Restaurant(String name, String cuisine, float rating, String address) {
        this.name = name;
        this.cuisine = cuisine;
        this.rating = rating;
        this.address = address;
        // For simplicity, we'll generate random coordinates near St. Petersburg
        this.latitude = 59.934280 + (Math.random() - 0.5) * 0.1;
        this.longitude = 30.335098 + (Math.random() - 0.5) * 0.1;
    }

    // Getters
    public String getName() {
        return name;
    }

    public String getCuisine() {
        return cuisine;
    }

    public float getRating() {
        return rating;
    }

    public String getAddress() {
        return address;
    }

    public double getLatitude() {
        return latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    // Setters
    public void setName(String name) {
        this.name = name;
    }

    public void setCuisine(String cuisine) {
        this.cuisine = cuisine;
    }

    public void setRating(float rating) {
        this.rating = rating;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }
    
    public static List<Restaurant> getAllRestaurants() {
        List<Restaurant> restaurants = new ArrayList<>();
        // Adding sample restaurants with fixed coordinates for consistency
        restaurants.add(new Restaurant("Пицца Хат", "Итальянская кухня", 4.5f, "ул. Большая Конюшенная, 12"));
        restaurants.add(new Restaurant("Суши Лав", "Японская кухня", 4.7f, "Невский проспект, 45"));
        restaurants.add(new Restaurant("Бургер Кинг", "Американская кухня", 4.2f, "Лиговский проспект, 67"));
        restaurants.add(new Restaurant("Точка Еды", "Русская кухня", 4.6f, "Ленина улица, 89"));
        restaurants.add(new Restaurant("Вкусно и Точка", "Европейская кухня", 4.3f, "Гороховая улица, 34"));
        restaurants.add(new Restaurant("Додо Пицца", "Итальянская кухня", 4.8f, "Петергофское шоссе, 56"));
        restaurants.add(new Restaurant("Китайский Дворик", "Китайская кухня", 4.4f, "Московский проспект, 78"));
        restaurants.add(new Restaurant("Макдоналдс", "Фастфуд", 4.1f, "Невский проспект, 102"));
        
        // Set fixed coordinates for consistency
        restaurants.get(0).setLatitude(59.933564);
        restaurants.get(0).setLongitude(30.317252);
        restaurants.get(1).setLatitude(59.934770);
        restaurants.get(1).setLongitude(30.328436);
        restaurants.get(2).setLatitude(59.929827);
        restaurants.get(2).setLongitude(30.341585);
        restaurants.get(3).setLatitude(59.941262);
        restaurants.get(3).setLongitude(30.315867);
        restaurants.get(4).setLatitude(59.938743);
        restaurants.get(4).setLongitude(30.321523);
        restaurants.get(5).setLatitude(59.918406);
        restaurants.get(5).setLongitude(30.330259);
        restaurants.get(6).setLatitude(59.930245);
        restaurants.get(6).setLongitude(30.356384);
        restaurants.get(7).setLatitude(59.936272);
        restaurants.get(7).setLongitude(30.362167);
        
        return restaurants;
    }
}
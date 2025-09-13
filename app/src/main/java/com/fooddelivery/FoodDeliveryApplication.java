package com.fooddelivery;

import android.app.Application;
import java.util.ArrayList;
import java.util.List;

public class FoodDeliveryApplication extends Application {
    private List<Restaurant> restaurants;
    
    @Override
    public void onCreate() {
        super.onCreate();
        initializeRestaurants();
    }
    
    private void initializeRestaurants() {
        restaurants = new ArrayList<>();
        // Инициализируем список всех ресторанов
        restaurants.add(new Restaurant("Пицца Хат", "Итальянская кухня", 4.5f, "ул. Большая Конюшенная, 12"));
        restaurants.add(new Restaurant("Суши Лав", "Японская кухня", 4.7f, "Невский проспект, 45"));
        restaurants.add(new Restaurant("Бургер Кинг", "Американская кухня", 4.2f, "Лиговский проспект, 67"));
        restaurants.add(new Restaurant("Точка Еды", "Русская кухня", 4.6f, "Ленина улица, 89"));
        restaurants.add(new Restaurant("Вкусно и Точка", "Европейская кухня", 4.3f, "Гороховая улица, 34"));
        restaurants.add(new Restaurant("Додо Пицца", "Итальянская кухня", 4.8f, "Петергофское шоссе, 56"));
        restaurants.add(new Restaurant("Китайский Дворик", "Китайская кухня", 4.4f, "Московский проспект, 78"));
        restaurants.add(new Restaurant("Макдоналдс", "Фастфуд", 4.1f, "Невский проспект, 102"));
    }
    
    public List<Restaurant> getRestaurants() {
        return restaurants;
    }
}
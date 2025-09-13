package com.fooddelivery;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.lang.StringBuilder;
import java.util.List;

public class YandexMapWebActivity extends AppCompatActivity {
    private WebView webView;
    private Button confirmOrderButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_yandex_map_web);

        initViews();
        setupWebView();
    }

    private void initViews() {
        webView = findViewById(R.id.webview);
        confirmOrderButton = findViewById(R.id.confirm_order_button);
        
        confirmOrderButton.setOnClickListener(v -> {
            // Clear cart and show confirmation
            CartManager.getInstance().clearCart();
            Toast.makeText(this, "Заказ подтвержден! Ожидайте доставку.", Toast.LENGTH_LONG).show();
            finish(); // Close this activity and return to previous
        });
    }

    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        webSettings.setSupportZoom(true);
        
        webView.setWebViewClient(new WebViewClient());
        
        // Генерируем URL для Yandex Maps с маркерами ресторанов
        String mapUrl = generateYandexMapUrl();
        webView.loadUrl(mapUrl);
    }
    
    private String generateYandexMapUrl() {
        // Получаем выбранный ресторан
        CartManager cartManager = CartManager.getInstance();
        Restaurant selectedRestaurant = cartManager.getRestaurant();
        
        // Базовый URL Yandex Maps
        StringBuilder urlBuilder = new StringBuilder("https://yandex.ru/maps/?ll=30.3158,59.9343&z=12");
        
        // Добавляем маркер пользователя
        urlBuilder.append("&pt=30.335098,59.934280,pm2rdl");
        
        // Добавляем маркеры всех ресторанов
        List<Restaurant> allRestaurants = Restaurant.getAllRestaurants();
        for (Restaurant restaurant : allRestaurants) {
            // Формат: долгота,широта,цвет_метки
            urlBuilder.append("~")
                    .append(restaurant.getLongitude())
                    .append(",")
                    .append(restaurant.getLatitude())
                    .append(",pm2orgl");
        }
        
        // Если есть выбранный ресторан, добавляем маршрут
        if (selectedRestaurant != null) {
            urlBuilder.append("&rtext=59.934280,30.335098~")
                    .append(selectedRestaurant.getLatitude())
                    .append(",")
                    .append(selectedRestaurant.getLongitude());
        }
        
        return urlBuilder.toString();
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
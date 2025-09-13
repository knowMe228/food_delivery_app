package com.fooddelivery;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private RecyclerView restaurantRecyclerView;
    private RestaurantAdapter restaurantAdapter;
    private List<Restaurant> restaurantList;
    private Button cartButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupRestaurantList();
        setupRecyclerView();
    }

    private void initViews() {
        restaurantRecyclerView = findViewById(R.id.restaurant_recycler_view);
        cartButton = findViewById(R.id.cart_button);
        cartButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, CartActivity.class);
                startActivity(intent);
            }
        });
    }

    private void setupRestaurantList() {
        // Используем статический метод для получения списка ресторанов
        restaurantList = Restaurant.getAllRestaurants();
    }

    private void setupRecyclerView() {
        restaurantAdapter = new RestaurantAdapter(restaurantList, this);
        restaurantRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        restaurantRecyclerView.setAdapter(restaurantAdapter);
    }

    public void onCartButtonClick(View view) {
        Intent intent = new Intent(this, CartActivity.class);
        startActivity(intent);
    }
}
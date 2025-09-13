package com.fooddelivery;

import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;

public class RestaurantDetailActivity extends AppCompatActivity {
    private TextView restaurantNameTextView;
    private TextView restaurantCuisineTextView;
    private TextView restaurantRatingTextView;
    private TextView restaurantAddressTextView;
    private RecyclerView menuRecyclerView;
    private MenuAdapter menuAdapter;
    private List<MenuItem> menuList;
    private Button addToCartButton;
    private Restaurant restaurant;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_restaurant_detail);

        initViews();
        getRestaurantData();
        setupMenuList();
        setupRecyclerView();
    }

    private void initViews() {
        restaurantNameTextView = findViewById(R.id.detail_restaurant_name);
        restaurantCuisineTextView = findViewById(R.id.detail_restaurant_cuisine);
        restaurantRatingTextView = findViewById(R.id.detail_restaurant_rating);
        restaurantAddressTextView = findViewById(R.id.detail_restaurant_address);
        menuRecyclerView = findViewById(R.id.menu_recycler_view);
        addToCartButton = findViewById(R.id.add_to_cart_button);
    }

    private void getRestaurantData() {
        // Get data from intent
        String name = getIntent().getStringExtra("restaurant_name");
        String cuisine = getIntent().getStringExtra("restaurant_cuisine");
        float rating = getIntent().getFloatExtra("restaurant_rating", 0);
        String address = getIntent().getStringExtra("restaurant_address");
        double latitude = getIntent().getDoubleExtra("restaurant_latitude", 0);
        double longitude = getIntent().getDoubleExtra("restaurant_longitude", 0);
        
        restaurant = new Restaurant(name, cuisine, rating, address);
        restaurant.setLatitude(latitude);
        restaurant.setLongitude(longitude);
        
        // Set data to views
        restaurantNameTextView.setText(restaurant.getName());
        restaurantCuisineTextView.setText(restaurant.getCuisine());
        restaurantRatingTextView.setText(String.valueOf(restaurant.getRating()));
        restaurantAddressTextView.setText(restaurant.getAddress());
    }

    private void setupMenuList() {
        menuList = new ArrayList<>();
        // Adding sample menu items
        menuList.add(new MenuItem("Маргарита", "Классическая пицца с томатами и моцареллой", 450.0, 1));
        menuList.add(new MenuItem("Пепперони", "Пицца с пепперони и сыром", 520.0, 1));
        menuList.add(new MenuItem("Четыре сыра", "Пицца с четырьмя видами сыра", 580.0, 1));
        menuList.add(new MenuItem("Гавайская", "Пицца с ветчиной и ананасами", 500.0, 1));
        menuList.add(new MenuItem("Вегетарианская", "Пицца с овощами", 480.0, 1));
        menuList.add(new MenuItem("Кола", "0.5л", 120.0, 2));
        menuList.add(new MenuItem("Фанта", "0.5л", 120.0, 2));
        menuList.add(new MenuItem("Сок", "Апельсиновый, 0.3л", 150.0, 2));
    }

    private void setupRecyclerView() {
        menuAdapter = new MenuAdapter(menuList, this);
        menuRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        menuRecyclerView.setAdapter(menuAdapter);
        
        addToCartButton.setOnClickListener(v -> {
            List<MenuItem> selectedItems = menuAdapter.getSelectedItems();
            if (selectedItems.isEmpty()) {
                Toast.makeText(this, "Выберите хотя бы один пункт меню", Toast.LENGTH_SHORT).show();
            } else {
                // Add selected items to cart
                CartManager.getInstance().addItems(selectedItems, restaurant);
                Toast.makeText(this, "Товары добавлены в корзину", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
package com.fooddelivery;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CartActivity extends AppCompatActivity {
    private RecyclerView cartRecyclerView;
    private CartAdapter cartAdapter;
    private List<CartItem> cartItems;
    private TextView totalPriceTextView;
    private Button checkoutButton;
    private CartManager cartManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cart);

        initViews();
        setupCart();
        setupRecyclerView();
    }

    private void initViews() {
        cartRecyclerView = findViewById(R.id.cart_recycler_view);
        totalPriceTextView = findViewById(R.id.total_price_text_view);
        checkoutButton = findViewById(R.id.checkout_button);
    }

    private void setupCart() {
        cartManager = CartManager.getInstance();
        cartItems = cartManager.getCartItems();
        
        // Update total price
        updateTotalPrice();
        
        checkoutButton.setOnClickListener(v -> {
            if (cartItems.isEmpty()) {
                Toast.makeText(this, "Корзина пуста", Toast.LENGTH_SHORT).show();
            } else {
                Intent intent = new Intent(this, YandexMapWebActivity.class);
                startActivity(intent);
            }
        });
    }

    private void setupRecyclerView() {
        cartAdapter = new CartAdapter(cartItems, this);
        cartRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        cartRecyclerView.setAdapter(cartAdapter);
    }

    private void updateTotalPrice() {
        double totalPrice = cartManager.getTotalPrice();
        totalPriceTextView.setText("Итого: " + String.format("%.2f", totalPrice) + " руб.");
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Refresh the cart when returning to this activity
        if (cartAdapter != null) {
            cartAdapter.notifyDataSetChanged();
            updateTotalPrice();
        }
    }
}
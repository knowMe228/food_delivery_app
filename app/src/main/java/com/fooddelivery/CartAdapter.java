package com.fooddelivery;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CartAdapter extends RecyclerView.Adapter<CartAdapter.CartViewHolder> {
    private List<CartItem> cartItems;
    private Context context;

    public CartAdapter(List<CartItem> cartItems, Context context) {
        this.cartItems = cartItems;
        this.context = context;
    }

    @NonNull
    @Override
    public CartViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_cart, parent, false);
        return new CartViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CartViewHolder holder, int position) {
        CartItem cartItem = cartItems.get(position);
        MenuItem menuItem = cartItem.getMenuItem();
        
        holder.nameTextView.setText(menuItem.getName());
        holder.quantityTextView.setText("Количество: " + String.valueOf(cartItem.getQuantity()));
        double totalPrice = menuItem.getPrice() * cartItem.getQuantity();
        holder.priceTextView.setText(String.format("%.2f", totalPrice) + " руб.");
    }

    @Override
    public int getItemCount() {
        return cartItems.size();
    }

    public static class CartViewHolder extends RecyclerView.ViewHolder {
        TextView nameTextView, quantityTextView, priceTextView;

        public CartViewHolder(@NonNull View itemView) {
            super(itemView);
            nameTextView = itemView.findViewById(R.id.cart_item_name);
            quantityTextView = itemView.findViewById(R.id.cart_item_quantity);
            priceTextView = itemView.findViewById(R.id.cart_item_price);
        }
    }
}
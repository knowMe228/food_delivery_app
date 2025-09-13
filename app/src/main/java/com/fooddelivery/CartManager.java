package com.fooddelivery;

import java.util.ArrayList;
import java.util.List;

public class CartManager {
    private static CartManager instance;
    private List<CartItem> cartItems;
    private Restaurant restaurant;

    private CartManager() {
        cartItems = new ArrayList<>();
    }

    public static synchronized CartManager getInstance() {
        if (instance == null) {
            instance = new CartManager();
        }
        return instance;
    }

    public void addItems(List<MenuItem> menuItems, Restaurant restaurant) {
        this.restaurant = restaurant;
        for (MenuItem menuItem : menuItems) {
            if (menuItem.getQuantity() > 0) {
                // Check if item already exists in cart
                boolean found = false;
                for (CartItem cartItem : cartItems) {
                    if (cartItem.getMenuItem().getName().equals(menuItem.getName())) {
                        cartItem.setQuantity(cartItem.getQuantity() + menuItem.getQuantity());
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    cartItems.add(new CartItem(menuItem, menuItem.getQuantity()));
                }
            }
        }
    }

    public List<CartItem> getCartItems() {
        return cartItems;
    }

    public Restaurant getRestaurant() {
        return restaurant;
    }
    
    public void setRestaurant(Restaurant restaurant) {
        this.restaurant = restaurant;
    }

    public double getTotalPrice() {
        double total = 0;
        for (CartItem item : cartItems) {
            total += item.getMenuItem().getPrice() * item.getQuantity();
        }
        return total;
    }

    public void clearCart() {
        cartItems.clear();
    }

    public int getItemCount() {
        int count = 0;
        for (CartItem item : cartItems) {
            count += item.getQuantity();
        }
        return count;
    }
}
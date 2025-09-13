package com.fooddelivery;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;

public class MenuAdapter extends RecyclerView.Adapter<MenuAdapter.MenuViewHolder> {
    private List<MenuItem> menuList;
    private Context context;

    public MenuAdapter(List<MenuItem> menuList, Context context) {
        this.menuList = menuList;
        this.context = context;
    }

    @NonNull
    @Override
    public MenuViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_menu, parent, false);
        return new MenuViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MenuViewHolder holder, int position) {
        MenuItem menuItem = menuList.get(position);
        holder.nameTextView.setText(menuItem.getName());
        holder.descriptionTextView.setText(menuItem.getDescription());
        holder.priceTextView.setText(String.valueOf(menuItem.getPrice()) + " руб.");

        // Set quantity
        holder.quantityTextView.setText(String.valueOf(menuItem.getQuantity()));

        // Set up button listeners
        holder.addButton.setOnClickListener(v -> {
            menuItem.incrementQuantity();
            holder.quantityTextView.setText(String.valueOf(menuItem.getQuantity()));
        });

        holder.removeButton.setOnClickListener(v -> {
            menuItem.decrementQuantity();
            holder.quantityTextView.setText(String.valueOf(menuItem.getQuantity()));
        });
    }

    @Override
    public int getItemCount() {
        return menuList.size();
    }

    public List<MenuItem> getSelectedItems() {
        List<MenuItem> selectedItems = new ArrayList<>();
        for (MenuItem item : menuList) {
            if (item.getQuantity() > 0) {
                selectedItems.add(item);
            }
        }
        return selectedItems;
    }

    public static class MenuViewHolder extends RecyclerView.ViewHolder {
        TextView nameTextView, descriptionTextView, priceTextView, quantityTextView;
        Button addButton, removeButton;

        public MenuViewHolder(@NonNull View itemView) {
            super(itemView);
            nameTextView = itemView.findViewById(R.id.menu_item_name);
            descriptionTextView = itemView.findViewById(R.id.menu_item_description);
            priceTextView = itemView.findViewById(R.id.menu_item_price);
            quantityTextView = itemView.findViewById(R.id.quantity_text_view);
            addButton = itemView.findViewById(R.id.add_button);
            removeButton = itemView.findViewById(R.id.remove_button);
        }
    }
}
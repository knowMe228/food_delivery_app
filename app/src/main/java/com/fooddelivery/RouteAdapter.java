package com.fooddelivery;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

public class RouteAdapter extends RecyclerView.Adapter<RouteAdapter.RouteViewHolder> {
    private RoutePoint userPoint;
    private RoutePoint restaurantPoint;
    private Context context;

    public RouteAdapter(RoutePoint userPoint, RoutePoint restaurantPoint, Context context) {
        this.userPoint = userPoint;
        this.restaurantPoint = restaurantPoint;
        this.context = context;
    }

    @NonNull
    @Override
    public RouteViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_route, parent, false);
        return new RouteViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull RouteViewHolder holder, int position) {
        if (position == 0) {
            holder.pointNameTextView.setText(userPoint.getName());
            holder.pointAddressTextView.setText("Координаты: " + String.format("%.6f", userPoint.getLatitude()) + ", " + String.format("%.6f", userPoint.getLongitude()));
        } else {
            holder.pointNameTextView.setText(restaurantPoint.getName());
            holder.pointAddressTextView.setText(restaurantPoint.getName() + " (" + String.format("%.6f", restaurantPoint.getLatitude()) + ", " + String.format("%.6f", restaurantPoint.getLongitude()) + ")");
        }
    }

    @Override
    public int getItemCount() {
        return 2; // User location and restaurant location
    }

    public static class RouteViewHolder extends RecyclerView.ViewHolder {
        TextView pointNameTextView, pointAddressTextView;

        public RouteViewHolder(@NonNull View itemView) {
            super(itemView);
            pointNameTextView = itemView.findViewById(R.id.point_name);
            pointAddressTextView = itemView.findViewById(R.id.point_address);
        }
    }
}
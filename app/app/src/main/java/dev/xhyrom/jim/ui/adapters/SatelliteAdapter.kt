package dev.xhyrom.jim.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import dev.xhyrom.jim.R
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.databinding.ItemSatelliteBinding

class SatelliteAdapter(private val onItemClick: (Satellite) -> Unit) :
    ListAdapter<Satellite, SatelliteAdapter.ViewHolder>(SatelliteDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemSatelliteBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ViewHolder(private val binding: ItemSatelliteBinding) :
        RecyclerView.ViewHolder(binding.root) {

        init {
            binding.root.setOnClickListener {
                val position = adapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onItemClick(getItem(position))
                }
            }
        }

        fun bind(satellite: Satellite) {
            binding.textSatelliteName.text = satellite.name
            binding.textSatelliteIp.text = satellite.ipAddress

            binding.connectionStatus.setImageResource(R.drawable.ic_connected)
        }
    }

    private class SatelliteDiffCallback : DiffUtil.ItemCallback<Satellite>() {
        override fun areItemsTheSame(oldItem: Satellite, newItem: Satellite): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Satellite, newItem: Satellite): Boolean {
            return oldItem == newItem
        }
    }
}
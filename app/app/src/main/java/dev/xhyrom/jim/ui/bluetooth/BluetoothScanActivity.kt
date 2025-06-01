package dev.xhyrom.jim.ui.bluetooth

import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import dev.xhyrom.jim.data.BluetoothDevice
import dev.xhyrom.jim.databinding.ActivityBluetoothBinding
import dev.xhyrom.jim.databinding.ItemBluetoothDeviceBinding

class BluetoothScanActivity : AppCompatActivity() {

    private lateinit var binding: ActivityBluetoothBinding
    private lateinit var viewModel: BluetoothViewModel
    private lateinit var adapter: BluetoothDeviceAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityBluetoothBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this).get(BluetoothViewModel::class.java)

        setupRecyclerView()
        setupObservers()
        setupClickListeners()

        // Start scanning for devices
        viewModel.scanForDevices()
    }

    private fun setupRecyclerView() {
        adapter = BluetoothDeviceAdapter { device ->
            viewModel.pairWithDevice(device)
        }
        binding.recyclerDevices.layoutManager = LinearLayoutManager(this)
        binding.recyclerDevices.adapter = adapter
    }

    private fun setupObservers() {
        viewModel.devices.observe(this) { devices ->
            adapter.submitList(devices)
            binding.emptyView.visibility = if (devices.isEmpty()) View.VISIBLE else View.GONE
        }

        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            binding.buttonScan.isEnabled = !isLoading
        }

        viewModel.errorMessage.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_LONG).show()
            }
        }

        viewModel.pairingStatus.observe(this) { success ->
            val message = if (success) "Device paired successfully" else "Failed to pair device"
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupClickListeners() {
        binding.buttonScan.setOnClickListener {
            viewModel.scanForDevices()
        }
    }

    inner class BluetoothDeviceAdapter(private val onPairClick: (BluetoothDevice) -> Unit) :
        RecyclerView.Adapter<BluetoothDeviceAdapter.DeviceViewHolder>() {

        private var devices = listOf<BluetoothDevice>()

        fun submitList(newDevices: List<BluetoothDevice>) {
            devices = newDevices
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DeviceViewHolder {
            val binding = ItemBluetoothDeviceBinding.inflate(
                layoutInflater, parent, false
            )
            return DeviceViewHolder(binding)
        }

        override fun onBindViewHolder(holder: DeviceViewHolder, position: Int) {
            holder.bind(devices[position])
        }

        override fun getItemCount() = devices.size

        inner class DeviceViewHolder(private val binding: ItemBluetoothDeviceBinding) :
            RecyclerView.ViewHolder(binding.root) {

            fun bind(device: BluetoothDevice) {
                binding.deviceName.text = device.name
                binding.deviceAddress.text = device.address
                binding.deviceType.text = device.type

                binding.buttonPair.setOnClickListener {
                    onPairClick(device)
                }
            }
        }
    }
}
package dev.xhyrom.jim.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import dev.xhyrom.jim.data.database.AppDatabase
import dev.xhyrom.jim.data.repository.SatelliteRepository
import dev.xhyrom.jim.databinding.FragmentHomeBinding
import dev.xhyrom.jim.ui.adapters.SatelliteAdapter

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private lateinit var homeViewModel: HomeViewModel
    private lateinit var satelliteAdapter: SatelliteAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val repository = SatelliteRepository(
            AppDatabase.getDatabase(requireContext()).satelliteDao()
        )
        
        homeViewModel = ViewModelProvider(
            this,
            HomeViewModel.Factory(repository)
        )[HomeViewModel::class.java]

        setupRecyclerView()
        setupObservers()
        setupClickListeners()
    }

    private fun setupRecyclerView() {
        satelliteAdapter = SatelliteAdapter { satellite ->
            val action = HomeFragmentDirections.actionHomeFragmentToSatelliteDetailFragment(satellite.id)
            findNavController().navigate(action)
        }
        binding.recyclerSatellites.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = satelliteAdapter
        }
    }

    private fun setupObservers() {
        homeViewModel.allSatellites.observe(viewLifecycleOwner) { satellites ->
            satelliteAdapter.submitList(satellites)
            binding.textEmpty.visibility = if (satellites.isEmpty()) View.VISIBLE else View.GONE
        }
    }

    private fun setupClickListeners() {
        binding.fabAddSatellite.setOnClickListener {
            val action = HomeFragmentDirections.actionHomeFragmentToAddSatelliteFragment()
            findNavController().navigate(action)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
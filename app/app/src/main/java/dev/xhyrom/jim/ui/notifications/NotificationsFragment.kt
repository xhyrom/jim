package dev.xhyrom.jim.ui.notifications

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import dev.xhyrom.jim.databinding.FragmentLogsBinding

class NotificationsFragment : Fragment() {

    private var _binding: FragmentLogsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val notificationsViewModel =
            ViewModelProvider(this).get(NotificationsViewModel::class.java)

        _binding = FragmentLogsBinding.inflate(inflater, container, false)
        val root: View = binding.root

        val textView: TextView = binding.textLogs
        notificationsViewModel.text.observe(viewLifecycleOwner) {
            textView.text = it
        }

        // TODO
        binding.logContent.text = """
            [2023-09-15 08:15:23] INFO: Device started
            [2023-09-15 08:15:25] INFO: Connected to Core API
            [2023-09-15 08:16:10] INFO: Wake word detected
            [2023-09-15 08:16:12] INFO: Transcription: "what's the weather today"
            [2023-09-15 08:16:14] INFO: Response received from Core
            [2023-09-15 08:16:15] INFO: TTS synthesis complete
            [2023-09-15 08:22:43] INFO: Wake word detected
            [2023-09-15 08:22:45] INFO: Transcription: "set an alarm for 7 AM"
            [2023-09-15 08:22:47] INFO: Response received from Core
            [2023-09-15 08:22:48] INFO: TTS synthesis complete
        """.trimIndent()

        return root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
package dev.xhyrom.jim.ui.terminal

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import dev.xhyrom.jim.R
import dev.xhyrom.jim.databinding.ItemFileBinding
import dev.xhyrom.jim.ssh.FileInfo

class FileListAdapter(
    private val onItemClick: (FileInfo) -> Unit
) : ListAdapter<FileInfo, FileListAdapter.FileViewHolder>(FileDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FileViewHolder {
        val binding = ItemFileBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return FileViewHolder(binding)
    }

    override fun onBindViewHolder(holder: FileViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class FileViewHolder(private val binding: ItemFileBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(fileInfo: FileInfo) {
            binding.textFileName.text = fileInfo.name
            binding.textFileDetails.text = if (fileInfo.isDirectory) {
                "Directory"
            } else {
                "${fileInfo.getFormattedSize()} - ${fileInfo.getFormattedPermissions()}"
            }

            binding.iconFile.setImageResource(
                if (fileInfo.isDirectory) R.drawable.ic_folder else R.drawable.ic_file
            )

            binding.root.setOnClickListener {
                onItemClick(fileInfo)
            }
        }
    }

    class FileDiffCallback : DiffUtil.ItemCallback<FileInfo>() {
        override fun areItemsTheSame(oldItem: FileInfo, newItem: FileInfo): Boolean {
            return oldItem.path == newItem.path
        }

        override fun areContentsTheSame(oldItem: FileInfo, newItem: FileInfo): Boolean {
            return oldItem == newItem
        }
    }
}
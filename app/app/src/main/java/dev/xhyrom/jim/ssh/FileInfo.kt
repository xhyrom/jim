package dev.xhyrom.jim.ssh

data class FileInfo(
    val name: String,
    val path: String,
    val size: Long,
    val permissions: String,
    val isDirectory: Boolean
) {
    fun getFormattedSize(): String {
        return when {
            size < 1024 -> "$size B"
            size < 1024 * 1024 -> "${size / 1024} KB"
            size < 1024 * 1024 * 1024 -> "${size / (1024 * 1024)} MB"
            else -> "${size / (1024 * 1024 * 1024)} GB"
        }
    }

    fun getFormattedPermissions(): String {
        return permissions
    }
}
package dev.xhyrom.jim.data.models

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "satellites")
data class Satellite(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    val ipAddress: String,
    val sshUsername: String = "pi",
    val sshPassword: String? = null,
    val sshPort: Int = 22,
    val description: String? = null,
    val lastConnected: Long? = null,
    val status: String = "UNKNOWN" // ONLINE, OFFLINE, UNKNOWN
)
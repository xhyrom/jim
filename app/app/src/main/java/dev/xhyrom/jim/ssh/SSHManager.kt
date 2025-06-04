package dev.xhyrom.jim.ssh

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.util.Properties
import com.jcraft.jsch.ChannelExec
import com.jcraft.jsch.JSch
import com.jcraft.jsch.Session

class SSHManager {
    private var session: Session? = null

    suspend fun connect(
        hostname: String,
        username: String,
        password: String,
        port: Int = 22
    ): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val jsch = JSch()
            session = jsch.getSession(username, hostname, port)
            session?.setPassword(password)

            val properties = Properties()
            properties.put("StrictHostKeyChecking", "no")
            session?.setConfig(properties)

            session?.connect(30000)
            Result.success(true)
        } catch (e: Exception) {
            Log.e("SSHManager", "Connection error", e)
            Result.failure(e)
        }
    }

    suspend fun executeCommand(command: String): Result<String> = withContext(Dispatchers.IO) {
        try {
            if (session == null || !session!!.isConnected) {
                return@withContext Result.failure(Exception("Not connected"))
            }

            val outputStream = ByteArrayOutputStream()
            val channel = session!!.openChannel("exec") as ChannelExec

            channel.setCommand(command)
            channel.outputStream = outputStream
            channel.connect()

            while (channel.isConnected) {
                Thread.sleep(100)
            }

            channel.disconnect()
            Result.success(outputStream.toString())
        } catch (e: Exception) {
            Log.e("SSHManager", "Command execution error", e)
            Result.failure(e)
        }
    }

    fun disconnect() {
        session?.disconnect()
        session = null
    }
}
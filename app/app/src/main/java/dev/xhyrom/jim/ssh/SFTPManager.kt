package dev.xhyrom.jim.ssh

import android.util.Log
import com.jcraft.jsch.ChannelSftp
import com.jcraft.jsch.JSch
import com.jcraft.jsch.Session
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.Properties
import java.util.Vector

class SFTPManager {
    private var session: Session? = null
    private var channelSftp: ChannelSftp? = null

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

            channelSftp = session?.openChannel("sftp") as ChannelSftp
            channelSftp?.connect()

            Result.success(true)
        } catch (e: Exception) {
            Log.e("SFTPManager", "Connection error", e)
            Result.failure(e)
        }
    }

    suspend fun listFiles(path: String): Result<List<FileInfo>> = withContext(Dispatchers.IO) {
        try {
            if (channelSftp == null || !channelSftp!!.isConnected) {
                return@withContext Result.failure(Exception("Not connected"))
            }

            val fileList = mutableListOf<FileInfo>()
            val entries = channelSftp!!.ls(path) as Vector<ChannelSftp.LsEntry>

            for (entry in entries) {
                if (entry.filename == "." || entry.filename == "..") continue

                val fileInfo = FileInfo(
                    name = entry.filename,
                    path = "$path/${entry.filename}",
                    size = entry.attrs.size,
                    permissions = entry.attrs.permissionsString,
                    isDirectory = entry.attrs.isDir
                )
                fileList.add(fileInfo)
            }

            Result.success(fileList)
        } catch (e: Exception) {
            Log.e("SFTPManager", "List files error", e)
            Result.failure(e)
        }
    }

    suspend fun downloadFile(remotePath: String, localPath: String): Result<Boolean> =
        withContext(Dispatchers.IO) {
            try {
                if (channelSftp == null || !channelSftp!!.isConnected) {
                    return@withContext Result.failure(Exception("Not connected"))
                }

                channelSftp!!.get(remotePath, localPath)
                Result.success(true)
            } catch (e: Exception) {
                Log.e("SFTPManager", "Download error", e)
                Result.failure(e)
            }
        }

    suspend fun uploadFile(localPath: String, remotePath: String): Result<Boolean> =
        withContext(Dispatchers.IO) {
            try {
                if (channelSftp == null || !channelSftp!!.isConnected) {
                    return@withContext Result.failure(Exception("Not connected"))
                }

                channelSftp!!.put(localPath, remotePath)
                Result.success(true)
            } catch (e: Exception) {
                Log.e("SFTPManager", "Upload error", e)
                Result.failure(e)
            }
        }

    suspend fun mkdir(path: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            if (channelSftp == null || !channelSftp!!.isConnected) {
                return@withContext Result.failure(Exception("Not connected"))
            }

            channelSftp!!.mkdir(path)
            Result.success(true)
        } catch (e: Exception) {
            Log.e("SFTPManager", "Mkdir error", e)
            Result.failure(e)
        }
    }

    suspend fun removeFile(path: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            if (channelSftp == null || !channelSftp!!.isConnected) {
                return@withContext Result.failure(Exception("Not connected"))
            }

            channelSftp!!.rm(path)
            Result.success(true)
        } catch (e: Exception) {
            Log.e("SFTPManager", "Remove file error", e)
            Result.failure(e)
        }
    }

    suspend fun removeDirectory(path: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            if (channelSftp == null || !channelSftp!!.isConnected) {
                return@withContext Result.failure(Exception("Not connected"))
            }

            channelSftp!!.rmdir(path)
            Result.success(true)
        } catch (e: Exception) {
            Log.e("SFTPManager", "Remove directory error", e)
            Result.failure(e)
        }
    }

    fun disconnect() {
        channelSftp?.disconnect()
        session?.disconnect()
        channelSftp = null
        session = null
    }
}
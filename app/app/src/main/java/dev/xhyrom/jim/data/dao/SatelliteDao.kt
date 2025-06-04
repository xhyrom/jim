package dev.xhyrom.jim.data.dao

import androidx.lifecycle.LiveData
import androidx.room.*
import dev.xhyrom.jim.data.models.Satellite

@Dao
interface SatelliteDao {
    @Query("SELECT * FROM satellites ORDER BY name ASC")
    fun getAllSatellites(): LiveData<List<Satellite>>

    @Query("SELECT * FROM satellites WHERE id = :id")
    fun getSatelliteById(id: Long): LiveData<Satellite>
    
    @Query("SELECT * FROM satellites WHERE status = :status ORDER BY name ASC")
    fun getSatellitesByStatus(status: String): LiveData<List<Satellite>>

    @Insert
    suspend fun insert(satellite: Satellite): Long

    @Update
    suspend fun update(satellite: Satellite)

    @Delete
    suspend fun delete(satellite: Satellite)
}
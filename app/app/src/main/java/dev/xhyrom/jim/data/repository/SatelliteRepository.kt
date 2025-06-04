package dev.xhyrom.jim.data.repository

import androidx.lifecycle.LiveData
import dev.xhyrom.jim.data.dao.SatelliteDao
import dev.xhyrom.jim.data.models.Satellite

class SatelliteRepository(private val satelliteDao: SatelliteDao) {
    val allSatellites: LiveData<List<Satellite>> = satelliteDao.getAllSatellites()
    
    suspend fun insert(satellite: Satellite): Long {
        return satelliteDao.insert(satellite)
    }

    suspend fun update(satellite: Satellite) {
        satelliteDao.update(satellite)
    }

    suspend fun delete(satellite: Satellite) {
        satelliteDao.delete(satellite)
    }

    fun getSatellitesByStatus(status: String): LiveData<List<Satellite>> {
        return satelliteDao.getSatellitesByStatus(status)
    }

    fun getSatelliteById(id: Long): LiveData<Satellite> {
        return satelliteDao.getSatelliteById(id)
    }
}
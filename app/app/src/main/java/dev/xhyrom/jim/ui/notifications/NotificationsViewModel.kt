package dev.xhyrom.jim.ui.notifications

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class NotificationsViewModel : ViewModel() {

    private val _text = MutableLiveData<String>().apply {
        value = "This is the logs section where you can view the assistant's activity logs"
    }
    val text: LiveData<String> = _text
}
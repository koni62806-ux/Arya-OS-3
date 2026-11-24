package com.arya.keyboard

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 36, 28, 28)
            setBackgroundColor(0xFF101522.toInt())
        }
        val title = TextView(this).apply {
            text = "Arya Keyboard"
            textSize = 28f
            setTextColor(0xFF8DB7FF.toInt())
        }
        val info = TextView(this).apply {
            text = "کیبورد فارسی و انگلیسی\n\n۱) ابتدا کیبورد Arya را فعال کن.\n۲) سپس آن را به‌عنوان صفحه‌کلید پیش‌فرض انتخاب کن."
            textSize = 17f
            setTextColor(0xFFFFFFFF.toInt())
            setPadding(0, 24, 0, 24)
        }
        val enable = Button(this).apply {
            text = "فعال‌سازی Arya Keyboard"
            setOnClickListener { startActivity(Intent(Settings.ACTION_INPUT_METHOD_SETTINGS)) }
        }
        val choose = Button(this).apply {
            text = "انتخاب کیبورد"
            setOnClickListener {
                val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
                imm.showInputMethodPicker()
            }
        }
        root.addView(title)
        root.addView(info)
        root.addView(enable)
        root.addView(choose)
        setContentView(root)
    }
}

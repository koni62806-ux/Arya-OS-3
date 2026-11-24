package com.arya.keyboard

import android.inputmethodservice.InputMethodService
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.Button
import android.widget.LinearLayout

class AryaInputMethodService : InputMethodService() {
    private var english = false
    private lateinit var keyboard: LinearLayout

    private val faRows = listOf(
        listOf("ض","ص","ث","ق","ف","غ","ع","ه","خ","ح","ج"),
        listOf("ش","س","ی","ب","ل","ا","ت","ن","م","ک","گ"),
        listOf("ظ","ط","ز","ر","ذ","د","پ","و","چ")
    )
    private val enRows = listOf(
        listOf("q","w","e","r","t","y","u","i","o","p"),
        listOf("a","s","d","f","g","h","j","k","l"),
        listOf("z","x","c","v","b","n","m")
    )

    override fun onCreateInputView(): View {
        keyboard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(5, 8, 5, 8)
            setBackgroundColor(Color.rgb(16, 21, 34))
        }
        renderKeyboard()
        return keyboard
    }

    override fun onStartInputView(info: EditorInfo?, restarting: Boolean) {
        super.onStartInputView(info, restarting)
        if (::keyboard.isInitialized) renderKeyboard()
    }

    private fun renderKeyboard() {
        keyboard.removeAllViews()
        val rows = if (english) enRows else faRows
        rows.forEach { row ->
            val line = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER
            }
            row.forEach { key ->
                line.addView(makeKey(key), LinearLayout.LayoutParams(0, dp(48), 1f).apply {
                    setMargins(dp(2), dp(3), dp(2), dp(3))
                })
            }
            keyboard.addView(line, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        }
        val controls = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER }
        addControl(controls, if (english) "فارسی" else "EN", 1f) {
            english = !english
            renderKeyboard()
        }
        addControl(controls, "?123", 1f) { commitText("123") }
        addControl(controls, "،", .7f) { commitText("،") }
        addControl(controls, "فاصله", 2.4f) { commitText(" ") }
        addControl(controls, "⌫", 1f) { deleteOne() }
        addControl(controls, "↵", 1f) { sendEnter() }
        keyboard.addView(controls)
    }

    private fun makeKey(label: String): Button = Button(this).apply {
        text = label
        textSize = if (label.length > 1) 14f else 20f
        setTextColor(Color.WHITE)
        typeface = Typeface.DEFAULT_BOLD
        isAllCaps = false
        background = keyBackground(0xFF26334B.toInt())
        setPadding(0, 0, 0, 0)
        setOnClickListener { commitText(label) }
    }

    private fun addControl(parent: LinearLayout, label: String, weight: Float, action: () -> Unit) {
        val button = Button(this).apply {
            text = label
            textSize = 13f
            setTextColor(Color.WHITE)
            isAllCaps = false
            background = keyBackground(0xFF36558A.toInt())
            setPadding(dp(2), 0, dp(2), 0)
            setOnClickListener { action() }
        }
        parent.addView(button, LinearLayout.LayoutParams(0, dp(48), weight).apply {
            setMargins(dp(2), dp(3), dp(2), dp(3))
        })
    }

    private fun keyBackground(color: Int) = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(8).toFloat()
        setStroke(dp(1), 0xFF49658F.toInt())
    }

    private fun commitText(value: String) { currentInputConnection?.commitText(value, 1) }
    private fun deleteOne() { currentInputConnection?.deleteSurroundingText(1, 0) }

    private fun sendEnter() {
        val connection = currentInputConnection ?: return
        val action = currentInputEditorInfo?.imeOptions?.and(EditorInfo.IME_MASK_ACTION)
        if (action != null && action != EditorInfo.IME_ACTION_NONE && action != EditorInfo.IME_ACTION_UNSPECIFIED) {
            connection.performEditorAction(action)
        } else {
            connection.commitText("\n", 1)
        }
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}

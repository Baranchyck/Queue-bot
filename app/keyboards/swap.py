from aiogram.utils.keyboard import InlineKeyboardBuilder


def swap_kb(from_user: int, from_pos: int, to_user: int, to_pos: int):
    payload = f"{from_user}:{from_pos}:{to_user}:{to_pos}"
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Прийняти", callback_data=f"swap_ok:{payload}")
    kb.button(text="❌ Відхилити", callback_data=f"swap_no:{payload}")
    kb.adjust(2)  # обидві кнопки в одному ряду
    return kb.as_markup()
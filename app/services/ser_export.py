from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

def build_xlsx(slots) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Черга"

    ws.append(["№", "Ім'я", "Telegram ID"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for s in slots:
        ws.append([s.position, s.user_name or "", s.user_id or ""])

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 16

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
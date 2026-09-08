import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

def calculate_expiration_date(product_name: str) -> str:
    """
    Calculate the expiration date for a given product and add the production day.
    
    Args:
        product_name (str): Name of the product ('LHP', 'LEBEN', or 'LAF')
    
    Returns:
        str: A string containing the expiration date or error message
    """
    expiration_periods = {
        "LHP": 5,
        "LEBEN": 20,
        "LAF": 30
    }
    
    if product_name not in expiration_periods:
        return "Unknown product name"
    
    production_date = datetime.now()
    expiration_date = production_date + timedelta(days=expiration_periods[product_name])
    
    # الأيام بالفرنسية
    days_in_french = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    # اختصار الشهر باللغة اللاتينية
    months_in_latin = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]
    
    # اليوم بالفرنسية
    production_day_of_week = days_in_french[production_date.weekday()]
    
    # الشهر باللاتينية
    expiration_month_in_latin = months_in_latin[expiration_date.month - 1]
    
    # تنسيق النتيجة: يوم نهاية الصلاحية مع اليوم المختصر للإنتاج
    return f"{expiration_date.day} {expiration_month_in_latin} {production_day_of_week[:2].upper()}"

# دالة لعرض النتيجة في واجهة المستخدم
def on_calculate_button_click():
    product_name = product_combobox.get().upper()
    result = calculate_expiration_date(product_name)
    if "Unknown" in result:
        messagebox.showerror("Error", result)
    else:
        result_label.config(text=f"Expiration Date: {result}")

# إعداد واجهة المستخدم باستخدام Tkinter
root = tk.Tk()
root.title("Product Expiration Calculator")

# إعداد واجهة الإدخال
product_label = tk.Label(root, text="Select product (LHP, LEBEN, LAF):")
product_label.pack(pady=10)

# إعداد Spinner (Combobox) لاختيار المنتج
product_combobox = ttk.Combobox(root, values=["LHP", "LEBEN", "LAF"])
product_combobox.pack(pady=5)
product_combobox.set("LHP")  # تعيين القيمة الافتراضية

calculate_button = tk.Button(root, text="Calculate Expiration Date", command=on_calculate_button_click)
calculate_button.pack(pady=10)

# إعداد مكون لعرض النتيجة
result_label = tk.Label(root, text="Expiration Date: ")
result_label.pack(pady=10)

# تشغيل واجهة المستخدم
root.mainloop()
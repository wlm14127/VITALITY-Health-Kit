from datetime import datetime

from fpdf import FPDF
import time

class PDF(FPDF):
    def header(self):
        self.set_y(12.5)
        self.set_font("roboto", "", 10)
        self.cell(0, 0, "Tech Titans | Health Report ({})".format(patientInfo.get("name")[2]), border=0, align="L")
        self.cell(0, 0, "{}".format(time.strftime("%d/%m/%Y")), border=0, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-12.5)
        self.set_font("roboto", "", 7)
        self.cell(0, 0, " Contains public sector information licensed under the Open Government Licence v3.0.", border=0, align="L")
        self.set_font("roboto", "", 10)
        self.cell(0, 0, f"{self.page_no()} of {{nb}}", border=0, align="R")

def initialise_fonts():
    pdf.add_font("roboto", style="", fname="Roboto-Regular.ttf")
    pdf.add_font("roboto", style="b", fname="Roboto-Bold.ttf")
    pdf.add_font("roboto", style="i", fname="Roboto-Italic.ttf")
    pdf.add_font("roboto", style="bi", fname="Roboto-BoldItalic.ttf")

    pdf.add_font("roboto-light", style="", fname="Roboto-Light.ttf")
    pdf.add_font("roboto-light", style="b", fname="Roboto-Medium.ttf")
    pdf.add_font("roboto-light", style="i", fname="Roboto-LightItalic.ttf")
    pdf.add_font("roboto-light", style="bi", fname="Roboto-MediumItalic.ttf")

messageBank = {
    "fileTitle": "Monthly Statistics",
    "fileSubTitle": "This report was **automatically generated**. If you have any concerns regarding this data, please seek help from your GP.",
    "main": {
        "normal": "Your statistics this month are **normal**. Breakdown available below.",
        "abnormal": "Some of your statistics this month are **abnormal**. Breakdown available below."
    },
    "heartrate": {
        "normal": "**No issues detected**. Categories accounted for: late-night/early-morning, morning, daytime, and evening.",
        "abnormal": "**{} incident(s) recorded**. Categories accounted for: late-night/early-morning, morning, daytime, and evening."
    },
    "temperature": {
        "normal": "**No issues detected.**",
        "abnormal": "**{} incident(s) recorded.**"
    }
}

patientInfo = {
    "name": ["Test", "User", "Test User"],
    "dob": "01/01/2003",
    "age": "21",
    "gender": "Male",
    "analysis": "abnormal",
    "heartrate": {
        "analysis": ["normal", "exerciseAdults"],
        "20:00 - 06:00": [92, "healthy"],
        "06:00 - 10:00": [82, "healthy"],
        "10:00 - 16:00": [70, "healthy"],
        "16:00 - 20:00": [67, "healthy"],
        "conclusion": "Exercise regularly. Your mental health also affects your heartrate - it may increase if you become more stressed. Consult your GP if you have any concerns."
    },
    "temperature": {
        "analysis": ["abnormal", "fever", "caution"],
        "incidents": {
            "02/03/2024": 38.3,
            "03/03/2024": 38.3
        }
    }
}

pdf = PDF()
pdf = PDF(orientation="portrait", format="A4")
initialise_fonts()
pdf.add_page()
pdf.set_font("roboto-light", style="b", size=14)
pdf.cell(0, 0, "{}".format(messageBank.get("fileTitle")), markdown=True)
pdf.ln()
pdf.set_font("roboto", style="", size=10)
pdf.cell(0, 5, "{}".format(messageBank.get("fileSubTitle")), markdown=True)
pdf.ln()
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.set_font("roboto", style="", size=10)
pdf.cell(0, 5)
pdf.ln()
pdf.cell(0, 5, "**Patient Name**:  {} (**{}**)".format(patientInfo.get("name")[2], patientInfo.get("gender")), markdown=True)
pdf.ln()
pdf.cell(0, 5, "**Date of Birth**:    {} (**{}**)".format(patientInfo.get("dob"), patientInfo.get("age")), markdown=True)
pdf.ln()
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.ln()
pdf.cell(0, 5, "Some of your statistics this month are **abnormal**. Breakdown available below.", markdown=True)
pdf.ln()
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.set_font("roboto-light", style="b", size=14)
pdf.cell(0, 17, "Heart Rate", markdown=True)
pdf.ln()
pdf.set_font("roboto", style="", size=10)
pdf.cell(0, -2.5, "**No issues detected**. Categories accounted for: morning, daytime, evening, and late-night.", markdown=True)
pdf.ln(3)
pdf.multi_cell(0, 5, "   \u2022   {:>15}: average of 90 bpm (**healthy**)\n   \u2022   {:>15}: average of 82 bpm (**healthy**)\n   \u2022   {:>15}: average of 70 bpm (**healthy**)\n   \u2022   {:>15}: average of 67 bpm (**healthy**)".format("20:00 - 06:00", "06:00 - 10:00", "10:00 - 16:00", "16:00 - 20:00"), markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "Your heart rate is expected to differ throughout the day - this is normal. **Do not** take measurements directly after exercising. **Avoid sitting down for long periods.**", markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "You should always ensure you take regular exercise - for your age group (**19 - 64**), this should include:", markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "   \u2022     at least **150 minutes** of moderate intensity activity a week or **75 minutes** of vigorous intensity activity a week.\n   \u2022     spread exercise evenly over **4** to **5** days a week, or **every day**.", markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "Ask your GP if you experience difficulties exercising.")
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.ln(5)
pdf.multi_cell(0, 5, "**Conclusion**: Exercise regularly. Your mental health also affects your heartrate - it may increase if you become more stressed. Consult your GP if you have any concerns.", markdown=True)
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.ln(0.0000001)
pdf.set_font("roboto-light", style="b", size=14)
pdf.cell(0, 17, "Temperature", markdown=True)
pdf.ln()
pdf.set_font("roboto", style="", size=10)
pdf.cell(0, -2.5, "**4 incident(s) recorded**.", markdown=True)
pdf.ln(3)
pdf.multi_cell(0, 5, "   \u2022     {}: unusually high body temperature (**38.3°C**)\n   \u2022     {}: unusually high body temperature (**38.3°C**)\n   \u2022     {}: unusually high body temperature (**38.3°C**)\n   \u2022     {}: unusually high body temperature (**38.3°C**)".format("02/03/2024", "03/03/2024", "05/03/2024", "12/03/2024"), markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "Normal body temperature is **around 37°C**. Body temperatures **above 38°C** may indicate **fever**. If your body temeprature is **persistently over 38°C**, you should:", markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "   \u2022     get lots of **rest**.\n   \u2022     **drink** plenty of fluids (water is best) to avoid dehydration – drink enough so your pee is --light yellow and clear--.\n   \u2022     take **paracetamol** or **ibuprofen** if you feel uncomfortable.", markdown=True)
pdf.ln(2)
pdf.multi_cell(0, 5, "**Avoid contact with other people until your temperature goes down.** Ask for an **urgent** GP appointment, or call **NHS 111**, if your high temperature persists for more than **4** consecutive days.", markdown=True)
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.ln(5)
pdf.multi_cell(0, 5, "**Conclusion**: You've had an unusually **high** number of temperature incidents this month. Consult your GP if this is a recurring pattern.", markdown=True)
pdf.line(10, pdf.get_y()+2.5, 200, pdf.get_y()+2.5)
pdf.ln()

pdf.output("report.pdf")
import csv
import tkinter as tk
from tkinter import messagebox, ttk
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import threading
from reportlab.lib.pagesizes import letter, landscape

import math

class Student:
    def __init__(self, roll_number, department):
        self.roll_number = roll_number
        self.department = department

def read_student_data(csv_file):
    students = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            student = Student(row['Roll Number'], row['Department'])
            students.append(student)
    return students
def gen_seat_and_room_chart(classroom_data, students):
    doc = SimpleDocTemplate("room_allocation_chart.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    
    data_room_allocation = [["Room Number", "Rows", "Cols", "Allocated Students"]]
    for room_data in classroom_data:
        room_number = room_data['room_number']
        rows = room_data['rows']
        cols = room_data['cols']
        
        room_students = students[:rows * cols]
        room_data['students'] = room_students

        # Remove assigned students from the list
        students = students[rows * cols:]  
        
        allocated_students = ", ".join([student.roll_number for student in room_data.get('students', [])])
        
        # If 'students' key is empty or not present, display "None"
        allocated_students = allocated_students if allocated_students else "None"
        
        data_room_allocation.append([room_number, rows, cols, allocated_students])
    
    table_room_allocation = Table(data_room_allocation, colWidths=[doc.width/len(data_room_allocation[0])]*len(data_room_allocation[0]), rowHeights=30)
    table_room_allocation.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements_room_allocation = [Paragraph("<para align=center><b>Room Allocation Chart</b></para>", styles['Title']), Spacer(1, 12), table_room_allocation]
    
    doc_seating_plan = SimpleDocTemplate("seating_plan.pdf", pagesize=landscape(letter))
    tables_seating_plan = []
    
    for i, room_data in enumerate(classroom_data):
        room_number = room_data['room_number']
        rows = room_data['rows']
        cols = room_data['cols']
        
        num_pages = math.ceil(len(room_data['students']) / (rows * cols))
        
        for j in range(num_pages):
            title = Paragraph(f"<para align=center><b>Seating Chart for Room {room_number}</b></para>", styles['Title'])
            tables_seating_plan.append(title)
            tables_seating_plan.append(Spacer(1, 12))
            
            class_table_data = []
            for k in range(rows):
                row_data = []
                for l in range(cols):
                    idx = j * (rows * cols) + k * cols + l
                    if idx < len(room_data['students']):
                        student = room_data['students'][idx]
                        row_data.append(student.roll_number)
                    else:
                        row_data.append("")
                
                class_table_data.append(row_data)
            
            colWidths = [doc_seating_plan.width / cols] * cols
            class_table = Table(class_table_data, colWidths=colWidths, rowHeights=70)
            class_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            tables_seating_plan.append(class_table)
            if j < num_pages - 1:
                tables_seating_plan.append(PageBreak())
    
    doc_seating_plan.build(tables_seating_plan)
    
    elements_room_allocation.append(Spacer(1, 12))
    doc.build(elements_room_allocation)
    
    messagebox.showinfo("Success", "PDFs generated successfully.")

def main():
    root = tk.Tk()
    root.title("Seating Chart and Room Allocation PDF Generator")
    root.geometry("400x200") 
    
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12))
    
    csv_file = 'student_data.csv'  
    students = read_student_data(csv_file)
    
    classroom_data = []
    with open('classroom_layout.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
          room_number, rows, cols = row
          classroom_data.append({'room_number': room_number, 'rows': int(rows), 'cols': int(cols), 'students': []})

    gen_seat_and_room_chart(classroom_data, students)
    
    messagebox.showinfo("Success", "PDFs generated successfully.")
    root.mainloop()

if __name__ == "__main__":
    main()
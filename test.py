import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np

class LetterMatrixGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Letter Matrix GUI")
        self.master.geometry("800x700")

        # Create a main frame
        main_frame = tk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create a canvas
        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add vertical scrollbar to the canvas
        y_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add horizontal scrollbar to the canvas
        x_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.canvas.bind('<Configure>', self.configure_canvas)

        # Create another frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas)

        # Add that frame to a window in the canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.input_string = ""
        self.current_rows = 1
        self.current_cols = 0

        # Input frame
        input_frame = tk.Frame(self.inner_frame)
        input_frame.pack(pady=10)

        self.input_entry = tk.Entry(input_frame, width=30)
        self.input_entry.grid(row=0, column=0, padx=5)

        submit_button = tk.Button(input_frame, text="Submit", command=self.submit_string)
        submit_button.grid(row=0, column=1, padx=5)

        # Display frame
        self.display_frame = tk.Frame(self.inner_frame)
        self.display_frame.pack(pady=10)

        # Control frame
        control_frame = tk.Frame(self.inner_frame)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Rows:").grid(row=0, column=0, padx=5)
        self.rows_entry = tk.Entry(control_frame, width=5)
        self.rows_entry.grid(row=0, column=1, padx=5)

        tk.Label(control_frame, text="Columns:").grid(row=0, column=2, padx=5)
        self.cols_entry = tk.Entry(control_frame, width=5)
        self.cols_entry.grid(row=0, column=3, padx=5)

        update_button = tk.Button(control_frame, text="Update Matrix", command=self.update_matrix)
        update_button.grid(row=0, column=4, padx=5)

        # Output frame
        output_frame = tk.Frame(self.inner_frame)
        output_frame.pack(pady=10)

        tk.Label(output_frame, text="Original Matrix Output:").pack()
        self.output_text = tk.Text(output_frame, height=3, width=50)
        self.output_text.pack()

        # Column order frame
        order_frame = tk.Frame(self.inner_frame)
        order_frame.pack(pady=10)

        tk.Label(order_frame, text="Column Order:").grid(row=0, column=0, padx=5)
        self.order_entry = tk.Entry(order_frame, width=30)
        self.order_entry.grid(row=0, column=1, padx=5)
        self.order_entry.insert(0, "0,3,6,2,5,1,4")  # Default order

        rearrange_button = tk.Button(order_frame, text="Rearrange Columns", command=self.rearrange_columns)
        rearrange_button.grid(row=0, column=2, padx=5)

        # Rearranged display frame
        self.rearranged_frame = tk.Frame(self.inner_frame)
        self.rearranged_frame.pack(pady=10)

        # Rearranged output frame
        rearranged_output_frame = tk.Frame(self.inner_frame)
        rearranged_output_frame.pack(pady=10)

        tk.Label(rearranged_output_frame, text="Rearranged Matrix Output:").pack()
        self.rearranged_output_text = tk.Text(rearranged_output_frame, height=3, width=50)
        self.rearranged_output_text.pack()

    def configure_canvas(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Update the width of the canvas window to fit the inner frame
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def submit_string(self):
        input_text = self.input_entry.get().upper()
        if not input_text.isalpha():
            messagebox.showerror("Error", "Please enter only uppercase letters.")
            return
        self.input_string = input_text
        self.current_rows = 1
        self.current_cols = len(input_text)
        self.update_display()

    def update_matrix(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive integers.")
            self.current_rows = rows
            self.current_cols = cols
            self.update_display()
            self.output_column_wise()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_display(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        max_width = max(len(self.input_string) // self.current_rows, self.current_cols)
        
        for i, char in enumerate(self.input_string):
            row = i // self.current_cols
            col = i % self.current_cols
            tk.Label(self.display_frame, text=char, width=2, height=1, relief="solid", borderwidth=1).grid(
                row=row, column=col, padx=(5, 0), pady=(5, 0), sticky='nsew'
            )
        
        # Configure grid to expand cells
        for i in range(self.current_rows):
            self.display_frame.grid_rowconfigure(i, weight=1)
        for i in range(max_width):
            self.display_frame.grid_columnconfigure(i, weight=1)

    def output_column_wise(self):
        rows = max(self.current_rows, (len(self.input_string) + self.current_cols - 1) // self.current_cols)
        cols = max(self.current_cols, len(self.input_string))
        matrix = np.full((rows, cols), ' ', dtype=str)

        for i, char in enumerate(self.input_string):
            row = i // self.current_cols
            col = i % self.current_cols
            if row < rows and col < cols:
                matrix[row, col] = char

        output = ''
        for col in range(cols - 1, -1, -1):
            for row in range(rows):
                if matrix[row, col] != ' ':
                    output += matrix[row, col]

        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, output)

    def rearrange_columns(self):
        try:
            order = [int(x) for x in self.order_entry.get().split(',')]
            if len(order) != self.current_cols or not all(0 <= x < self.current_cols for x in order):
                raise ValueError("Invalid column order")
        except ValueError:
            messagebox.showerror("Error", "Invalid column order. Please enter comma-separated indices.")
            return

        rows = max(self.current_rows, (len(self.input_string) + self.current_cols - 1) // self.current_cols)
        cols = max(self.current_cols, len(self.input_string))
        matrix = np.full((rows, cols), ' ', dtype=str)

        for i, char in enumerate(self.input_string):
            row = i // self.current_cols
            col = i % self.current_cols
            if row < rows and col < cols:
                matrix[row, col] = char

        rearranged_matrix = matrix[:, order]

        # Display rearranged matrix
        for widget in self.rearranged_frame.winfo_children():
            widget.destroy()

        rows, cols = rearranged_matrix.shape
        for row in range(rows):
            for col in range(cols):
                tk.Label(self.rearranged_frame, text=rearranged_matrix[row, col], width=2, height=1, relief="solid", borderwidth=1).grid(
                    row=row, column=col, padx=(5, 0), pady=(5, 0), sticky='nsew'
                )
        # Output rearranged matrix
        output = ''
        for col in range(cols - 1, -1, -1):
            for row in range(rows):
                if rearranged_matrix[row, col] != ' ':
                    output += rearranged_matrix[row, col]

        self.rearranged_output_text.delete('1.0', tk.END)
        self.rearranged_output_text.insert(tk.END, output)

root = tk.Tk()
app = LetterMatrixGUI(root)
root.mainloop()

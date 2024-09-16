import os
import tkinter as tk
from tkinter import messagebox
from script import *

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Order Batcher - {}".format(APP_VERSION))
        self.root.geometry("450x350")

        self.frame1 = tk.Frame(self.root)
        self.frame1.pack()

        self.labelFrame1 = tk.LabelFrame(self.frame1, text="Batch Filename")
        self.labelFrame1.pack(padx=20, pady=20)

        self.inputField = tk.Entry(self.labelFrame1, font=("Arial", 10), width=50)
        self.inputField.bind("<KeyPress>", self.onEnter)
        self.inputField.pack(padx=10, pady=(5,10))

        self.submitButton = tk.Button(self.frame1, text="Batch", font=("Arial", 9), command=self.submitBatch, width=20)
        self.submitButton.pack(padx=10, pady=0)

        self.statusMessage = tk.Label(self.frame1, text='', font=("Arial", 9))
        self.statusMessage.pack(padx=10, pady=10)

        self.labelFrame2 = tk.LabelFrame(self.frame1, text="Out of Stock SKU(s)")
        self.labelFrame2.pack(padx=20, pady=20)

        self.outOfStockSKUsBox = tk.Text(self.labelFrame2, font=("Arial", 9), width=50)
        self.outOfStockSKUsBox.pack(padx=10, pady=(5,10))
        self.outOfStockSKUsBox.config(state=tk.DISABLED)
        
        self.root.mainloop()

    def onEnter(self, event):
        if event.keysym == "Return":
            self.submitBatch()

    def clearMessages(self):
        self.outOfStockSKUsBox.config(state=tk.NORMAL)
        self.outOfStockSKUsBox.delete('1.0', tk.END)
        self.outOfStockSKUsBox.config(state=tk.DISABLED)
        self.statusMessage.config(text="")

    def submitBatch(self):
        self.clearMessages()

        inputFilename = self.inputField.get()

        if len(inputFilename) != 0:
            response = batchOrders(inputFilename)

            if response["success"]:
                self.statusMessage.config(text="Your output filename is: " + response["outputFilename"])
                os.system("start EXCEL.EXE " + response["outputFilename"])

            if response["success"] is not None and not response["success"]:
                self.showStatusMessage("Error", response["errorMessage"])

            if response["warning"] is not None and not response["warning"]:
                if response["outOfStockSKUs"]:
                    outOfStockSKUsList = "\n".join(response["outOfStockSKUs"])
                    self.outOfStockSKUsBox.config(state=tk.NORMAL)
                    self.outOfStockSKUsBox.insert(tk.END, outOfStockSKUsList)
                    self.outOfStockSKUsBox.config(state=tk.DISABLED)
                    
                self.showStatusMessage("Warning", response["warningMessage"])

            self.inputField.delete(0, "end")

    def showStatusMessage(self, title, message):
        messagebox.showinfo(title=title, message=message)

def main():
    App()

if __name__ == "__main__":
    main()
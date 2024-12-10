import os
import tkinter as tk
from tkinter import messagebox
from script import *

INSTRUCTION = """
    1. Copy and paste your batch file from your Downloads folder into 'Batch Filename' field. (Note: Your batch file needs to be in the Downloads folder.)\n
    2. Click the 'Batch' button or hit Enter on your keyboard.\n
    3. If there is a warning or error, a pop-up will show up with the message.\n
    4. If it is successful, an Excel file with the result will open automatically.\n
    5. This program automatically converts quantity to CASE, BOX, and EACH. This program also splits SKUs bundle into individual SKU.\n
    6. Copy the information from the Excel file onto SAP. (Note: If you are selecting all the columns when copying to SAP, make sure the columns order match.)\n
    7. Do not forget to enter the Discount amount on SAP, if there is any.\n
"""

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap("./assets/icon/icon.ico")
        self.root.title("Order Batcher - {}".format(APP_VERSION))
        self.root.geometry("450x350")

        self.frame1 = tk.Frame(self.root)
        self.frame1.pack()

        self.howToButton = tk.Button(self.frame1, text="?", width=2, height=1, command=self.showInstruction)
        self.howToButton.pack(side=tk.TOP, anchor=tk.NE, padx=(0,20), pady=(4,0))

        self.labelFrame1 = tk.LabelFrame(self.frame1, text="Batch Filename")
        self.labelFrame1.pack(padx=20, pady=20)

        self.inputField = tk.Entry(self.labelFrame1, font=("Arial", 10), width=50)
        self.inputField.bind("<KeyPress>", self.onEnter)
        self.inputField.pack(padx=10, pady=(5,10))

        self.submitButton = tk.Button(self.frame1, text="Batch", font=("Arial", 9), command=self.submitBatch, width=20)
        self.submitButton.pack(padx=10, pady=0)

        self.statusMessage = tk.Label(self.frame1, text='', font=("Arial", 9))
        self.statusMessage.pack(padx=10, pady=10)

        self.labelFrame2 = tk.LabelFrame(self.frame1, text="Message")
        self.labelFrame2.pack(padx=20, pady=20)

        self.infoBox = tk.Text(self.labelFrame2, font=("Arial", 9), width=50)
        self.infoBox.pack(padx=10, pady=(5,10))
        self.infoBox.config(state=tk.DISABLED)
        
        self.root.mainloop()

    def showInstruction(self):
        messagebox.showinfo(title='Instruction', message=INSTRUCTION)

    def onEnter(self, event):
        if event.keysym == "Return":
            self.submitBatch()

    def clearMessages(self):
        self.infoBox.config(state=tk.NORMAL)
        self.infoBox.delete('1.0', tk.END)
        self.infoBox.config(state=tk.DISABLED)
        self.statusMessage.config(text="")

    def submitBatch(self):
        self.clearMessages()
        
        inputFilename = self.inputField.get()

        if len(inputFilename) != 0:
            self.statusMessage.config(text="Processing...")
            self.root.update()
            
            response = batchOrders(inputFilename)

            if response["success"]:
                self.statusMessage.config(text="Your output filename is: " + response["outputFilename"])
                os.system("start EXCEL.EXE " + response["outputFilename"])

            if response["success"] is not None and not response["success"]:
                if response["notExistSKUs"]:
                    notExistSKUs = "\n".join(response["notExistSKUs"])
                    self.infoBox.config(state=tk.NORMAL)
                    self.infoBox.insert(tk.END, "** Not Exist: **\n" + notExistSKUs)
                    self.infoBox.config(state=tk.DISABLED)
                self.showStatusMessage("Error", response["errorMessage"])

            if response["warning"] is not None and not response["warning"]:
                if response["outOfStockSKUs"]:
                    outOfStockSKUsList = "\n".join(response["outOfStockSKUs"])
                    self.infoBox.config(state=tk.NORMAL)
                    self.infoBox.insert(tk.END, "** Out of Stock: **\n" + outOfStockSKUsList)
                    self.infoBox.config(state=tk.DISABLED)
                self.showStatusMessage("Warning", response["warningMessage"])

            self.inputField.delete(0, "end")

    def showStatusMessage(self, title, message):
        messagebox.showinfo(title=title, message=message)

def main():
    App()

if __name__ == "__main__":
    main()
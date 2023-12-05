# restaurant_concierge_gui.py
import tkinter as tk
from tkinter import scrolledtext
from restaurant_concierge import RestaurantConcierge
from tkinter import ttk
from tkinter import simpledialog
from tkinter import ttk, simpledialog
import json

class RestaurantConciergeGUI:
    def __init__(self, master, concierge_instance):
        self.master = master
        self.concierge = concierge_instance
        master.title("Restaurant Concierge")
        master.geometry("1280x720")  # Set the initial size of the GUI

        self.label = ttk.Label(master, text="Choose an option:")
        self.label.pack(pady=10)

        self.keyword_entry_label = ttk.Label(master, text="Enter Keyword:")
        self.keyword_entry_label.pack(pady=5)
        self.keyword_entry = ttk.Entry(master)
        self.keyword_entry.pack(pady=5)

        self.button_location = ttk.Button(master, text="Use Current Location", command=self.use_current_location)
        self.button_location.pack(pady=5)

        # self.button_address = ttk.Button(master, text="Enter Address", command=self.enter_address)
        # self.button_address.pack(pady=5)

        self.button_exit = ttk.Button(master, text="Exit", command=master.destroy)
        self.button_exit.pack(pady=10)

        default_text = "Welcome to Restaurant Concierge!\nThe process will take about a min or few min after select option please wait and keep window open."
        # Create a Text widget to display recommendations
        self.result_text = tk.Text(master, height=100, width=260)
        self.result_text.pack(pady=10)
        self.result_text.insert(tk.END, default_text)


    def use_current_location(self):
        # Call the function to get recommendations and update the result_text
        keyword = self.keyword_entry.get()  # Get the keyword from the Entry widget
        result_text = "Results:\n"
        print('res \n', self.get_recommendations(address=None, keyword=keyword))
        result_text += self.get_recommendations(address=None, keyword=keyword)
        self.update_result_text(f'keyword: {keyword} \n {result_text}')


    # def enter_address(self,keyword = None):
    #     address_insert = simpledialog.askstring("Enter Address", "Enter the address you want to search:")
    #     if address_insert:
    #         # Call the function to get recommendations and update the result_text
    #         result_text = "Results:\n"
    #         result_text += self.get_recommendations(address=address_insert,keyword=keyword)
    #         self.update_result_text(result_text)

    def get_recommendations(self, address=None, keyword = ""):
        # Implement the logic to get recommendations here
        # For example, you can call your RestaurantConcierge class to fetch recommendations
        if keyword is None:
            keyword = ""
        recommendations = self.concierge.run_main(keyword = keyword)
        
        if recommendations is None:
            return ""

        temp = ''
        # Convert each dictionary to a single-line JSON-formatted string
        no = 1
        for i in recommendations:
            # temp += str(i.get('name'))+ '   ' +str(i.get('Ambience'))+ '   ' +str(i.get('details'))+  '   '+ str(i.get('combined_score')) +  '   '+ str(i.get('relevance_percentage')) +'\n'
            details_data = i.get('details')
            formatted_details = "\n".join([f"{key}: {value}" for key, value in details_data.items()])

            temp += f"{no}. Name: {i.get('name')}\nRecommand Score: {i.get('combined_score')}\nRelevance with keyword Percentage: {i.get('relevance_percentage')}\nDetails: {formatted_details}\n\n\n"
            no +=1

        # Combine the strings into a single string
        recommendations_str = temp

        return recommendations_str

    def update_result_text(self, text):
        # Update the result_text widget with the provided text
        self.result_text.delete("1.0", tk.END)  # Clear existing text

        # Set default formatting (normal weight)
        self.result_text.tag_configure("normal", font=("Helvetica", 10, "normal"))

        # Set bold formatting for the "bold" tag
        self.result_text.tag_configure("bold", font=("Helvetica", 10, "bold"))

        # Insert the text with formatting
        self.result_text.insert(tk.END, text, "normal")

        # Find the start index of the first name in the text
        start_index = self.result_text.search("Name:", "1.0", tk.END)

        while start_index:
            # Find the end index of the current name
            end_index = self.result_text.search("\n", start_index, tk.END)

            # Tag the current name with the "bold" tag to make it bold
            self.result_text.tag_add("bold", start_index, end_index)

            # Find the start index of the next name in the text
            start_index = self.result_text.search("Name:", end_index, tk.END)

if __name__ == "__main__":
    concierge_instance = RestaurantConcierge()  # Create an instance of RestaurantConcierge
    concierge_instance.read_yelp_data()
    root = tk.Tk()
    app = RestaurantConciergeGUI(root, concierge_instance)  # Pass the instance to the GUI
    root.mainloop()

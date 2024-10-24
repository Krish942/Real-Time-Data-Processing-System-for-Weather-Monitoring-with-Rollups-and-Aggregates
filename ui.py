import tkinter as tk
from tkinter import messagebox
import time
from weather_monitor import get_weather_data, process_weather_data, save_weather_data, calculate_daily_summary, check_thresholds
import json

class WeatherApp:
    def __init__(self, root, config):
        self.root = root
        self.root.title("Weather Monitoring System")
        self.root.geometry("600x550")  # Adjusted to fit all elements
        
        self.api_key = config['api_key']
        self.cities = config['cities']
        self.thresholds = config['thresholds']
        self.interval = config['interval']  # Interval in minutes
        
        self.unit = 'C'  # Default to Celsius
        
        self.create_widgets()
        
        # Start the weather update loop
        self.update_weather_loop()

    def create_widgets(self):
        self.city_var = tk.StringVar(value=self.cities[0])
        self.city_menu = tk.OptionMenu(self.root, self.city_var, *self.cities)
        self.city_menu.pack(pady=10)
        
        self.update_button = tk.Button(self.root, text="Update Weather", command=self.fetch_weather_data)
        self.update_button.pack(pady=10)
        
        self.weather_label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.weather_label.pack(pady=20)
        
        self.alert_label = tk.Label(self.root, text="", font=("Helvetica", 12), fg="red")
        self.alert_label.pack(pady=10)
        
        self.unit_button = tk.Button(self.root, text="Switch to Fahrenheit", command=self.toggle_temperature_unit)
        self.unit_button.pack(pady=10)
        
        self.summary_button = tk.Button(self.root, text="Show Daily Summary", command=self.display_summary)
        self.summary_button.pack(pady=10)
        
        self.summary_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.summary_label.pack(pady=10)
    
    def fetch_weather_data(self):
        city = self.city_var.get()
        data = get_weather_data(city, self.api_key)
        if data:
            self.processed_data = process_weather_data(data)
            save_weather_data(city, self.processed_data)
            self.display_weather(self.processed_data)
            self.check_alerts(self.processed_data)
        else:
            messagebox.showerror("Error", f"Failed to retrieve data for {city}")

    def display_weather(self, data):
        temp_display = self.convert_temperature(data['temp_celsius'])
        feels_like_display = self.convert_temperature(data['feels_like_celsius'])
        
        weather_text = (
            f"Weather: {data['main']}\n"
            f"Temperature: {temp_display:.2f}°{self.unit}\n"
            f"Feels Like: {feels_like_display:.2f}°{self.unit}\n"
            f"Timestamp: {data['timestamp']}"
        )
        self.weather_label.config(text=weather_text)
    
    def check_alerts(self, data):
        alerts = check_thresholds(data, self.thresholds)
        alert_text = "\n".join(alerts) if alerts else "No alerts"
        self.alert_label.config(text=alert_text)

    def display_summary(self):
        city = self.city_var.get()
        summary = calculate_daily_summary(city)
        if summary:
            avg_temp = self.convert_temperature(summary['average_temp'])
            max_temp = self.convert_temperature(summary['max_temp'])
            min_temp = self.convert_temperature(summary['min_temp'])
            
            summary_text = (
                f"Daily Summary for {city}:\n"
                f"Average Temperature: {avg_temp:.2f}°{self.unit}\n"
                f"Max Temperature: {max_temp:.2f}°{self.unit}\n"
                f"Min Temperature: {min_temp:.2f}°{self.unit}\n"
                f"Dominant Condition: {summary['dominant_condition']}"
            )
            self.summary_label.config(text=summary_text)
        else:
            messagebox.showinfo("Info", f"No data available for {city} today.")
    
    def toggle_temperature_unit(self):
        # Toggle between Celsius and Fahrenheit
        if self.unit == 'C':
            self.unit = 'F'
            self.unit_button.config(text="Switch to Celsius")
        else:
            self.unit = 'C'
            self.unit_button.config(text="Switch to Fahrenheit")
        
        # Refresh displayed weather data if it exists
        if hasattr(self, 'processed_data'):
            self.display_weather(self.processed_data)

    def convert_temperature(self, temp_celsius):
        # Convert temperature to the selected unit (Celsius or Fahrenheit)
        if self.unit == 'F':
            return (temp_celsius * 9/5) + 32
        else:
            return temp_celsius

    def update_weather_loop(self):
        # Fetch the weather data and update the UI
        self.fetch_weather_data()
        
        # Call this function again after `self.interval * 60 * 1000` milliseconds (for periodic updates)
        # self.root.after(self.interval * 60 * 1000, self.update_weather_loop)
        self.root.after( 5000, self.update_weather_loop)
if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    
    root = tk.Tk()
    app = WeatherApp(root, config)
    root.mainloop()

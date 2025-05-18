import json
import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from PIL import Image, ImageTk

class UploaderLogViewer:
    def __init__(self, root, json_path):
        self.root = root
        self.json_path = json_path
        self.log_data = self.load_json()

        self.root.title("Presence Uploader Logs")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("Channel.TFrame", background="#ffffff", relief="raised", borderwidth=1)
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"), background="#f5f5f5")
        self.style.configure("Channel.TLabel", font=("Arial", 14, "bold"), background="#ffffff")
        self.style.configure("Success.TLabel", foreground="green")
        self.style.configure("Failed.TLabel", foreground="red")

        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header = ttk.Label(self.main_frame, text="Presence Uploader Logs", style="Header.TLabel")
        header.pack(pady=(0, 20))

        refresh_button = ttk.Button(self.main_frame, text="Refresh Data", command=self.refresh_data)
        refresh_button.pack(pady=(0, 20))

        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.details_tab = ttk.Frame(self.tab_control)
        self.timeline_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.details_tab, text="Details")
        self.tab_control.add(self.timeline_tab, text="Timeline")

        self.init_dashboard()
        self.init_details()
        self.init_timeline()

        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def load_json(self):
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON: {e}")
            return {}

    def refresh_data(self):
        self.log_data = self.load_json()
        for widget in self.dashboard_tab.winfo_children():
            widget.destroy()
        for widget in self.details_tab.winfo_children():
            widget.destroy()
        for widget in self.timeline_tab.winfo_children():
            widget.destroy()

        self.init_dashboard()
        self.init_details()
        self.init_timeline()

    def init_dashboard(self):
        scrollable_canvas = tk.Canvas(self.dashboard_tab, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(self.dashboard_tab, orient="vertical", command=scrollable_canvas.yview)
        scrollable_frame = ttk.Frame(scrollable_canvas, style="TFrame")

        scrollable_frame.bind("<Configure>", lambda e: scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all")))

        scrollable_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        summary_frame = ttk.Frame(scrollable_frame, style="TFrame")
        summary_frame.pack(fill="x", pady=10)

        ttk.Label(summary_frame, text="Upload Status Summary", style="Header.TLabel").pack(pady=10)

        channels = len(self.log_data)
        platforms = set()
        total_uploads = 0
        successful = 0

        for channel, platforms_data in self.log_data.items():
            for platform, data in platforms_data.items():
                platforms.add(platform)
                total_uploads += 1
                if data.get("status") == "success":
                    successful += 1

        failed = total_uploads - successful

        stats_frame = ttk.Frame(summary_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)

        stats = [
            ("Channels", channels),
            ("Platforms", len(platforms)),
            ("Total Uploads", total_uploads),
            ("Successful", successful),
            ("Failed", failed)
        ]

        for i, (label, value) in enumerate(stats):
            ttk.Label(stats_frame, text=f"{label}:", font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            ttk.Label(stats_frame, text=str(value), font=("Arial", 12)).grid(row=i, column=1, sticky="w", padx=10, pady=5)

        if total_uploads > 0:
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)

            labels = ['Success', 'Failed']
            sizes = [successful, failed]
            colors = ['#4CAF50', '#F44336']

            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title('Upload Success Rate')

            fig_canvas = FigureCanvasTkAgg(fig, summary_frame)
            fig_canvas.draw()
            fig_canvas.get_tk_widget().pack(pady=10)

        if platforms:
            platform_stats = {}
            for channel, platforms_data in self.log_data.items():
                for platform in platforms_data:
                    if platform not in platform_stats:
                        platform_stats[platform] = 0
                    platform_stats[platform] += 1

            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            platform_keys = list(platform_stats.keys())
            counts = list(platform_stats.values())

            ax.bar(platform_keys, counts, color='#2196F3')
            ax.set_title('Uploads per Platform')
            ax.set_ylabel('Number of Uploads')

            fig_canvas = FigureCanvasTkAgg(fig, summary_frame)
            fig_canvas.draw()
            fig_canvas.get_tk_widget().pack(pady=10)

    def init_details(self):
        scrollable_canvas = tk.Canvas(self.details_tab, bg="#f5f5f5")
        v_scrollbar = ttk.Scrollbar(self.details_tab, orient="vertical", command=scrollable_canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.details_tab, orient="horizontal", command=scrollable_canvas.xview)
        scrollable_frame = ttk.Frame(scrollable_canvas, style="TFrame")

        scrollable_frame.bind("<Configure>", lambda e: scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all")))

        scrollable_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        scrollable_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        if not self.log_data:
            ttk.Label(scrollable_frame, text="No data available", font=("Arial", 14)).pack(pady=20)
            return

        for channel, platforms_data in self.log_data.items():
            channel_frame = ttk.Frame(scrollable_frame, style="Channel.TFrame")
            channel_frame.pack(fill="x", padx=10, pady=10, ipadx=10, ipady=10)

            ttk.Label(channel_frame, text=channel, style="Channel.TLabel").pack(anchor="w", padx=10, pady=5)

            table_frame = ttk.Frame(channel_frame)
            table_frame.pack(fill="x", padx=10, pady=5)

            headers = ["Platform", "Last Upload", "Status", "Exception", "Log File"]
            for i, header in enumerate(headers):
                ttk.Label(table_frame, text=header, font=("Arial", 11, "bold")).grid(row=0, column=i, sticky="w", padx=5, pady=5)

            for i, (platform, data) in enumerate(platforms_data.items(), 1):
                ttk.Label(table_frame, text=platform).grid(row=i, column=0, sticky="w", padx=5, pady=3)
                ttk.Label(table_frame, text=data.get("last_uploaded", "N/A")).grid(row=i, column=1, sticky="w", padx=5, pady=3)

                status = data.get("status", "unknown")
                status_style = "Success.TLabel" if status == "success" else "Failed.TLabel"
                ttk.Label(table_frame, text=status, style=status_style).grid(row=i, column=2, sticky="w", padx=5, pady=3)

                exception_text = data.get("exception", "")
                exception_box = tk.Text(table_frame, height=2, width=50, wrap="word", font=("Arial", 9))
                exception_box.insert("1.0", exception_text)
                exception_box.configure(state="disabled", bg="#f0f0f0", relief="solid")
                exception_box.grid(row=i, column=3, sticky="w", padx=5, pady=3)

                log_path = data.get("log_file", "")
                if os.path.isfile(log_path):
                    def make_open_callback(path=log_path):
                        return lambda: os.startfile(path)
                    view_button = ttk.Button(table_frame, text="View Log", command=make_open_callback(log_path))
                    view_button.grid(row=i, column=4, padx=5, pady=3)
                else:
                    ttk.Label(table_frame, text="No Log").grid(row=i, column=4, padx=5, pady=3)


    def init_timeline(self):
        scrollable_canvas = tk.Canvas(self.timeline_tab, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(self.timeline_tab, orient="vertical", command=scrollable_canvas.yview)
        scrollable_frame = ttk.Frame(scrollable_canvas, style="TFrame")

        scrollable_frame.bind("<Configure>", lambda e: scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all")))

        scrollable_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not self.log_data:
            ttk.Label(scrollable_frame, text="No data available", font=("Arial", 14)).pack(pady=20)
            return

        upload_data = []
        for channel, platforms_data in self.log_data.items():
            for platform, data in platforms_data.items():
                if "last_uploaded" in data and data["last_uploaded"]:
                    try:
                        timestamp = datetime.strptime(data["last_uploaded"], "%Y-%m-%d %H:%M:%S")
                        status = data.get("status", "unknown")
                        upload_data.append({"channel": channel, "platform": platform, "timestamp": timestamp, "status": status})
                    except ValueError:
                        continue

        upload_data.sort(key=lambda x: x["timestamp"])

        if upload_data:
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            channels = list(set(item["channel"] for item in upload_data))
            platforms = list(set(item["platform"] for item in upload_data))

            y_positions = {}
            for i, channel in enumerate(channels):
                for j, platform in enumerate(platforms):
                    y_positions[(channel, platform)] = i * (len(platforms) + 1) + j

            x_dates, y_pos, colors, labels = [], [], [], []

            for item in upload_data:
                x_dates.append(item["timestamp"])
                y_pos.append(y_positions[(item["channel"], item["platform"])])
                colors.append("green" if item["status"] == "success" else "red")
                labels.append(f"{item['channel']} - {item['platform']} ({item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})")

            scatter = ax.scatter(x_dates, y_pos, c=colors, s=80, alpha=0.7)

            y_labels = [f"{ch} - {pl}" for ch in channels for pl in platforms]
            ax.set_yticks(list(y_positions.values()))
            ax.set_yticklabels(y_labels)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            fig.autofmt_xdate()
            ax.set_title('Upload Timeline by Channel and Platform')
            ax.grid(True, linestyle='--', alpha=0.7)

            tooltip_frame = ttk.Frame(scrollable_frame, padding=5)
            tooltip_frame.pack(fill="x", pady=10)

            tooltip_label = ttk.Label(tooltip_frame, text="Hover over points to see details")
            tooltip_label.pack(pady=5)

            fig_canvas = FigureCanvasTkAgg(fig, scrollable_frame)
            fig_canvas.draw()
            canvas_widget = fig_canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True, pady=10)

            def hover(event):
                if event.inaxes == ax:
                    cont, ind = scatter.contains(event)
                    if cont:
                        i = ind["ind"][0]
                        tooltip_label.config(text=labels[i])
                    else:
                        tooltip_label.config(text="Hover over points to see details")

            fig_canvas.figure.canvas.mpl_connect("motion_notify_event", hover)

        ttk.Label(scrollable_frame, text="Recent Uploads", style="Header.TLabel").pack(pady=10)
        list_frame = ttk.Frame(scrollable_frame)
        list_frame.pack(fill="x", padx=20, pady=10)

        headers = ["Timestamp", "Channel", "Platform", "Status"]
        for i, header in enumerate(headers):
            ttk.Label(list_frame, text=header, font=("Arial", 11, "bold")).grid(row=0, column=i, sticky="w", padx=10, pady=5)

        upload_data.reverse()
        for i, item in enumerate(upload_data[:20], 1):
            timestamp_str = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            ttk.Label(list_frame, text=timestamp_str).grid(row=i, column=0, sticky="w", padx=10, pady=3)
            ttk.Label(list_frame, text=item["channel"]).grid(row=i, column=1, sticky="w", padx=10, pady=3)
            ttk.Label(list_frame, text=item["platform"]).grid(row=i, column=2, sticky="w", padx=10, pady=3)
            status_style = "Success.TLabel" if item["status"] == "success" else "Failed.TLabel"
            ttk.Label(list_frame, text=item["status"], style=status_style).grid(row=i, column=3, sticky="w", padx=10, pady=3)

    def on_tab_change(self, event):
        tab_id = self.tab_control.select()
        tab_name = self.tab_control.tab(tab_id, "text")
        print(f"Switched to {tab_name} tab")

if __name__ == "__main__":
    json_path = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Uploader\\Logs\\global_uploader_logs.json"
    root = tk.Tk()
    app = UploaderLogViewer(root, json_path)

    try:
        icon = tk.PhotoImage(data="""R0lGODlhIAAgAPcAAP///...AAA7""")
        root.iconphoto(True, icon)
    except:
        pass

    root.mainloop()

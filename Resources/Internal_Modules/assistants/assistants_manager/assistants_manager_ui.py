import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

MODULES_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules"
sys.path.insert(0, MODULES_DIR)
from assistants.assistants_manager.assistants_manager import OpenAIAssistantManager

manager = OpenAIAssistantManager()

def assign_agent():
    name = agent_name_entry.get().strip()
    instructions = instructions_text.get("1.0", tk.END).strip()
    tools_raw = tools_entry.get().strip()

    if not name or not instructions:
        messagebox.showerror("Input Error", "Both Agent Name and Instructions are required.")
        return

    try:
        tools_list = [t.strip() for t in tools_raw.split(",")] if tools_raw else []
        tools_schema = [{"type": "function", "function": {"name": t}} for t in tools_list]

        agent_id = manager.assign_agent(name=name, instructions=instructions, tools=tools_schema)
        result_label.config(text=f"✅ Assigned Agent ID: {agent_id}")
        result_label.bind("<Button-1>", lambda e: copy_to_clipboard(agent_id))
        result_label.config(cursor="hand2")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_agent():
    name = agent_name_entry.get().strip()
    instructions = instructions_text.get("1.0", tk.END).strip()
    tools_raw = tools_entry.get().strip()

    if not name or not instructions:
        messagebox.showerror("Input Error", "Both Agent Name and Instructions are required.")
        return

    try:
        tools_list = [t.strip() for t in tools_raw.split(",")] if tools_raw else []
        tools_schema = [{"type": "function", "function": {"name": t}} for t in tools_list]

        manager.update_agent_instructions(name=name, new_instructions=instructions, tools=tools_schema)
        agent_id = manager.get_agent_id(name)
        result_label.config(text=f"✅ Updated Agent ID: {agent_id}")
        result_label.bind("<Button-1>", lambda e: copy_to_clipboard(agent_id))
        result_label.config(cursor="hand2")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    messagebox.showinfo("Copied", f"Copied to clipboard:\n{text}")

def see_all_agents():
    agents = manager.list_all_agents()
    if not agents:
        messagebox.showinfo("No Agents", "No agents found.")
        return

    window = tk.Toplevel(root)
    window.title("All Agents")

    for agent_str in agents:
        name, agent_id = agent_str.rsplit("(", 1)
        agent_id = agent_id.strip(") ")

        btn = tk.Button(window, text=agent_str, width=60,
                        command=lambda aid=agent_id: show_agent_details(aid))
        btn.pack(padx=5, pady=5)

def show_agent_details(assistant_id):
    try:
        details = manager.get_agent_details(assistant_id)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    detail_win = tk.Toplevel(root)
    detail_win.title(f"Agent: {details['name']}")

    tk.Label(detail_win, text=f"Agent ID: {assistant_id}", fg="blue", cursor="hand2").pack(pady=5)
    label = detail_win.children[list(detail_win.children)[-1]]
    label.bind("<Button-1>", lambda e: copy_to_clipboard(assistant_id))

    tk.Label(detail_win, text=f"Model: {details['model']}").pack(pady=5)

    # Instructions
    tk.Label(detail_win, text="Instructions:").pack(pady=5)
    instructions_box = scrolledtext.ScrolledText(detail_win, width=60, height=15)
    instructions_box.insert(tk.END, details["instructions"])
    instructions_box.pack(padx=5, pady=5)

    # Tools (editable)
    current_tools = ", ".join([
        getattr(t.function, "name", "") for t in details["tools"]
        if getattr(t, "type", None) == "function"
    ]) if details["tools"] else ""
    tk.Label(detail_win, text="Tools (comma-separated function names):").pack(pady=5)
    tools_box = tk.Entry(detail_win, width=60)
    tools_box.insert(0, current_tools)
    tools_box.pack(pady=5)

    def update_instructions_and_tools():
        new_text = instructions_box.get("1.0", tk.END).strip()
        tools_raw = tools_box.get().strip()
        tools_list = [t.strip() for t in tools_raw.split(",")] if tools_raw else []
        tools_schema = [{"type": "function", "function": {"name": t}} for t in tools_list]

        try:
            # ✅ only call manager method
            manager.update_agent_instructions(
                name=details["name"],
                new_instructions=new_text,
                tools=tools_schema
            )
            messagebox.showinfo("Success", "Agent updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_agent():
        try:
            # ✅ only call manager method
            manager.delete_agent(assistant_id=assistant_id)
            messagebox.showinfo("Deleted", f"Assistant {assistant_id} deleted.")
            detail_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


    update_btn = tk.Button(detail_win, text="Update Agent", command=update_instructions_and_tools)
    update_btn.pack(pady=5)

    delete_btn = tk.Button(detail_win, text="❌ Delete Agent", fg="red", command=delete_agent)
    delete_btn.pack(pady=5)

# =================== UI SETUP ==========================
root = tk.Tk()
root.title("OpenAI Agent Manager")

tk.Label(root, text="Agent Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
agent_name_entry = tk.Entry(root, width=40)
agent_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Agent Instructions:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
instructions_text = scrolledtext.ScrolledText(root, width=60, height=15)
instructions_text.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Tools (comma-separated):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
tools_entry = tk.Entry(root, width=60)
tools_entry.grid(row=2, column=1, padx=5, pady=5)

button_frame = tk.Frame(root)
button_frame.grid(row=3, column=1, pady=10)

assign_button = tk.Button(button_frame, text="Assign Agent", width=20, command=assign_agent)
assign_button.pack(side="left", padx=5)

see_agents_button = tk.Button(root, text="See All Agents", width=20, command=see_all_agents)
see_agents_button.grid(row=4, column=1, pady=10)

result_label = tk.Label(root, text="", fg="green")
result_label.grid(row=5, column=1, pady=10)

root.mainloop()

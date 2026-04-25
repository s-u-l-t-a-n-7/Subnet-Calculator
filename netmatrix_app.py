import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ipaddress
import csv
import webbrowser # استيراد مكتبة لفتح الروابط

def get_subnet_details(ip_input):
    """
    Calculates the details of a given subnet.
    """
    try:
        network = ipaddress.ip_network(ip_input, strict=False)
        network_address = network.network_address
        broadcast_address = network.broadcast_address
        netmask = network.netmask
        prefix_length = network.prefixlen
        total_hosts = network.num_addresses - 2 if network.prefixlen < 31 else 0
        if total_hosts < 0: total_hosts = 0
        
        if total_hosts > 0:
            first_host = network_address + 1
            last_host = broadcast_address - 1
        else:
            first_host, last_host = "N/A", "N/A"

        return {
            "is_valid": True, "network_address": str(network_address), "broadcast_address": str(broadcast_address),
            "netmask": str(netmask), "prefix_length": prefix_length, "total_hosts": total_hosts,
            "host_range": f"{first_host} - {last_host}", "input": ip_input, "num_addresses": network.num_addresses
        }
    except ValueError as e:
        return {"is_valid": False, "error": str(e)}

class SubnetCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetMatrix Subnetting Suite v5.1")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # Classic colors
        self.bg_color = "#f0f0f0"; self.fg_color = "#000000"; self.gold = "#c9a03d"
        self.red = "#cc0000"; self.green = "#008000"; self.gray = "#808080"
        
        self.root.configure(bg=self.bg_color)
        
        self.setup_styles()
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color, font=('Tahoma', 10))
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Heading.TLabel', font=('Tahoma', 11, 'bold'), foreground=self.gold)
        self.style.configure('Card.TLabelframe', relief=tk.GROOVE, borderwidth=2, background=self.bg_color)
        self.style.configure('Card.TLabelframe.Label', font=('Tahoma', 10, 'bold'), foreground=self.gold)
        self.style.configure('Action.TButton', font=('Tahoma', 9), padding=6)
        self.style.map('Action.TButton', background=[('active', self.gold)])
        self.style.configure('TNotebook', background=self.bg_color, borderwidth=1)
        self.style.configure('TNotebook.Tab', font=('Tahoma', 9, 'bold'), padding=[12, 4])
        self.style.map('TNotebook.Tab', background=[('selected', self.gold)], foreground=[('selected', 'white')])
        self.style.configure('Treeview', background='white', foreground='black', rowheight=25, fieldbackground='white')
        self.style.configure('Treeview.Heading', font=('Tahoma', 9, 'bold'), background=self.gray, foreground='white')
        self.style.map('Treeview.Heading', background=[('active', self.gold)])
        self.style.configure('TEntry', fieldbackground='white', foreground='black', borderwidth=1)
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.bg_color, fg=self.fg_color, activebackground=self.gold)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to CSV", command=self.export_current_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # --- قائمة المطور الجديدة ---
        dev_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        menubar.add_cascade(label="Developer", menu=dev_menu)
        dev_menu.add_command(label="GitHub: s-u-l-t-a-n-7", command=lambda: webbrowser.open_new_tab("https://github.com/s-u-l-t-a-n-7" ))
        dev_menu.add_separator()
        dev_menu.add_command(label="Telegram: @Sul4384", command=lambda: webbrowser.open_new_tab("https://t.me/Sul4384" ))
        dev_menu.add_command(label="Telegram: @SAM_CYS", command=lambda: webbrowser.open_new_tab("https://t.me/SAM_CYS" ))
        dev_menu.add_separator()
        dev_menu.add_command(label="Email: samsultan95.15@gmail.com", command=lambda: webbrowser.open_new_tab("mailto:samsultan95.15@gmail.com"))
        
    def show_about(self):
        messagebox.showinfo("About", "NetMatrix Subnetting Suite v5.1\n\nDeveloped by: Sultan Shamsan\nAssisted by: Manus AI")
        
    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root); self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.notebook = ttk.Notebook(self.main_frame); self.notebook.pack(fill="both", expand=True)
        self.tab_calculator = ttk.Frame(self.notebook); self.tab_subnetter = ttk.Frame(self.notebook); self.tab_vlsm = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_calculator, text="IP Calculator"); self.notebook.add(self.tab_subnetter, text="Subnet Generator"); self.notebook.add(self.tab_vlsm, text="VLSM Planner")
        self.create_calculator_tab(); self.create_subnetter_tab(); self.create_vlsm_tab()
        
    def create_calculator_tab(self):
        input_frame = ttk.LabelFrame(self.tab_calculator, text="Network Input", style='Card.TLabelframe'); input_frame.pack(fill="x", padx=10, pady=10)
        row1 = ttk.Frame(input_frame); row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="IP Address:", width=15).pack(side="left", padx=5)
        self.ip_entry = ttk.Entry(row1, width=25); self.ip_entry.pack(side="left", padx=5); self.ip_entry.insert(0, "192.168.1.1")
        row2 = ttk.Frame(input_frame); row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="Subnet Mask:", width=15).pack(side="left", padx=5)
        self.mask_entry = ttk.Entry(row2, width=25); self.mask_entry.pack(side="left", padx=5); self.mask_entry.insert(0, "/24")
        row3 = ttk.Frame(input_frame); row3.pack(fill="x", pady=5)
        ttk.Label(row3, text="Quick:", width=15).pack(side="left", padx=5)
        for mask in ["/24", "/16", "/8"]:
            btn = ttk.Button(row3, text=mask, command=lambda m=mask: self.mask_entry.delete(0, tk.END) or self.mask_entry.insert(0, m), style='Action.TButton')
            btn.pack(side="left", padx=2)
        btn_frame = ttk.Frame(self.tab_calculator); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Calculate", command=self.calculate, style='Action.TButton').pack()
        results_frame = ttk.LabelFrame(self.tab_calculator, text="Results", style='Card.TLabelframe'); results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        text_frame = ttk.Frame(results_frame); text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.results_text = tk.Text(text_frame, height=12, wrap="word", bg="white", fg="black", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview); self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        
    def create_subnetter_tab(self):
        config_frame = ttk.LabelFrame(self.tab_subnetter, text="Subnet Configuration", style='Card.TLabelframe'); config_frame.pack(fill="x", padx=10, pady=10)
        row1 = ttk.Frame(config_frame); row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="Main Network:", width=18).pack(side="left", padx=5)
        self.network_entry = ttk.Entry(row1, width=30); self.network_entry.pack(side="left", padx=5); self.network_entry.insert(0, "192.168.0.0/16")
        row2 = ttk.Frame(config_frame); row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="Subnet by:", width=18).pack(side="left", padx=5)
        self.subnet_mode = tk.StringVar(value="hosts")
        ttk.Radiobutton(row2, text="Number of Hosts", variable=self.subnet_mode, value="hosts").pack(side="left", padx=10)
        ttk.Radiobutton(row2, text="Number of Subnets", variable=self.subnet_mode, value="subnets").pack(side="left", padx=10)
        row3 = ttk.Frame(config_frame); row3.pack(fill="x", pady=5)
        ttk.Label(row3, text="Required Value:", width=18).pack(side="left", padx=5)
        self.value_entry = ttk.Entry(row3, width=15); self.value_entry.pack(side="left", padx=5); self.value_entry.insert(0, "250")
        btn_frame = ttk.Frame(self.tab_subnetter); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Generate Subnets", command=self.perform_subnetting, style='Action.TButton').pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_subnetter_to_csv, style='Action.TButton').pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.clear_treeview(self.tree), style='Action.TButton').pack(side="left", padx=5)
        results_frame = ttk.LabelFrame(self.tab_subnetter, text="Generated Subnets", style='Card.TLabelframe'); results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tree_frame = ttk.Frame(results_frame); tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        cols = ("#", "Network ID", "CIDR", "Host Range", "Broadcast", "Hosts")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        for col in cols: self.tree.heading(col, text=col)
        self.tree.column("#", width=50, anchor="center"); self.tree.column("CIDR", width=70, anchor="center"); self.tree.column("Hosts", width=80, anchor="center")
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew"); v_scroll.grid(row=0, column=1, sticky="ns"); h_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)
        
    def create_vlsm_tab(self):
        config_frame = ttk.LabelFrame(self.tab_vlsm, text="VLSM Configuration", style='Card.TLabelframe'); config_frame.pack(fill="x", padx=10, pady=10)
        row1 = ttk.Frame(config_frame); row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="Main Network:", width=18).pack(side="left", padx=5)
        self.vlsm_network = ttk.Entry(row1, width=35); self.vlsm_network.pack(side="left", padx=5); self.vlsm_network.insert(0, "10.0.0.0/8")
        req_frame = ttk.LabelFrame(config_frame, text="Department Requirements", style='Card.TLabelframe'); req_frame.pack(fill="x", pady=10, padx=5)
        header = ttk.Frame(req_frame); header.pack(fill="x", pady=5)
        ttk.Label(header, text="Department Name", width=20).pack(side="left", padx=5); ttk.Label(header, text="Required Hosts", width=15).pack(side="left", padx=5)
        self.req_container = ttk.Frame(req_frame); self.req_container.pack(fill="x", pady=5)
        self.requirements = []
        self.add_requirement("Engineering", "1000"); self.add_requirement("Sales", "500")
        btn_frame = ttk.Frame(req_frame); btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Department", command=self.add_requirement, style='Action.TButton').pack(side="left", padx=5)
        main_btn_frame = ttk.Frame(self.tab_vlsm); main_btn_frame.pack(pady=10)
        ttk.Button(main_btn_frame, text="Calculate VLSM", command=self.perform_vlsm, style='Action.TButton').pack(side="left", padx=5)
        ttk.Button(main_btn_frame, text="Export CSV", command=self.export_vlsm_to_csv, style='Action.TButton').pack(side="left", padx=5)
        ttk.Button(main_btn_frame, text="Clear", command=lambda: self.clear_treeview(self.vlsm_tree), style='Action.TButton').pack(side="left", padx=5)
        results_frame = ttk.LabelFrame(self.tab_vlsm, text="VLSM Plan", style='Card.TLabelframe'); results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tree_frame = ttk.Frame(results_frame); tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        cols = ("Department", "Required", "Allocated", "Network ID", "CIDR", "Host Range", "Broadcast")
        self.vlsm_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        for col in cols: self.vlsm_tree.heading(col, text=col)
        self.vlsm_tree.column("CIDR", width=60, anchor="center"); self.vlsm_tree.column("Required", width=80, anchor="center"); self.vlsm_tree.column("Allocated", width=80, anchor="center")
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.vlsm_tree.yview); h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.vlsm_tree.xview)
        self.vlsm_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.vlsm_tree.grid(row=0, column=0, sticky="nsew"); v_scroll.grid(row=0, column=1, sticky="ns"); h_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)
        
    def add_requirement(self, name="", hosts=""):
        frame = ttk.Frame(self.req_container)
        frame.pack(fill="x", pady=2)
        name_entry = ttk.Entry(frame, width=25); name_entry.pack(side="left", padx=5); name_entry.insert(0, name)
        hosts_entry = ttk.Entry(frame, width=15); hosts_entry.pack(side="left", padx=5); hosts_entry.insert(0, hosts)
        # --- إصلاح الحذف ---
        delete_btn = ttk.Button(frame, text="Delete", command=lambda f=frame: self.delete_requirement(f), style='Action.TButton')
        delete_btn.pack(side="left", padx=5)
        self.requirements.append({'frame': frame, 'name': name_entry, 'hosts': hosts_entry})
        
    def delete_requirement(self, frame_to_delete):
        if len(self.requirements) <= 1:
            messagebox.showwarning("Warning", "At least one department is required"); return
        
        # البحث عن العنصر المراد حذفه وتدميره
        for i, req in enumerate(self.requirements):
            if req['frame'] == frame_to_delete:
                req['frame'].destroy()
                self.requirements.pop(i)
                break
        
    def clear_treeview(self, treeview):
        for item in treeview.get_children(): treeview.delete(item)
            
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor="w"); self.status_bar.pack(side=tk.BOTTOM, fill="x")
        
    def calculate(self):
        ip = self.ip_entry.get().strip(); mask = self.mask_entry.get().strip()
        if not ip or not mask: messagebox.showerror("Error", "Please enter IP address and subnet mask"); return
        if '/' in ip: full_ip = ip
        else:
            try:
                if not mask.startswith('/'): prefix = ipaddress.ip_network(f'0.0.0.0/{mask}').prefixlen; full_ip = f"{ip}/{prefix}"
                else: full_ip = f"{ip}{mask}"
            except ValueError: messagebox.showerror("Error", f"Invalid subnet mask: {mask}"); return
        details = get_subnet_details(full_ip)
        self.results_text.config(state="normal"); self.results_text.delete(1.0, tk.END)
        if details["is_valid"]:
            result = f"""{'='*50}\nNetwork Details\n{'='*50}\n\nInput:              {details['input']}\nNetwork Address:    {details['network_address']}\nNetmask:            {details['netmask']} (/{details['prefix_length']})\nBroadcast Address:  {details['broadcast_address']}\nUsable Host Range:  {details['host_range']}\nAvailable Hosts:    {details['total_hosts']}\n{'='*50}\n"""
            self.results_text.insert(tk.END, result); self.status_bar.config(text="Calculation successful", foreground=self.green)
        else:
            self.results_text.insert(tk.END, f"Error: {details['error']}"); self.status_bar.config(text="Calculation failed", foreground=self.red)
        self.results_text.config(state="disabled")
        
    def perform_subnetting(self):
        self.clear_treeview(self.tree)
        try:
            network = ipaddress.ip_network(self.network_entry.get().strip()); value = int(self.value_entry.get().strip())
            if self.subnet_mode.get() == "hosts":
                if value <= 0: raise ValueError("Hosts must be greater than 0")
                host_bits = (value + 2).bit_length(); new_prefix = 32 - host_bits
            else:
                if value <= 0: raise ValueError("Subnets must be greater than 0")
                subnet_bits = (value - 1).bit_length(); new_prefix = network.prefixlen + subnet_bits
            if new_prefix <= network.prefixlen or new_prefix > 32: raise ValueError("Value too large for this network")
            subnets = list(network.subnets(new_prefix=new_prefix))
            for i, subnet in enumerate(subnets):
                details = get_subnet_details(str(subnet))
                self.tree.insert("", "end", values=(i + 1, details["network_address"], f"/{details['prefix_length']}", details["host_range"], details["broadcast_address"], details["total_hosts"]))
            self.status_bar.config(text=f"Generated {len(subnets)} subnets", foreground=self.green)
        except Exception as e: messagebox.showerror("Error", str(e)); self.status_bar.config(text="Subnetting failed", foreground=self.red)
            
    def perform_vlsm(self):
        self.clear_treeview(self.vlsm_tree)
        try:
            network = ipaddress.ip_network(self.vlsm_network.get().strip())
            requirements = []
            for req in self.requirements:
                name = req['name'].get().strip(); hosts_str = req['hosts'].get().strip()
                if name and hosts_str: requirements.append({"name": name, "hosts": int(hosts_str)})
            if not requirements: messagebox.showwarning("Warning", "Please add at least one department"); return
            requirements.sort(key=lambda x: x["hosts"], reverse=True)
            
            # --- خوارزمية VLSM المحسنة ---
            next_available_address = network.network_address
            results = []
            for req in requirements:
                host_bits = (req["hosts"] + 2).bit_length()
                prefix = 32 - host_bits
                
                # إيجاد أول شبكة فرعية متاحة بالحجم المطلوب
                # تبدأ من العنوان المتاح التالي
                subnet = ipaddress.ip_network(f"{next_available_address}/{prefix}", strict=False)
                
                # التأكد من أن الشبكة الجديدة لا تتجاوز الشبكة الأم
                if not network.supernet_of(subnet):
                    raise ValueError(f"Not enough address space for department '{req['name']}'")
                
                details = get_subnet_details(str(subnet))
                results.append({**req, **details})
                
                # القفز إلى العنوان التالي المتاح مباشرة
                next_available_address = subnet.broadcast_address + 1
                    
            for res in results:
                self.vlsm_tree.insert("", "end", values=(res["name"], res["hosts"], res["total_hosts"], res["network_address"], f"/{res['prefix_length']}", res["host_range"], res["broadcast_address"]))
            self.status_bar.config(text=f"VLSM plan generated for {len(results)} departments", foreground=self.green)
        except Exception as e:
            messagebox.showerror("Error", str(e)); self.status_bar.config(text="VLSM calculation failed", foreground=self.red)
            
    def export_current_results(self):
        current = self.notebook.index(self.notebook.select())
        if current == 1: self.export_subnetter_to_csv()
        elif current == 2: self.export_vlsm_to_csv()
        else: messagebox.showinfo("Info", "Switch to Subnetter or VLSM tab to export")
            
    def export_subnetter_to_csv(self): self.export_treeview_to_csv(self.tree, "subnet_plan")
    def export_vlsm_to_csv(self): self.export_treeview_to_csv(self.vlsm_tree, "vlsm_plan")
        
    def export_treeview_to_csv(self, treeview, filename):
        if not treeview.get_children(): messagebox.showinfo("No Data", "No data to export"); return
        try:
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not path: return
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f); writer.writerow(treeview["columns"])
                for item in treeview.get_children(): writer.writerow(treeview.item(item)["values"])
            self.status_bar.config(text=f"Exported to {path}", foreground=self.green)
        except Exception as e: messagebox.showerror("Error", str(e)); self.status_bar.config(text="Export failed", foreground=self.red)

if __name__ == "__main__":
    root = tk.Tk()
    app = SubnetCalculatorApp(root)
    root.mainloop()

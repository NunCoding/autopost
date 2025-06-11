import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
import cv2

# Install required packages:
# pip install pillow opencv-python customtkinter

try:
    import customtkinter as ctk

    CTK_AVAILABLE = True
except ImportError:
    print("CustomTkinter not available. Install with: pip install customtkinter")
    CTK_AVAILABLE = False


class ModernSocialMediaGUI:
    def __init__(self):
        # Initialize main window
        if CTK_AVAILABLE:
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
            self.setup_ttk_styles()

        self.root.title("Social Media Auto-Poster")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Data storage
        self.videos = []
        self.current_video = None
        self.credentials = {
            'youtube': {'client_id': '', 'client_secret': '', 'authenticated': False},
            'instagram': {'username': '', 'password': '', 'authenticated': False}
        }

        # Create UI
        self.create_widgets()
        self.load_config()

    def setup_ttk_styles(self):
        """Setup modern styles for standard tkinter"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'), foreground='#2563eb')
        style.configure('Heading.TLabel', font=('Helvetica', 12, 'bold'), foreground='#1f2937')
        style.configure('Modern.TButton', font=('Helvetica', 10), padding=10)
        style.configure('Success.TButton', background='#10b981', foreground='white')
        style.configure('Primary.TButton', background='#2563eb', foreground='white')
        style.configure('Danger.TButton', background='#ef4444', foreground='white')

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = self.create_frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        self.create_header(main_frame)

        # Content area
        content_frame = self.create_frame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(20, 0))

        # Left panel - Video list
        self.create_video_list_panel(content_frame)

        # Right panel - Video editor
        self.create_video_editor_panel(content_frame)

        # Status bar
        self.create_status_bar(main_frame)

    def create_frame(self, parent, **kwargs):
        """Create a frame with modern styling"""
        if CTK_AVAILABLE:
            return ctk.CTkFrame(parent, **kwargs)
        else:
            frame = ttk.Frame(parent, **kwargs)
            frame.configure(relief="solid", borderwidth=1)
            return frame

    def create_label(self, parent, text, style=None, **kwargs):
        """Create a label with modern styling"""
        if CTK_AVAILABLE:
            return ctk.CTkLabel(parent, text=text, **kwargs)
        else:
            return ttk.Label(parent, text=text, style=style, **kwargs)

    def create_button(self, parent, text, command=None, style=None, **kwargs):
        """Create a button with modern styling"""
        if CTK_AVAILABLE:
            return ctk.CTkButton(parent, text=text, command=command, **kwargs)
        else:
            return ttk.Button(parent, text=text, command=command, style=style, **kwargs)

    def create_entry(self, parent, **kwargs):
        """Create an entry with modern styling"""
        if CTK_AVAILABLE:
            return ctk.CTkEntry(parent, **kwargs)
        else:
            return ttk.Entry(parent, **kwargs)

    def create_textbox(self, parent, **kwargs):
        """Create a textbox with modern styling"""
        if CTK_AVAILABLE:
            return ctk.CTkTextbox(parent, **kwargs)
        else:
            text_widget = tk.Text(parent, **kwargs)
            text_widget.configure(font=('Helvetica', 10))
            return text_widget

    def create_header(self, parent):
        """Create the header section"""
        header_frame = self.create_frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))

        # Title
        title_label = self.create_label(
            header_frame,
            "🎬 Social Media Auto-Poster",
            font=("Helvetica", 24, "bold") if not CTK_AVAILABLE else None
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Header buttons
        button_frame = self.create_frame(header_frame)
        button_frame.pack(side="right", padx=20, pady=15)

        self.add_videos_btn = self.create_button(
            button_frame,
            "📁 Add Videos",
            command=self.add_videos,
            width=120 if CTK_AVAILABLE else None
        )
        self.add_videos_btn.pack(side="left", padx=5)

        self.upload_all_btn = self.create_button(
            button_frame,
            "🚀 Upload All",
            command=self.upload_all_videos,
            width=120 if CTK_AVAILABLE else None
        )
        self.upload_all_btn.pack(side="left", padx=5)

        self.settings_btn = self.create_button(
            button_frame,
            "⚙️ Settings",
            command=self.show_settings,
            width=120 if CTK_AVAILABLE else None
        )
        self.settings_btn.pack(side="left", padx=5)

    def create_video_list_panel(self, parent):
        """Create the video list panel"""
        # Left panel frame
        left_panel = self.create_frame(parent)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_panel.configure(width=350)

        # Title
        list_title = self.create_label(left_panel, "📹 Video Queue",
                                       font=("Helvetica", 14, "bold") if not CTK_AVAILABLE else None)
        list_title.pack(pady=15)

        # Video list with scrollbar
        list_frame = self.create_frame(left_panel)
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Create scrollable frame
        if CTK_AVAILABLE:
            self.video_list_frame = ctk.CTkScrollableFrame(list_frame)
            self.video_list_frame.pack(fill="both", expand=True)
        else:
            # Create scrollable frame with tkinter
            canvas = tk.Canvas(list_frame, bg='white')
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
            self.video_list_frame = ttk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=self.video_list_frame, anchor="nw")

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Mouse wheel binding
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas.bind("<MouseWheel>", on_mousewheel)

    def create_video_editor_panel(self, parent):
        """Create the video editor panel"""
        # Right panel frame
        right_panel = self.create_frame(parent)
        right_panel.pack(side="right", fill="both", expand=True)

        # Title
        editor_title = self.create_label(right_panel, "✏️ Video Editor",
                                         font=("Helvetica", 14, "bold") if not CTK_AVAILABLE else None)
        editor_title.pack(pady=15)

        # Editor content
        self.editor_frame = self.create_frame(right_panel)
        self.editor_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Default message
        self.show_default_editor_message()

    def show_default_editor_message(self):
        """Show default message when no video is selected"""
        # Clear existing widgets
        for widget in self.editor_frame.winfo_children():
            widget.destroy()

        default_label = self.create_label(
            self.editor_frame,
            "Select a video from the queue to edit its details",
            font=("Helvetica", 12) if not CTK_AVAILABLE else None
        )
        default_label.pack(expand=True)

    def create_video_editor_form(self, video):
        """Create the video editor form"""
        # Clear existing widgets
        for widget in self.editor_frame.winfo_children():
            widget.destroy()

        # Create scrollable form
        if CTK_AVAILABLE:
            form_frame = ctk.CTkScrollableFrame(self.editor_frame)
        else:
            form_frame = self.editor_frame
        form_frame.pack(fill="both", expand=True)

        # Video preview (placeholder)
        preview_frame = self.create_frame(form_frame)
        preview_frame.pack(fill="x", pady=10)

        preview_label = self.create_label(preview_frame, f"🎥 {video['name']}",
                                          font=("Helvetica", 12, "bold") if not CTK_AVAILABLE else None)
        preview_label.pack(pady=10)

        # Title field
        title_frame = self.create_frame(form_frame)
        title_frame.pack(fill="x", pady=5)

        self.create_label(title_frame, "Title:").pack(anchor="w")
        self.title_entry = self.create_entry(title_frame)
        self.title_entry.pack(fill="x", pady=2)
        self.title_entry.insert(0, video.get('title', ''))

        # Description field
        desc_frame = self.create_frame(form_frame)
        desc_frame.pack(fill="x", pady=5)

        self.create_label(desc_frame, "Description:").pack(anchor="w")
        self.desc_text = self.create_textbox(desc_frame, height=100 if CTK_AVAILABLE else 4)
        self.desc_text.pack(fill="x", pady=2)
        if CTK_AVAILABLE:
            self.desc_text.insert("1.0", video.get('description', ''))
        else:
            self.desc_text.insert("1.0", video.get('description', ''))

        # Tags field
        tags_frame = self.create_frame(form_frame)
        tags_frame.pack(fill="x", pady=5)

        self.create_label(tags_frame, "Tags (comma-separated):").pack(anchor="w")
        self.tags_entry = self.create_entry(tags_frame)
        self.tags_entry.pack(fill="x", pady=2)
        self.tags_entry.insert(0, ', '.join(video.get('tags', [])))

        # Platform selection
        platform_frame = self.create_frame(form_frame)
        platform_frame.pack(fill="x", pady=10)

        self.create_label(platform_frame, "Platforms:",
                          font=("Helvetica", 12, "bold") if not CTK_AVAILABLE else None).pack(anchor="w")

        # Platform checkboxes
        self.platform_vars = {}
        platforms = [
            ('youtube', '📺 YouTube'),
            ('instagram', '📷 Instagram'),
            ('tiktok', '🎵 TikTok (Coming Soon)')
        ]

        for platform_id, platform_name in platforms:
            var = tk.BooleanVar(value=platform_id in video.get('platforms', []))
            self.platform_vars[platform_id] = var

            if CTK_AVAILABLE:
                checkbox = ctk.CTkCheckBox(platform_frame, text=platform_name, variable=var)
                if platform_id == 'tiktok':
                    checkbox.configure(state="disabled")
            else:
                checkbox = ttk.Checkbutton(platform_frame, text=platform_name, variable=var)
                if platform_id == 'tiktok':
                    checkbox.configure(state="disabled")

            checkbox.pack(anchor="w", pady=2)

        # Privacy setting
        privacy_frame = self.create_frame(form_frame)
        privacy_frame.pack(fill="x", pady=5)

        self.create_label(privacy_frame, "Privacy:").pack(anchor="w")
        self.privacy_var = tk.StringVar(value=video.get('privacy', 'public'))

        if CTK_AVAILABLE:
            privacy_menu = ctk.CTkOptionMenu(privacy_frame, variable=self.privacy_var,
                                             values=["public", "private"])
        else:
            privacy_menu = ttk.Combobox(privacy_frame, textvariable=self.privacy_var,
                                        values=["public", "private"], state="readonly")
        privacy_menu.pack(fill="x", pady=2)

        # Action buttons
        button_frame = self.create_frame(form_frame)
        button_frame.pack(fill="x", pady=20)

        save_btn = self.create_button(
            button_frame,
            "💾 Save Changes",
            command=lambda: self.save_video_changes(video),
            width=150 if CTK_AVAILABLE else None
        )
        save_btn.pack(side="left", padx=5)

        upload_btn = self.create_button(
            button_frame,
            "🚀 Upload Now",
            command=lambda: self.upload_single_video(video),
            width=150 if CTK_AVAILABLE else None
        )
        upload_btn.pack(side="left", padx=5)

        remove_btn = self.create_button(
            button_frame,
            "🗑️ Remove",
            command=lambda: self.remove_video(video),
            width=150 if CTK_AVAILABLE else None
        )
        remove_btn.pack(side="right", padx=5)

    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = self.create_frame(parent)
        status_frame.pack(fill="x", pady=(20, 0))

        self.status_label = self.create_label(status_frame, "Ready")
        self.status_label.pack(side="left", padx=20, pady=10)

        # Progress bar
        if CTK_AVAILABLE:
            self.progress_bar = ctk.CTkProgressBar(status_frame)
        else:
            self.progress_bar = ttk.Progressbar(status_frame, mode='determinate')
        self.progress_bar.pack(side="right", padx=20, pady=10, fill="x", expand=True)

        if not CTK_AVAILABLE:
            self.progress_bar.configure(value=0)

    def add_videos(self):
        """Add videos to the queue"""
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("All files", "*.*")
            ]
        )

        for file_path in files:
            video = {
                'id': len(self.videos) + 1,
                'path': file_path,
                'name': Path(file_path).name,
                'title': Path(file_path).stem,
                'description': '',
                'tags': [],
                'platforms': ['youtube'],
                'privacy': 'public',
                'status': 'pending'
            }
            self.videos.append(video)

        self.refresh_video_list()
        self.update_status(f"Added {len(files)} video(s)")

    def refresh_video_list(self):
        """Refresh the video list display"""
        # Clear existing items
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()

        if not self.videos:
            no_videos_label = self.create_label(
                self.video_list_frame,
                "No videos in queue\nClick 'Add Videos' to start",
                font=("Helvetica", 10) if not CTK_AVAILABLE else None
            )
            no_videos_label.pack(pady=20)
            return

        # Create video items
        for video in self.videos:
            self.create_video_item(video)

    def create_video_item(self, video):
        """Create a video item in the list"""
        item_frame = self.create_frame(self.video_list_frame)
        item_frame.pack(fill="x", pady=5, padx=5)

        # Video info
        info_frame = self.create_frame(item_frame)
        info_frame.pack(fill="x", padx=10, pady=10)

        # Title
        title_label = self.create_label(
            info_frame,
            video.get('title', video['name']),
            font=("Helvetica", 10, "bold") if not CTK_AVAILABLE else None
        )
        title_label.pack(anchor="w")

        # Status and platforms
        status_text = f"Status: {video['status'].title()}"
        if video.get('platforms'):
            platforms_text = ", ".join([p.title() for p in video['platforms']])
            status_text += f" | Platforms: {platforms_text}"

        status_label = self.create_label(
            info_frame,
            status_text,
            font=("Helvetica", 8) if not CTK_AVAILABLE else None
        )
        status_label.pack(anchor="w")

        # Select button
        select_btn = self.create_button(
            info_frame,
            "Edit",
            command=lambda v=video: self.select_video(v),
            width=80 if CTK_AVAILABLE else None
        )
        select_btn.pack(anchor="e", pady=2)

    def select_video(self, video):
        """Select a video for editing"""
        self.current_video = video
        self.create_video_editor_form(video)
        self.update_status(f"Selected: {video['name']}")

    def save_video_changes(self, video):
        """Save changes to the selected video"""
        try:
            # Get values from form
            if CTK_AVAILABLE:
                title = self.title_entry.get()
                description = self.desc_text.get("1.0", "end-1c")
                tags_text = self.tags_entry.get()
            else:
                title = self.title_entry.get()
                description = self.desc_text.get("1.0", "end-1c")
                tags_text = self.tags_entry.get()

            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
            privacy = self.privacy_var.get()

            # Update video
            video.update({
                'title': title,
                'description': description,
                'tags': tags,
                'platforms': platforms,
                'privacy': privacy
            })

            self.refresh_video_list()
            self.update_status("Changes saved")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

    def remove_video(self, video):
        """Remove a video from the queue"""
        if messagebox.askyesno("Confirm", f"Remove '{video['name']}' from queue?"):
            self.videos.remove(video)
            self.refresh_video_list()
            self.show_default_editor_message()
            self.update_status(f"Removed: {video['name']}")

    def upload_single_video(self, video):
        """Upload a single video"""

        def upload_thread():
            try:
                video['status'] = 'uploading'
                self.refresh_video_list()
                self.update_status(f"Uploading: {video['name']}")

                # Simulate upload process
                for i in range(101):
                    time.sleep(0.05)
                    if CTK_AVAILABLE:
                        self.progress_bar.set(i / 100)
                    else:
                        self.progress_bar.configure(value=i)
                    self.root.update_idletasks()

                video['status'] = 'completed'
                self.refresh_video_list()
                self.update_status(f"Completed: {video['name']}")

                if CTK_AVAILABLE:
                    self.progress_bar.set(0)
                else:
                    self.progress_bar.configure(value=0)

            except Exception as e:
                video['status'] = 'failed'
                self.refresh_video_list()
                messagebox.showerror("Upload Error", f"Failed to upload {video['name']}: {str(e)}")

        threading.Thread(target=upload_thread, daemon=True).start()

    def upload_all_videos(self):
        """Upload all pending videos"""
        pending_videos = [v for v in self.videos if v['status'] == 'pending']

        if not pending_videos:
            messagebox.showinfo("Info", "No pending videos to upload")
            return

        def upload_all_thread():
            for video in pending_videos:
                self.upload_single_video(video)
                time.sleep(1)  # Delay between uploads

        threading.Thread(target=upload_all_thread, daemon=True).start()

    def show_settings(self):
        """Show settings dialog"""
        settings_window = self.create_settings_window()

    def create_settings_window(self):
        """Create settings window"""
        if CTK_AVAILABLE:
            settings_window = ctk.CTkToplevel(self.root)
        else:
            settings_window = tk.Toplevel(self.root)

        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Title
        title_label = self.create_label(
            settings_window,
            "⚙️ Platform Settings",
            font=("Helvetica", 16, "bold") if not CTK_AVAILABLE else None
        )
        title_label.pack(pady=20)

        # YouTube settings
        youtube_frame = self.create_frame(settings_window)
        youtube_frame.pack(fill="x", padx=20, pady=10)

        self.create_label(youtube_frame, "📺 YouTube Settings",
                          font=("Helvetica", 12, "bold") if not CTK_AVAILABLE else None).pack(anchor="w")

        self.create_label(youtube_frame, "Client ID:").pack(anchor="w", pady=(10, 0))
        youtube_id_entry = self.create_entry(youtube_frame)
        youtube_id_entry.pack(fill="x", pady=2)
        youtube_id_entry.insert(0, self.credentials['youtube']['client_id'])

        # Instagram settings
        instagram_frame = self.create_frame(settings_window)
        instagram_frame.pack(fill="x", padx=20, pady=10)

        self.create_label(instagram_frame, "📷 Instagram Settings",
                          font=("Helvetica", 12, "bold") if not CTK_AVAILABLE else None).pack(anchor="w")

        self.create_label(instagram_frame, "Username:").pack(anchor="w", pady=(10, 0))
        instagram_user_entry = self.create_entry(instagram_frame)
        instagram_user_entry.pack(fill="x", pady=2)
        instagram_user_entry.insert(0, self.credentials['instagram']['username'])

        self.create_label(instagram_frame, "Password:").pack(anchor="w", pady=(10, 0))
        instagram_pass_entry = self.create_entry(instagram_frame)
        if CTK_AVAILABLE:
            instagram_pass_entry.configure(show="*")
        else:
            instagram_pass_entry.configure(show="*")
        instagram_pass_entry.pack(fill="x", pady=2)
        instagram_pass_entry.insert(0, self.credentials['instagram']['password'])

        # Buttons
        button_frame = self.create_frame(settings_window)
        button_frame.pack(fill="x", padx=20, pady=20)

        def save_settings():
            self.credentials['youtube']['client_id'] = youtube_id_entry.get()
            self.credentials['instagram']['username'] = instagram_user_entry.get()
            self.credentials['instagram']['password'] = instagram_pass_entry.get()
            self.save_config()
            settings_window.destroy()
            self.update_status("Settings saved")

        save_btn = self.create_button(button_frame, "💾 Save", command=save_settings)
        save_btn.pack(side="left")

        cancel_btn = self.create_button(button_frame, "❌ Cancel", command=settings_window.destroy)
        cancel_btn.pack(side="right")

    def update_status(self, message):
        """Update status bar"""
        if hasattr(self, 'status_label'):
            if CTK_AVAILABLE:
                self.status_label.configure(text=message)
            else:
                self.status_label.configure(text=message)

    def load_config(self):
        """Load configuration from file"""
        try:
            with open("gui_config.json", "r") as f:
                config = json.load(f)
                self.credentials.update(config.get('credentials', {}))
        except FileNotFoundError:
            pass

    def save_config(self):
        """Save configuration to file"""
        config = {
            'credentials': self.credentials
        }
        with open("gui_config.json", "w") as f:
            json.dump(config, f, indent=4)

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main function to run the application"""
    try:
        app = ModernSocialMediaGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
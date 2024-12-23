import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.subtitle_extractor import VideoSubtitleExtractor
import time
from ttkthemes import ThemedTk
from utils import SUPPORTED_LANGUAGES, check_gpu_availability

class SubtitleExtractorApp:
    def __init__(self):
        self.root = ThemedTk(theme="arc")  # Using themed tk for better look
        self.root.title("Video Hardcoded Subtitle Extractor")
        self.root.geometry("800x800")
        self.root.configure(bg='#f0f0f0')
        
        # Add icon to the application
        icon_path = "assets/icon/icon.ico"
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.video_path = ""
        self.subtitles = None
        self.is_processing_complete = False
        self.MAX_DISPLAY_SUBTITLES = 50  # Maximum number of subtitles to display
        self.save_button = None  # Add this line to store save button reference
        self.selected_lang = "en"  # Default language
        self.is_gpu_available = check_gpu_availability()

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Video Subtitle Extractor",
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=10)

        # Video selection frame
        self.frame_video = ttk.LabelFrame(main_frame, text="Video Selection", padding="10")
        self.frame_video.pack(fill=tk.X, padx=5, pady=5)

        self.entry_video = ttk.Entry(self.frame_video, width=50)
        self.entry_video.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.button_browse = ttk.Button(
            self.frame_video,
            text="Browse",
            command=self.browse_video,
            style='Accent.TButton'
        )
        self.button_browse.pack(side=tk.LEFT, padx=5)

        # Settings frame
        self.frame_settings = ttk.LabelFrame(main_frame, text="Processing Settings", padding="10")
        self.frame_settings.pack(fill=tk.X, padx=5, pady=5)

        # Frame rate settings
        frame_rate_frame = ttk.Frame(self.frame_settings)
        frame_rate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_rate_frame, text="Frame Processing Rate:").pack(side=tk.LEFT)
        self.frame_rate_value = ttk.Label(frame_rate_frame, text="5")
        self.frame_rate_value.pack(side=tk.RIGHT, padx=5)
        
        self.scale_frame_rate = ttk.Scale(
            frame_rate_frame,
            from_=1,
            to=30,
            orient=tk.HORIZONTAL,
            command=self.update_frame_rate_value
        )
        self.scale_frame_rate.set(5)
        self.scale_frame_rate.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Confidence threshold settings
        confidence_frame = ttk.Frame(self.frame_settings)
        confidence_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(confidence_frame, text="Confidence Threshold:").pack(side=tk.LEFT)
        self.confidence_value = ttk.Label(confidence_frame, text="0.5")
        self.confidence_value.pack(side=tk.RIGHT, padx=5)
        
        self.scale_confidence = ttk.Scale(
            confidence_frame,
            from_=0.1,
            to=1.0,
            orient=tk.HORIZONTAL,
            command=self.update_confidence_value
        )
        self.scale_confidence.set(0.5)
        self.scale_confidence.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Add language selection frame after settings frame
        lang_frame = ttk.Frame(self.frame_settings)
        lang_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        
        # Create language dropdown
        self.lang_var = tk.StringVar(value="en")
        lang_options = [f"{code} - {name}" for code, name in SUPPORTED_LANGUAGES.items()]
        self.lang_dropdown = ttk.Combobox(
            lang_frame, 
            values=lang_options,
            textvariable=self.lang_var,
            state='readonly',
            width=15
        )
        self.lang_dropdown.pack(side=tk.LEFT, padx=5)
        self.lang_dropdown.bind('<<ComboboxSelected>>', self.on_lang_change)        

        # Add GPU status indicator in settings frame
        gpu_frame = ttk.Frame(self.frame_settings)
        gpu_frame.pack(fill=tk.X, pady=5)
        
        gpu_status = "✅ GPU Available" if self.is_gpu_available else "❌ GPU Not Available."
        ttk.Label(gpu_frame, text="GPU Status:").pack(side=tk.LEFT)
        ttk.Label(gpu_frame, text=gpu_status).pack(side=tk.LEFT, padx=5)

        # Progress frame
        self.frame_progress = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        self.frame_progress.pack(fill=tk.X, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(
            self.frame_progress,
            mode='determinate',
            length=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(self.frame_progress, text="Ready")
        self.progress_label.pack()

        self.time_label = ttk.Label(self.frame_progress, text="Processing time: -")
        self.time_label.pack()

        # Process button with processing state
        self.button_process = ttk.Button(
            main_frame,
            text="Process Subtitles",
            command=self.process_subtitles,
            style='Accent.TButton'
        )
        self.button_process.pack(pady=10)

        # Add "Process New Video" button (initially disabled)
        self.button_new_process = ttk.Button(
            main_frame,
            text="Process New Video",
            command=self.reset_processing,
            style='Accent.TButton',
            state='disabled'
        )
        self.button_new_process.pack(pady=5)

        # Subtitles display
        subtitle_frame = ttk.LabelFrame(main_frame, text="Extracted Subtitles", padding="10")
        subtitle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_subtitles = tk.Text(
            subtitle_frame,
            height=15,
            width=80,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        scrollbar = ttk.Scrollbar(subtitle_frame, command=self.text_subtitles.yview)
        self.text_subtitles.configure(yscrollcommand=scrollbar.set)
        
        self.text_subtitles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Save button with disabled state
        self.button_save = ttk.Button(
            main_frame,
            text="Save Subtitles",
            command=self.save_subtitles,
            style='Accent.TButton',
            state='disabled'  # Initially disabled
        )
        self.button_save.pack(pady=20)

    def update_progress(self, value, message="Processing..."):
        self.progress_bar['value'] = value
        self.progress_label.config(text=message)
        self.root.update_idletasks()

    def update_frame_rate_value(self, value):
        self.frame_rate_value.config(text=f"{float(value):.0f}")

    def update_confidence_value(self, value):
        self.confidence_value.config(text=f"{float(value):.1f}")

    def browse_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        self.entry_video.delete(0, tk.END)
        self.entry_video.insert(0, self.video_path)

    def reset_processing(self):
        """Reset the application state for new video processing"""
        self.is_processing_complete = False
        self.subtitles = None
        self.video_path = ""
        self.entry_video.delete(0, tk.END)
        self.text_subtitles.delete(1.0, tk.END)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready")
        self.time_label.config(text="Processing time: -")
        self.button_process.configure(state='normal')
        self.button_new_process.configure(state='disabled')
        self.button_save.configure(state='disabled')
        self.enable_all_controls()

    def process_subtitles(self):
        if self.is_processing_complete:
            messagebox.showinfo("Info", "Processing already completed. Click 'Process New Video' to start fresh.")
            return

        video_path = self.entry_video.get()
        if not video_path:
            messagebox.showwarning("Warning", "Please select a video.")
            return

        if not os.path.isfile(video_path):
            messagebox.showwarning("Warning", f"The specified path '{video_path}' is not a valid file.")
            return

        # Disable all controls during processing
        self.disable_all_controls()
        
        # Show initialization message
        self.update_progress(0, "Initializing OCR engine...")
        self.root.update()  # Force update UI
        
        # Add small delay to show initialization
        self.root.after(1000, lambda: self.start_processing(video_path))

    def on_lang_change(self, event):
        """Handle language selection change"""
        selection = self.lang_dropdown.get()
        self.selected_lang = selection.split(' - ')[0]  # Get language code

    def start_processing(self, video_path):
        """Actual processing after initialization delay"""
        frame_rate = self.scale_frame_rate.get()
        confidence_threshold = self.scale_confidence.get()

        extractor = VideoSubtitleExtractor(
            lang=self.selected_lang,
            use_gpu=self.is_gpu_available
        )
        start_time = time.time()

        try:
            self.update_progress(0, "Processing video...")
            self.subtitles = extractor.extract_subtitles(
                video_path, 
                frame_rate=frame_rate,
                confidence_threshold=confidence_threshold,
                progress_bar=self
            )

            end_time = time.time()
            processing_time = end_time - start_time
            
            self.time_label.config(text=f"Processing time: {processing_time:.2f} seconds")
            self.display_subtitles()
            
            # Enable save button only if subtitles were found
            if self.subtitles:
                self.button_save.configure(state='normal')
            
            # Mark processing as complete and enable new process button
            self.is_processing_complete = True
            self.button_new_process.configure(state='normal')
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.update_progress(0, "Processing failed")
            self.button_process.configure(state='normal')
        finally:
            self.button_browse.configure(state='normal')

    def disable_all_controls(self):
        """Disable all control buttons during processing"""
        self.button_process.configure(state='disabled')
        self.button_browse.configure(state='disabled')
        self.button_new_process.configure(state='disabled')
        self.button_save.configure(state='disabled')
        self.scale_frame_rate.configure(state='disabled')
        self.scale_confidence.configure(state='disabled')

    def enable_all_controls(self):
        """Re-enable all control buttons after processing"""
        self.button_browse.configure(state='normal')
        self.scale_frame_rate.configure(state='normal')
        self.scale_confidence.configure(state='normal')
        # Note: Process and Save buttons are handled separately

    def display_subtitles(self):
        self.text_subtitles.delete(1.0, tk.END)
        if self.subtitles:
            total_subtitles = len(self.subtitles)
            display_count = min(self.MAX_DISPLAY_SUBTITLES, total_subtitles)
            
            if total_subtitles > self.MAX_DISPLAY_SUBTITLES:
                self.text_subtitles.insert(tk.END, 
                    f"Showing first {display_count} of {total_subtitles} subtitles:\n\n"
                )
            
            for i, subtitle in enumerate(self.subtitles[:display_count], 1):
                self.text_subtitles.insert(tk.END, 
                    f"{i}. {subtitle['start_time']} --> {subtitle['end_time']}\n"
                    f"{subtitle['text']}\n\n"
                )
            
            if total_subtitles > self.MAX_DISPLAY_SUBTITLES:
                self.text_subtitles.insert(tk.END, 
                    f"\n... {total_subtitles - display_count} more subtitles not shown ...\n"
                    f"All subtitles will be included when saved to file.\n"
                )
            
            self.update_progress(100, "Processing completed!")
        else:
            self.text_subtitles.insert(tk.END, "No subtitles found.")
            self.update_progress(100, "No subtitles found")

    def save_subtitles(self):
        if not self.subtitles:
            messagebox.showwarning("Warning", "No subtitles to save.")
            return

        output_filename = f"{os.path.splitext(os.path.basename(self.video_path))[0]}.srt"
        output_path = filedialog.asksaveasfilename(defaultextension=".srt", initialfile=output_filename, filetypes=[("SRT files", "*.srt")])

        if output_path:
            srt_content = ""
            for i, subtitle in enumerate(self.subtitles, 1):
                srt_content += f"{i}\n{subtitle['start_time']} --> {subtitle['end_time']}\n{subtitle['text']}\n\n"

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)

            messagebox.showinfo("Info", f"Subtitles saved to {output_path}")

    # Add this method to make the class compatible with progress_bar parameter
    def progress(self, value):
        self.update_progress(value)

def main():
    app = SubtitleExtractorApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()

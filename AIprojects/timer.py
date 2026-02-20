#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk


class CountdownTimer:
    def __init__(self, root):
        self.root = root
        root.title("Countdown Timer")
        root.resizable(False, False)

        self.running = False
        self.flashing = False
        self._timer_id = None
        self._flash_id = None
        self._display_updater = None
        self.remaining = 0
        self.flash_state = False

        # Input controls for hours, minutes, seconds
        input_frame = ttk.Frame(root, padding=(10, 10))
        input_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(input_frame, text="Hours:").grid(row=0, column=0, padx=(0, 4))
        self.hours_sb = tk.Spinbox(
            input_frame, from_=0, to=99, width=4, font=("TkDefaultFont", 10)
        )
        self.hours_sb.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(input_frame, text="Minutes:").grid(row=0, column=2, padx=(0, 4))
        self.mins_sb = tk.Spinbox(
            input_frame, from_=0, to=59, width=4, font=("TkDefaultFont", 10)
        )
        self.mins_sb.grid(row=0, column=3, padx=(0, 10))

        ttk.Label(input_frame, text="Seconds:").grid(row=0, column=4, padx=(0, 4))
        self.secs_sb = tk.Spinbox(
            input_frame, from_=0, to=59, width=4, font=("TkDefaultFont", 10)
        )
        self.secs_sb.grid(row=0, column=5)

        # Large display
        disp_frame = ttk.Frame(root, padding=(10, 6))
        disp_frame.grid(row=1, column=0, sticky="ew")
        self.time_label = ttk.Label(
            disp_frame, text="00:00:00", font=("Courier", 36), anchor="center"
        )
        self.time_label.pack(fill="x")

        # Buttons
        btn_frame = ttk.Frame(root, padding=(10, 10))
        btn_frame.grid(row=2, column=0, sticky="ew")
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop)
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # initialize spinboxes to 0
        self.hours_sb.delete(0, "end")
        self.hours_sb.insert(0, "0")
        self.mins_sb.delete(0, "end")
        self.mins_sb.insert(0, "0")
        self.secs_sb.delete(0, "end")
        self.secs_sb.insert(0, "10")

        # Keep updating the label when not running so user sees adjustments
        self._schedule_display_update()

        # Ensure we clean up after ourselves
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _schedule_display_update(self):
        self._update_display()
        self._display_updater = self.root.after(200, self._schedule_display_update)

    def _update_display(self):
        if self.running:
            h, m, s = self._hms_from_seconds(self.remaining)
        else:
            try:
                h = int(self.hours_sb.get())
                m = int(self.mins_sb.get())
                s = int(self.secs_sb.get())
            except Exception:
                h, m, s = 0, 0, 0
        self.time_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

    def _hms_from_seconds(self, total):
        if total < 0:
            total = 0
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return h, m, s

    def start(self):
        if self.running:
            return
        # If there was a finished flash, stop it first
        if self.flashing:
            self._stop_flashing()

        try:
            h = int(self.hours_sb.get())
            m = int(self.mins_sb.get())
            s = int(self.secs_sb.get())
        except Exception:
            h, m, s = 0, 0, 0

        total = max(0, h * 3600 + m * 60 + s)
        self.remaining = total

        # Disable spinboxes while running so accidental edits don't confuse state
        self._set_spinboxes_state("disabled")

        if self.remaining <= 0:
            # immediate time up
            self._time_up()
            return

        self.running = True
        self._tick()

    def _tick(self):
        self._update_display()
        if self.remaining <= 0:
            self.running = False
            self._time_up()
            return
        self.remaining -= 1
        self._timer_id = self.root.after(1000, self._tick)

    def stop(self):
        # Stops/pauses the countdown and any flashing
        if self._timer_id:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        self.running = False
        self._set_spinboxes_state("normal")
        if self.flashing:
            self._stop_flashing()

    def _set_spinboxes_state(self, state):
        for sb in (self.hours_sb, self.mins_sb, self.secs_sb):
            sb.config(state=state)

    def _time_up(self):
        # Called when countdown reaches zero
        self.time_label.config(text="00:00:00")
        self._start_flashing()

    def _start_flashing(self):
        if self.flashing:
            return
        self.flashing = True
        self.flash_state = False
        self._flash()  # start the loop
        # Play a bell once immediately
        try:
            self.root.bell()
        except Exception:
            pass

    def _flash(self):
        # Toggle visual state
        self.flash_state = not self.flash_state
        if self.flash_state:
            self.time_label.config(background="red", foreground="white")
            try:
                self.root.configure(background="red")
            except Exception:
                pass
        else:
            self.time_label.config(background="black", foreground="yellow")
            try:
                self.root.configure(background=self.root.cget("background"))
            except Exception:
                pass

        # beep on each flash
        try:
            self.root.bell()
        except Exception:
            pass

        # schedule next flash
        self._flash_id = self.root.after(600, self._flash)

    def _stop_flashing(self):
        if self._flash_id:
            try:
                self.root.after_cancel(self._flash_id)
            except Exception:
                pass
            self._flash_id = None
        self.flashing = False
        # restore normal visuals
        self.time_label.config(background="", foreground="")
        try:
            self.root.configure(background=self.root.cget("background"))
        except Exception:
            pass

    def _on_close(self):
        # cleanup scheduled callbacks before exit
        if self._timer_id:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
        if self._flash_id:
            try:
                self.root.after_cancel(self._flash_id)
            except Exception:
                pass
        if self._display_updater:
            try:
                self.root.after_cancel(self._display_updater)
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()

    def make_letter(self):
        values = {k: s.get() for k, s in self.v.items()}
        try:
            letter.create_letter(values)
        except Exception as ex:
            messagebox.showerror("Error", f"Could not open report:\n{ex}")

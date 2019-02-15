from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty

import os
import re
import downloader

YOUTUBE_URL_REG_EXP = "((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)"
OUTPUT_DIR = "labeled_data"


class MainScreen(BoxLayout):
    text_input_url = ObjectProperty()
    button_positive = ObjectProperty()
    button_negative = ObjectProperty()
    button_skip = ObjectProperty()
    text_comment = ObjectProperty()
    text_progress = ObjectProperty()
    skip_interval = ObjectProperty()
    text_comment_count = ObjectProperty()

    def set_buttons_disabled(self, disabled):
        self.button_positive.disabled = disabled
        self.button_negative.disabled = disabled
        self.button_skip.disabled = disabled

    def start(self):
        m = re.search(YOUTUBE_URL_REG_EXP, self.text_input_url.text)
        if m is None:
            ErrorPopup().open()
        else:
            self.video_id = m.group(0)
            self.comment_generator = downloader.download_comments(self.video_id)
            self.comment_count = 0

            self.set_buttons_disabled(False)
            self.get_next_comment()

    def get_next_comment(self):
        try:
            num_skip = int(self.skip_interval.text)
            for _ in range(num_skip):
                self.current_comment = next(self.comment_generator)
            self.update_comment_count(num_skip)
            self.text_comment.text = self.current_comment['text']
        except StopIteration:
            self.text_comment.text = "No more comments! Switch to another video"
            self.set_buttons_disabled(True)

    def label(self, label):
        fname = os.path.join(OUTPUT_DIR, label, "{}.txt".format(self.current_comment["cid"]))
        with open(fname, "w+", encoding="utf8") as f:
            f.write(self.current_comment['text'])
        self.get_next_comment()

    def update_comment_count(self, num_skip):
        self.comment_count += num_skip
        self.text_comment_count.text = "Comment count: " + str(self.comment_count)


class ErrorPopup(Popup):
    pass


class TextLabelingApp(App):
    pass


if __name__ == '__main__':
    os.makedirs(os.path.join(OUTPUT_DIR, "pos"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "neg"), exist_ok=True)
    TextLabelingApp().run()

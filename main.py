from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

import os
import re
import downloader

CRAWL_LIMIT = 200
YOUTUBE_URL_REG_EXP = "((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)"
OUTPUT_DIR = "labeled_data"


class MainScreen(BoxLayout):
    text_input_url = ObjectProperty()
    button_positive = ObjectProperty()
    button_negative = ObjectProperty()
    button_skip = ObjectProperty()
    text_comment = ObjectProperty()
    text_progress = ObjectProperty()

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
            if (self.comment_count >= CRAWL_LIMIT):
                raise StopIteration
            self.comment_count += 1
            self.text_comment.text = next(self.comment_generator)['text']
            self.text_progress.text = "{}/{}".format(self.comment_count, CRAWL_LIMIT)
        except StopIteration:
            self.text_comment.text = "DONE!"
            self.set_buttons_disabled(True)

    def label(self, label):
        fname = os.path.join(OUTPUT_DIR, label, "{}_{}.txt".format(self.video_id, self.comment_count))
        with open(fname, "w+") as f:
            f.write(self.text_comment.text)
        self.get_next_comment()


class ErrorPopup(Popup):
    pass


class TextLabelingApp(App):
    pass


if __name__ == '__main__':
    os.makedirs(os.path.join(OUTPUT_DIR, "pos"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "neg"), exist_ok=True)
    TextLabelingApp().run()

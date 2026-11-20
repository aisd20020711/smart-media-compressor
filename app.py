import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps
import av


class CompressorApp:

    def __init__(self, root):

        self.root = root

        self.root.title("智能影音圖片壓縮器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.file_path = tk.StringVar()
        self.quality = tk.StringVar(value="一般")

        self.image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }

        self.video_extensions = {
            ".mp4",
            ".mkv",
            ".mov",
            ".avi",
            ".webm",
            ".m4v",
            ".flv"
        }

        self.create_widgets()

    # ==========================================================
    # GUI
    # ==========================================================

    def create_widgets(self):

        title = tk.Label(
            self.root,
            text="智能影音圖片壓縮器",
            font=("Arial", 20, "bold")
        )

        title.pack(pady=20)

        subtitle = tk.Label(
            self.root,
            text="圖片使用 Pillow｜影片使用 PyAV｜保留原始聲音",
            fg="gray"
        )

        subtitle.pack()

        # ------------------------------------------------------
        # 檔案
        # ------------------------------------------------------

        file_frame = tk.Frame(self.root)

        file_frame.pack(
            fill="x",
            padx=25,
            pady=20
        )

        self.entry = tk.Entry(
            file_frame,
            textvariable=self.file_path,
            width=52
        )

        self.entry.pack(
            side="left",
            padx=(0, 8)
        )

        self.browse_button = tk.Button(
            file_frame,
            text="瀏覽檔案",
            command=self.browse_file,
            width=10
        )

        self.browse_button.pack(
            side="left"
        )

        # ------------------------------------------------------
        # 類型
        # ------------------------------------------------------

        self.type_label = tk.Label(
            self.root,
            text="尚未選取檔案",
            fg="gray",
            font=("Arial", 11)
        )

        self.type_label.pack(pady=5)

        # ------------------------------------------------------
        # 品質
        # ------------------------------------------------------

        quality_frame = tk.Frame(self.root)

        quality_frame.pack(pady=15)

        tk.Label(
            quality_frame,
            text="影片壓縮品質："
        ).pack(side="left")

        self.quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality,
            values=[
                "高品質",
                "一般",
                "高壓縮"
            ],
            state="readonly",
            width=12
        )

        self.quality_combo.pack(
            side="left",
            padx=10
        )

        # ------------------------------------------------------
        # 進度條
        # ------------------------------------------------------

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=520,
            mode="determinate"
        )

        self.progress.pack(
            pady=15
        )

        self.progress_label = tk.Label(
            self.root,
            text="0%"
        )

        self.progress_label.pack()

        # ------------------------------------------------------
        # 狀態
        # ------------------------------------------------------

        self.status_label = tk.Label(
            self.root,
            text="請選擇圖片或影片",
            fg="gray",
            wraplength=520
        )

        self.status_label.pack(
            pady=15
        )

        # ------------------------------------------------------
        # 開始
        # ------------------------------------------------------

        self.run_button = tk.Button(
            self.root,
            text="開始壓縮",
            command=self.start_compress,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 13, "bold"),
            width=22,
            state="disabled"
        )

        self.run_button.pack(
            pady=10
        )

        # ------------------------------------------------------
        # 說明
        # ------------------------------------------------------

        tk.Label(
            self.root,
            text="影片輸出：H.264 + AAC MP4",
            fg="#666666"
        ).pack(pady=5)

    # ==========================================================
    # 選擇檔案
    # ==========================================================

    def browse_file(self):

        path = filedialog.askopenfilename(

            title="選擇要壓縮的圖片或影片",

            filetypes=[

                (
                    "所有支援檔案",
                    "*.jpg *.jpeg *.png *.webp "
                    "*.mp4 *.mkv *.mov *.avi "
                    "*.webm *.m4v *.flv"
                ),

                (
                    "圖片",
                    "*.jpg *.jpeg *.png *.webp"
                ),

                (
                    "影片",
                    "*.mp4 *.mkv *.mov *.avi "
                    "*.webm *.m4v *.flv"
                )
            ]
        )

        if not path:
            return

        path = os.path.abspath(path)

        if not os.path.isfile(path):

            messagebox.showerror(
                "錯誤",
                "找不到指定的檔案。"
            )

            return

        self.file_path.set(path)

        ext = os.path.splitext(path)[1].lower()

        if ext in self.image_extensions:

            self.type_label.config(
                text="偵測到：圖片檔案",
                fg="green"
            )

            self.status_label.config(
                text="圖片將轉換成 WebP"
            )

        elif ext in self.video_extensions:

            self.type_label.config(
                text="偵測到：影片檔案",
                fg="blue"
            )

            self.status_label.config(
                text="影片將壓縮成 H.264 + AAC MP4"
            )

        else:

            self.type_label.config(
                text="不支援的檔案格式",
                fg="red"
            )

            self.run_button.config(
                state="disabled"
            )

            return

        self.run_button.config(
            state="normal"
        )

    # ==========================================================
    # 開始壓縮
    # ==========================================================

    def start_compress(self):

        if not self.file_path.get():
            return

        self.run_button.config(
            state="disabled"
        )

        self.browse_button.config(
            state="disabled"
        )

        self.progress["value"] = 0
        self.progress_label.config(
            text="0%"
        )

        thread = threading.Thread(
            target=self.compress_file,
            daemon=True
        )

        thread.start()

    # ==========================================================
    # 主流程
    # ==========================================================

    def compress_file(self):

        input_path = self.file_path.get()

        try:

            ext = os.path.splitext(
                input_path
            )[1].lower()

            directory = os.path.dirname(
                input_path
            )

            filename = os.path.splitext(
                os.path.basename(input_path)
            )[0]

            # --------------------------------------------------
            # 圖片
            # --------------------------------------------------

            if ext in self.image_extensions:

                output_path = os.path.join(
                    directory,
                    filename + "_compressed.webp"
                )

                self.root.after(
                    0,
                    lambda: self.status_label.config(
                        text="圖片壓縮中..."
                    )
                )

                self.compress_image(
                    input_path,
                    output_path
                )

            # --------------------------------------------------
            # 影片
            # --------------------------------------------------

            elif ext in self.video_extensions:

                output_path = os.path.join(
                    directory,
                    filename + "_compressed.mp4"
                )

                self.compress_video(
                    input_path,
                    output_path
                )

            else:

                raise Exception(
                    "不支援的檔案格式。"
                )

            # --------------------------------------------------
            # 計算大小
            # --------------------------------------------------

            original_size = (
                os.path.getsize(input_path)
                / 1024
                / 1024
            )

            compressed_size = (
                os.path.getsize(output_path)
                / 1024
                / 1024
            )

            if original_size > 0:

                reduction = (
                    1 -
                    compressed_size /
                    original_size
                ) * 100

            else:

                reduction = 0

            self.root.after(
                0,
                lambda: self.compress_success(
                    output_path,
                    original_size,
                    compressed_size,
                    reduction
                )
            )

        except Exception as e:

            error = str(e)

            self.root.after(
                0,
                lambda: self.compress_error(error)
            )

    # ==========================================================
    # 圖片壓縮
    # ==========================================================

    def compress_image(
        self,
        input_path,
        output_path
    ):

        img = Image.open(input_path)

        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # ------------------------------------------------------
        # 處理透明圖片
        # ------------------------------------------------------

        if img.mode in ("RGBA", "LA"):

            background = Image.new(
                "RGB",
                img.size,
                (255, 255, 255)
            )

            alpha = img.getchannel("A")

            background.paste(
                img,
                mask=alpha
            )

            img = background

        elif img.mode != "RGB":

            img = img.convert("RGB")

        # ------------------------------------------------------
        # WebP
        # ------------------------------------------------------

        img.save(
            output_path,
            "WEBP",
            quality=85,
            method=6
        )

        img.close()

        self.update_progress(100)

    # ==========================================================
    # 影片壓縮
    #
    # 這裡是這次真正修正聲音的地方。
    #
    # 不再先 decode(video)
    # 再 decode(audio)
    #
    # 改成 demux VIDEO + AUDIO，
    # 同一個讀取流程處理兩種串流。
    # ==========================================================

    def compress_video(
        self,
        input_path,
        output_path
    ):

        input_container = None
        output_container = None

        try:

            # --------------------------------------------------
            # 開啟來源
            # --------------------------------------------------

            input_container = av.open(
                input_path
            )

            # --------------------------------------------------
            # 找 Video
            # --------------------------------------------------

            if not input_container.streams.video:

                raise Exception(
                    "找不到影片串流。"
                )

            video_input = (
                input_container.streams.video[0]
            )

            # --------------------------------------------------
            # 找 Audio
            # --------------------------------------------------

            audio_input = None

            if input_container.streams.audio:

                audio_input = (
                    input_container.streams.audio[0]
                )

            # --------------------------------------------------
            # 顯示來源資訊
            # --------------------------------------------------

            video_codec = (
                video_input.codec_context.name
            )

            if audio_input:

                audio_codec = (
                    audio_input.codec_context.name
                )

                audio_rate = (
                    audio_input.rate
                    or 48000
                )

                try:
                    audio_layout = (
                        audio_input.layout.name
                    )
                except Exception:
                    audio_layout = "未知"

            else:

                audio_codec = "無音訊"
                audio_rate = 48000
                audio_layout = "無"

            self.root.after(
                0,
                lambda vc=video_codec,
                       ac=audio_codec,
                       al=audio_layout:
                self.status_label.config(
                    text=
                    f"影片：{vc}\n"
                    f"音訊：{ac} / {al}"
                )
            )

            # --------------------------------------------------
            # 建立輸出 MP4
            # --------------------------------------------------

            output_container = av.open(
                output_path,
                mode="w"
            )

            # --------------------------------------------------
            # H.264 Video
            # --------------------------------------------------

            fps = (
                video_input.average_rate
            )

            if fps is None:

                fps = 30

            output_video = (
                output_container.add_stream(
                    "libx264",
                    rate=fps
                )
            )

            output_video.width = (
                video_input.codec_context.width
            )

            output_video.height = (
                video_input.codec_context.height
            )

            output_video.pix_fmt = "yuv420p"

            # --------------------------------------------------
            # 壓縮品質
            # --------------------------------------------------

            quality = self.quality.get()

            if quality == "高品質":

                crf = "23"

            elif quality == "高壓縮":

                crf = "32"

            else:

                crf = "28"

            output_video.options = {

                "crf": crf,

                "preset": "fast"

            }

            # --------------------------------------------------
            # AAC Audio
            # --------------------------------------------------

            output_audio = None

            if audio_input is not None:

                output_audio = (
                    output_container.add_stream(
                        "aac",
                        rate=audio_rate
                    )
                )

                output_audio.bit_rate = 128000

                # 儘可能保留原聲道
                try:

                    output_audio.layout = (
                        audio_input.layout
                    )

                except Exception:

                    pass

            # --------------------------------------------------
            # MP4 Fast Start
            # --------------------------------------------------

            try:

                output_container.metadata[
                    "compatible_brands"
                ] = "isomiso2avc1mp41"

            except Exception:

                pass

            # --------------------------------------------------
            # 總時間
            # --------------------------------------------------

            total_duration = None

            if video_input.duration is not None:

                total_duration = (
                    float(video_input.duration)
                    *
                    float(video_input.time_base)
                )

            # ==================================================
            # 核心：
            #
            # 一次 demux video + audio
            #
            # ==================================================

            streams = [video_input]

            if audio_input is not None:
                streams.append(audio_input)

            for packet in input_container.demux(
                streams
            ):

                # =================================================
                # Video Packet
                # =================================================

                if (
                    packet.stream.index
                    == video_input.index
                ):

                    for frame in packet.decode():

                        # -------------------------------
                        # 編碼 H.264
                        # -------------------------------

                        encoded_packets = (
                            output_video.encode(
                                frame
                            )
                        )

                        for encoded in encoded_packets:

                            output_container.mux(
                                encoded
                            )

                        # -------------------------------
                        # 進度
                        # -------------------------------

                        if (
                            total_duration
                            and frame.time is not None
                        ):

                            percent = (
                                frame.time /
                                total_duration *
                                100
                            )

                            percent = max(
                                0,
                                min(
                                    99,
                                    percent
                                )
                            )

                            self.update_progress(
                                percent
                            )

                # =================================================
                # Audio Packet
                # =================================================

                elif (
                    audio_input is not None
                    and packet.stream.index
                    == audio_input.index
                ):

                    for frame in packet.decode():

                        # -------------------------------
                        # AAC
                        # -------------------------------

                        encoded_packets = (
                            output_audio.encode(
                                frame
                            )
                        )

                        for encoded in encoded_packets:

                            output_container.mux(
                                encoded
                            )

            # ==================================================
            # Flush Video Encoder
            # ==================================================

            for packet in output_video.encode():

                output_container.mux(
                    packet
                )

            # ==================================================
            # Flush Audio Encoder
            # ==================================================

            if output_audio is not None:

                for packet in output_audio.encode():

                    output_container.mux(
                        packet
                    )

            # ==================================================
            # 完成
            # ==================================================

            self.update_progress(100)

            if audio_input is not None:

                self.root.after(
                    0,
                    lambda:
                    self.status_label.config(
                        text=
                        "影片與聲音壓縮完成"
                    )
                )

            else:

                self.root.after(
                    0,
                    lambda:
                    self.status_label.config(
                        text=
                        "影片完成，但原始影片沒有音訊"
                    )
                )

        finally:

            if input_container is not None:

                input_container.close()

            if output_container is not None:

                output_container.close()

    # ==========================================================
    # 更新進度
    # ==========================================================

    def update_progress(
        self,
        value
    ):

        value = max(
            0,
            min(
                100,
                value
            )
        )

        self.root.after(
            0,
            lambda v=value:
            self.progress.config(
                value=v
            )
        )

        self.root.after(
            0,
            lambda v=value:
            self.progress_label.config(
                text=f"{v:.1f}%"
            )
        )

    # ==========================================================
    # 成功
    # ==========================================================

    def compress_success(
        self,
        output_path,
        original_size,
        compressed_size,
        reduction
    ):

        self.run_button.config(
            state="normal"
        )

        self.browse_button.config(
            state="normal"
        )

        self.progress["value"] = 100

        self.progress_label.config(
            text="100%"
        )

        self.status_label.config(
            text="壓縮完成！",
            fg="green"
        )

        messagebox.showinfo(

            "壓縮完成",

            "壓縮完成！\n\n"

            f"原始大小："
            f"{original_size:.2f} MB\n\n"

            f"壓縮後："
            f"{compressed_size:.2f} MB\n\n"

            f"容量減少："
            f"{reduction:.1f}%\n\n"

            f"輸出檔案：\n"
            f"{output_path}"
        )

    # ==========================================================
    # 失敗
    # ==========================================================

    def compress_error(
        self,
        error
    ):

        self.run_button.config(
            state="normal"
        )

        self.browse_button.config(
            state="normal"
        )

        self.progress["value"] = 0

        self.progress_label.config(
            text="0%"
        )

        self.status_label.config(
            text="壓縮失敗",
            fg="red"
        )

        messagebox.showerror(
            "壓縮失敗",
            "影片壓縮時發生錯誤：\n\n"
            + error
        )


# ==============================================================
# 主程式
# ==============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CompressorApp(root)

    root.mainloop()

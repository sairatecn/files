
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from pathlib import Path
import json
import subprocess
import sys


# ============================================================
# 配置文件
# ============================================================

CONFIG_FILE = Path.home() / ".photo_cropper_config.json"


# ============================================================
# 支持的图片格式
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


# ============================================================
# 主程序
# ============================================================

class PhotoCropperApp:

    def __init__(self, root):

        self.root = root

        self.root.title("照片中心裁剪工具")

        self.root.geometry("1100x720")

        self.root.minsize(
            900,
            600
        )

        # ----------------------------------------------------
        # 数据
        # ----------------------------------------------------

        self.image_paths = []

        self.output_dir = None

        # ----------------------------------------------------
        # 参数
        # ----------------------------------------------------

        self.width_var = tk.IntVar(
            value=400
        )

        self.height_var = tk.IntVar(
            value=300
        )

        self.format_var = tk.StringVar(
            value="WEBP"
        )

        self.webp_quality_var = tk.IntVar(
            value=90
        )

        self.status_var = tk.StringVar(
            value="请添加需要处理的照片"
        )

        self.progress_var = tk.DoubleVar(
            value=0
        )

        # ----------------------------------------------------
        # 加载配置
        # ----------------------------------------------------

        self.load_config()

        # ----------------------------------------------------
        # 创建界面
        # ----------------------------------------------------

        self.build_ui()

        # ----------------------------------------------------
        # 格式变化
        # ----------------------------------------------------

        self.format_var.trace_add(
            "write",
            self.on_format_changed
        )

        self.on_format_changed()

    # ========================================================
    # 配置
    # ========================================================

    def load_config(self):

        try:

            if not CONFIG_FILE.exists():
                return

            data = json.loads(
                CONFIG_FILE.read_text(
                    encoding="utf-8"
                )
            )

            self.width_var.set(
                int(
                    data.get(
                        "width",
                        400
                    )
                )
            )

            self.height_var.set(
                int(
                    data.get(
                        "height",
                        300
                    )
                )
            )

            self.format_var.set(
                data.get(
                    "format",
                    "WEBP"
                )
            )

            self.webp_quality_var.set(
                int(
                    data.get(
                        "webp_quality",
                        90
                    )
                )
            )

        except Exception:
            pass

    # ========================================================
    # 保存配置
    # ========================================================

    def save_config(self):

        try:

            data = {
                "width": int(
                    self.width_var.get()
                ),

                "height": int(
                    self.height_var.get()
                ),

                "format": self.format_var.get(),

                "webp_quality": int(
                    self.webp_quality_var.get()
                ),
            }

            CONFIG_FILE.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=4
                ),
                encoding="utf-8"
            )

        except Exception:
            pass

    # ========================================================
    # 创建界面
    # ========================================================

    def build_ui(self):

        # ====================================================
        # 左侧参数区
        # ====================================================

        left_frame = tk.Frame(
            self.root,
            width=270,
            padx=20,
            pady=20
        )

        left_frame.pack(
            side="left",
            fill="y"
        )

        left_frame.pack_propagate(
            False
        )

        # ----------------------------------------------------
        # 标题
        # ----------------------------------------------------

        tk.Label(
            left_frame,
            text="裁剪参数",
            font=(
                "Microsoft YaHei UI",
                18,
                "bold"
            )
        ).pack(
            anchor="w",
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # 宽度
        # ----------------------------------------------------

        tk.Label(
            left_frame,
            text="宽度（像素）",
            font=(
                "Microsoft YaHei UI",
                11
            )
        ).pack(
            anchor="w"
        )

        self.width_entry = tk.Spinbox(
            left_frame,
            from_=1,
            to=100000,
            textvariable=self.width_var,
            font=(
                "Consolas",
                13
            ),
            width=14
        )

        self.width_entry.pack(
            anchor="w",
            pady=(5, 18)
        )

        # ----------------------------------------------------
        # 高度
        # ----------------------------------------------------

        tk.Label(
            left_frame,
            text="高度（像素）",
            font=(
                "Microsoft YaHei UI",
                11
            )
        ).pack(
            anchor="w"
        )

        self.height_entry = tk.Spinbox(
            left_frame,
            from_=1,
            to=100000,
            textvariable=self.height_var,
            font=(
                "Consolas",
                13
            ),
            width=14
        )

        self.height_entry.pack(
            anchor="w",
            pady=(5, 20)
        )

        # ----------------------------------------------------
        # 裁剪方式
        # ----------------------------------------------------

        tk.Label(
            left_frame,
            text="裁剪方式",
            font=(
                "Microsoft YaHei UI",
                11,
                "bold"
            )
        ).pack(
            anchor="w",
            pady=(5, 8)
        )

        rule_text = (
            "以照片中心为基准\n\n"
            "最终保留区域：\n"
            "宽 × 高\n\n"
            "例如：\n"
            "400 × 300\n\n"
            "即从照片中心\n"
            "裁出 400 × 300 像素区域"
        )

        tk.Label(
            left_frame,
            text=rule_text,
            justify="left",
            anchor="w",
            font=(
                "Microsoft YaHei UI",
                10
            ),
            fg="#555555"
        ).pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # 分隔
        # ----------------------------------------------------

        ttk.Separator(
            left_frame,
            orient="horizontal"
        ).pack(
            fill="x",
            pady=20
        )

        # ----------------------------------------------------
        # 导出格式
        # ----------------------------------------------------

        tk.Label(
            left_frame,
            text="导出格式",
            font=(
                "Microsoft YaHei UI",
                11,
                "bold"
            )
        ).pack(
            anchor="w"
        )

        self.format_combo = ttk.Combobox(
            left_frame,
            textvariable=self.format_var,
            values=[
                "JPG",
                "PNG",
                "WEBP",
                "BMP",
                "TIFF"
            ],
            state="readonly",
            width=16,
            font=(
                "Microsoft YaHei UI",
                10
            )
        )

        self.format_combo.pack(
            anchor="w",
            pady=(6, 15)
        )

        # ----------------------------------------------------
        # WEBP质量
        # ----------------------------------------------------

        self.webp_quality_label = tk.Label(
            left_frame,
            text="WEBP质量（1～100）",
            font=(
                "Microsoft YaHei UI",
                11
            )
        )

        self.webp_quality_label.pack(
            anchor="w"
        )

        self.webp_quality_spinbox = tk.Spinbox(
            left_frame,
            from_=1,
            to=100,
            textvariable=self.webp_quality_var,
            font=(
                "Consolas",
                12
            ),
            width=14
        )

        self.webp_quality_spinbox.pack(
            anchor="w",
            pady=(5, 10)
        )

        tk.Label(
            left_frame,
            text="推荐：85～95\n数值越高，画质越好，文件越大",
            justify="left",
            font=(
                "Microsoft YaHei UI",
                9
            ),
            fg="#777777"
        ).pack(
            anchor="w"
        )

        # ====================================================
        # 右侧区域
        # ====================================================

        right_frame = tk.Frame(
            self.root,
            padx=20,
            pady=20
        )

        right_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ====================================================
        # 顶部按钮
        # ====================================================

        button_frame = tk.Frame(
            right_frame
        )

        button_frame.pack(
            fill="x"
        )

        # 添加照片

        tk.Button(
            button_frame,
            text="添加照片",
            command=self.add_files,
            font=(
                "Microsoft YaHei UI",
                11
            ),
            padx=18,
            pady=7
        ).pack(
            side="left"
        )

        # 删除选中

        tk.Button(
            button_frame,
            text="删除选中",
            command=self.remove_selected,
            font=(
                "Microsoft YaHei UI",
                11
            ),
            padx=18,
            pady=7
        ).pack(
            side="left",
            padx=8
        )

        # 清空

        tk.Button(
            button_frame,
            text="清空列表",
            command=self.clear_files,
            font=(
                "Microsoft YaHei UI",
                11
            ),
            padx=18,
            pady=7
        ).pack(
            side="left"
        )

        # 导出

        self.export_button = tk.Button(
            button_frame,
            text="导出",
            command=self.export_images,
            font=(
                "Microsoft YaHei UI",
                11,
                "bold"
            ),
            padx=30,
            pady=7
        )

        self.export_button.pack(
            side="right"
        )

        # ====================================================
        # 导出文件夹
        # ====================================================

        output_frame = tk.Frame(
            right_frame
        )

        output_frame.pack(
            fill="x",
            pady=(15, 10)
        )

        tk.Button(
            output_frame,
            text="选择导出文件夹",
            command=self.select_output_dir,
            font=(
                "Microsoft YaHei UI",
                10
            )
        ).pack(
            side="left"
        )

        self.output_label = tk.Label(
            output_frame,
            text="未选择导出文件夹",
            anchor="w",
            font=(
                "Microsoft YaHei UI",
                10
            ),
            fg="#666666"
        )

        self.output_label.pack(
            side="left",
            padx=12,
            fill="x",
            expand=True
        )

        # ====================================================
        # 文件数量
        # ====================================================

        self.file_count_label = tk.Label(
            right_frame,
            text="待处理照片：0 张",
            anchor="w",
            font=(
                "Microsoft YaHei UI",
                11,
                "bold"
            )
        )

        self.file_count_label.pack(
            fill="x",
            pady=(5, 8)
        )

        # ====================================================
        # 文件列表
        # ====================================================

        list_frame = tk.Frame(
            right_frame
        )

        list_frame.pack(
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            list_frame
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.file_list = tk.Listbox(
            list_frame,
            font=(
                "Microsoft YaHei UI",
                10
            ),
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set,
            activestyle="none"
        )

        self.file_list.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.file_list.yview
        )

        # 双击定位文件

        self.file_list.bind(
            "<Double-Button-1>",
            self.open_file_location
        )

        # ====================================================
        # 进度条
        # ====================================================

        self.progress_bar = ttk.Progressbar(
            right_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )

        self.progress_bar.pack(
            fill="x",
            pady=(12, 4)
        )

        # ====================================================
        # 状态
        # ====================================================

        self.status_label = tk.Label(
            right_frame,
            textvariable=self.status_var,
            anchor="w",
            font=(
                "Microsoft YaHei UI",
                10
            ),
            fg="#666666"
        )

        self.status_label.pack(
            fill="x",
            pady=(5, 0)
        )

    # ========================================================
    # 格式改变
    # ========================================================

    def on_format_changed(
        self,
        *args
    ):

        if self.format_var.get() == "WEBP":

            self.webp_quality_label.pack(
                anchor="w"
            )

            self.webp_quality_spinbox.pack(
                anchor="w",
                pady=(5, 10)
            )

        else:

            self.webp_quality_label.pack_forget()

            self.webp_quality_spinbox.pack_forget()

    # ========================================================
    # 添加照片
    # ========================================================

    def add_files(self):

        paths = filedialog.askopenfilenames(
            title="添加需要处理的照片",
            filetypes=[
                (
                    "照片文件",
                    "*.jpg *.jpeg *.png *.webp "
                    "*.bmp *.tif *.tiff"
                ),
                (
                    "所有文件",
                    "*.*"
                )
            ]
        )

        if not paths:
            return

        # 已存在的文件
        existing = {
            str(
                Path(path).resolve()
            )
            for path in self.image_paths
        }

        added_count = 0

        for path in paths:

            normalized = str(
                Path(path).resolve()
            )

            # 自动去重

            if normalized in existing:
                continue

            self.image_paths.append(
                path
            )

            existing.add(
                normalized
            )

            added_count += 1

        self.refresh_file_list()

        self.status_var.set(
            f"本次添加 {added_count} 张照片"
        )

    # ========================================================
    # 刷新列表
    # ========================================================

    def refresh_file_list(self):

        self.file_list.delete(
            0,
            tk.END
        )

        for path in self.image_paths:

            self.file_list.insert(
                tk.END,
                Path(path).name
            )

        count = len(
            self.image_paths
        )

        self.file_count_label.config(
            text=f"待处理照片：{count} 张"
        )

    # ========================================================
    # 删除选中
    # ========================================================

    def remove_selected(self):

        selected = list(
            self.file_list.curselection()
        )

        if not selected:

            messagebox.showinfo(
                "提示",
                "请先选择需要删除的照片。"
            )

            return

        # 从后往前删除
        for index in reversed(
            selected
        ):

            del self.image_paths[index]

        self.refresh_file_list()

        self.status_var.set(
            f"已删除 {len(selected)} 张照片"
        )

    # ========================================================
    # 清空列表
    # ========================================================

    def clear_files(self):

        if not self.image_paths:
            return

        result = messagebox.askyesno(
            "确认清空",
            "确定要清空全部待处理照片吗？"
        )

        if not result:
            return

        self.image_paths.clear()

        self.refresh_file_list()

        self.progress_var.set(
            0
        )

        self.status_var.set(
            "照片列表已清空"
        )

    # ========================================================
    # 选择导出目录
    # ========================================================

    def select_output_dir(self):

        directory = filedialog.askdirectory(
            title="选择导出文件夹"
        )

        if not directory:
            return

        self.output_dir = Path(
            directory
        )

        self.output_label.config(
            text=str(
                self.output_dir
            )
        )

        self.status_var.set(
            "已选择导出文件夹"
        )

    # ========================================================
    # 获取裁剪区域
    # ========================================================

    def get_crop_box(
        self,
        image_width,
        image_height
    ):

        width = int(
            self.width_var.get()
        )

        height = int(
            self.height_var.get()
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "宽度和高度必须大于 0"
            )

        if width > image_width:

            raise ValueError(
                f"裁剪宽度 {width} "
                f"超过原图宽度 {image_width}"
            )

        if height > image_height:

            raise ValueError(
                f"裁剪高度 {height} "
                f"超过原图高度 {image_height}"
            )

        # ----------------------------------------------------
        # 计算中心
        # ----------------------------------------------------

        center_x = image_width / 2

        center_y = image_height / 2

        left = int(
            center_x - width / 2
        )

        top = int(
            center_y - height / 2
        )

        right = left + width

        bottom = top + height

        return (
            left,
            top,
            right,
            bottom
        )

    # ========================================================
    # 获取导出扩展名
    # ========================================================

    def get_extension(self):

        extension_map = {

            "JPG": ".jpg",

            "PNG": ".png",

            "WEBP": ".webp",

            "BMP": ".bmp",

            "TIFF": ".tiff",
        }

        return extension_map[
            self.format_var.get()
        ]

    # ========================================================
    # 保存图片
    # ========================================================

    def save_image(
        self,
        image,
        output_path
    ):

        export_format = (
            self.format_var.get()
        )

        # ----------------------------------------------------
        # JPG
        # ----------------------------------------------------

        if export_format == "JPG":

            if image.mode not in (
                "RGB",
                "L"
            ):

                image = image.convert(
                    "RGB"
                )

            image.save(
                output_path,
                format="JPEG",
                quality=95,
                optimize=True
            )

        # ----------------------------------------------------
        # PNG
        # ----------------------------------------------------

        elif export_format == "PNG":

            image.save(
                output_path,
                format="PNG",
                optimize=True
            )

        # ----------------------------------------------------
        # WEBP
        # ----------------------------------------------------

        elif export_format == "WEBP":

            quality = int(
                self.webp_quality_var.get()
            )

            if not 1 <= quality <= 100:

                raise ValueError(
                    "WEBP质量必须在1～100之间"
                )

            image.save(
                output_path,
                format="WEBP",
                quality=quality,
                method=6
            )

        # ----------------------------------------------------
        # BMP
        # ----------------------------------------------------

        elif export_format == "BMP":

            if image.mode not in (
                "RGB",
                "L"
            ):

                image = image.convert(
                    "RGB"
                )

            image.save(
                output_path,
                format="BMP"
            )

        # ----------------------------------------------------
        # TIFF
        # ----------------------------------------------------

        elif export_format == "TIFF":

            image.save(
                output_path,
                format="TIFF"
            )

    # ========================================================
    # 导出
    # ========================================================

    def export_images(self):

        # ----------------------------------------------------
        # 检查照片
        # ----------------------------------------------------

        if not self.image_paths:

            messagebox.showwarning(
                "提示",
                "请先添加需要处理的照片。"
            )

            return

        # ----------------------------------------------------
        # 检查导出目录
        # ----------------------------------------------------

        if self.output_dir is None:

            messagebox.showwarning(
                "提示",
                "请先选择导出文件夹。"
            )

            return

        # ----------------------------------------------------
        # 检查参数
        # ----------------------------------------------------

        try:

            width = int(
                self.width_var.get()
            )

            height = int(
                self.height_var.get()
            )

            if width <= 0 or height <= 0:

                raise ValueError

            if self.format_var.get() == "WEBP":

                quality = int(
                    self.webp_quality_var.get()
                )

                if not 1 <= quality <= 100:

                    raise ValueError

        except Exception:

            messagebox.showerror(
                "参数错误",
                "请检查宽度、高度和WEBP质量参数。"
            )

            return

        # ----------------------------------------------------
        # 保存配置
        # ----------------------------------------------------

        self.save_config()

        # ----------------------------------------------------
        # 创建目录
        # ----------------------------------------------------

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # 开始处理
        # ----------------------------------------------------

        total = len(
            self.image_paths
        )

        success = 0

        failed = []

        extension = self.get_extension()

        self.export_button.config(
            state="disabled"
        )

        self.progress_var.set(
            0
        )

        try:

            for index, file_path in enumerate(
                self.image_paths,
                start=1
            ):

                source = Path(
                    file_path
                )

                try:

                    # ----------------------------------------
                    # 打开图片
                    # ----------------------------------------

                    with Image.open(
                        file_path
                    ) as img:

                        original_width, original_height = (
                            img.size
                        )

                        # ------------------------------------
                        # 计算裁剪区域
                        # ------------------------------------

                        crop_box = self.get_crop_box(
                            original_width,
                            original_height
                        )

                        # ------------------------------------
                        # 裁剪
                        # ------------------------------------

                        cropped = img.crop(
                            crop_box
                        )

                        # ------------------------------------
                        # 新文件名
                        # ------------------------------------

                        output_path = (
                            self.output_dir /
                            f"{source.stem}{extension}"
                        )

                        # ------------------------------------
                        # 如果目标文件已经存在
                        # 直接覆盖
                        # ------------------------------------

                        self.save_image(
                            cropped,
                            output_path
                        )

                        success += 1

                except Exception as e:

                    failed.append(
                        f"{source.name}：{e}"
                    )

                # --------------------------------------------
                # 更新进度
                # --------------------------------------------

                progress = (
                    index /
                    total *
                    100
                )

                self.progress_var.set(
                    progress
                )

                self.status_var.set(
                    f"正在处理："
                    f"{index}/{total}    "
                    f"{source.name}"
                )

                self.root.update_idletasks()

        finally:

            self.export_button.config(
                state="normal"
            )

        # ====================================================
        # 完成
        # ====================================================

        self.progress_var.set(
            100
        )

        self.status_var.set(
            f"处理完成：成功 {success} 张，"
            f"失败 {len(failed)} 张"
        )

        # ----------------------------------------------------
        # 有失败
        # ----------------------------------------------------

        if failed:

            detail = "\n".join(
                failed[:10]
            )

            if len(failed) > 10:

                detail += (
                    f"\n……另外还有 "
                    f"{len(failed) - 10} 张失败"
                )

            messagebox.showwarning(
                "导出完成",
                f"成功：{success} 张\n"
                f"失败：{len(failed)} 张\n\n"
                f"{detail}"
            )

        # ----------------------------------------------------
        # 全部成功
        # ----------------------------------------------------

        else:

            messagebox.showinfo(
                "导出完成",
                f"成功处理 {success} 张照片。\n\n"
                f"裁剪尺寸："
                f"{width} × {height}\n\n"
                f"导出格式："
                f"{self.format_var.get()}\n\n"
                f"导出位置：\n"
                f"{self.output_dir}"
            )

    # ========================================================
    # 双击定位文件
    # ========================================================

    def open_file_location(
        self,
        event
    ):

        selection = (
            self.file_list.curselection()
        )

        if not selection:
            return

        index = selection[0]

        path = Path(
            self.image_paths[index]
        )

        if not path.exists():
            return

        # ----------------------------------------------------
        # Windows
        # ----------------------------------------------------

        if sys.platform.startswith(
            "win"
        ):

            subprocess.run(
                [
                    "explorer",
                    "/select,",
                    str(path)
                ]
            )

        # ----------------------------------------------------
        # macOS
        # ----------------------------------------------------

        elif sys.platform == "darwin":

            subprocess.run(
                [
                    "open",
                    "-R",
                    str(path)
                ]
            )

        # ----------------------------------------------------
        # Linux
        # ----------------------------------------------------

        else:

            subprocess.run(
                [
                    "xdg-open",
                    str(path.parent)
                ]
            )


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PhotoCropperApp(
        root
    )

    root.mainloop()


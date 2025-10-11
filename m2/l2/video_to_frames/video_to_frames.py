import cv2
import os
import numpy as np
from typing import Optional, List
from rembg import remove
from PIL import Image


def save_frame(frame: np.ndarray, frame_number: int, output_dir: str) -> None:
    """Сохраняет кадр как PNG с альфа-каналом."""
    fname = os.path.join(output_dir, f"frame_{frame_number:04d}.png")
    cv2.imwrite(fname, frame)


def process_video(
    input_video: str,
    output_dir: str,
    start_time: int,  # ms
    end_time: int,  # ms
    target_fps: int,
    gif_path: Optional[str] = None,  # <-- куда сохранить GIF
) -> None:

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(input_video)
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(original_fps / target_fps)

    # время → кадры
    start_frame = int(start_time * original_fps / 1000)
    end_frame = int(end_time * original_fps / 1000)

    frame_number = 0
    saved_frame_number = 0
    gif_frames: List[Image.Image] = []  # сюда сложим кадры для GIF

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number < start_frame:
            frame_number += 1
            continue
        if frame_number > end_frame:
            break

        if frame_number % frame_interval == 0:
            # 1. удаляем фон
            frame_no_bg = remove(frame)  # BGRA (H,W,4)

            # 2. складываем PNG
            save_frame(frame_no_bg, saved_frame_number, output_dir)

            # 3. при необходимости готовим кадр для GIF
            if gif_path:
                # Pillow работает с RGBA → конвертим из BGRA
                rgba = cv2.cvtColor(frame_no_bg, cv2.COLOR_BGRA2RGBA)
                pil_img = Image.fromarray(rgba)

                # GIF поддерживает максимум 256 цветов,
                # поэтому конвертируем в палитровый «P» с сохранением альфы
                pil_img = pil_img.convert("P", palette=Image.ADAPTIVE, colors=256)
                pil_img.info["transparency"] = pil_img.palette.getcolor((0, 0, 0, 0))
                gif_frames.append(pil_img)

            saved_frame_number += 1

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows()

    # 4. Записываем анимацию
    if gif_path and gif_frames:
        # duration = одна картинка на N миллисекунд
        duration_ms = int(1000 / target_fps)
        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=duration_ms,
            loop=0,  # 0 = бесконечный цикл
            disposal=2,  # «очистить до фонового» между кадрами
        )
        print(f"GIF сохранён в {gif_path}")


if __name__ == "__main__":
    process_video(
        input_video="input_video.mp4",
        output_dir="output_frames",
        start_time=3000,
        end_time=3800,
        target_fps=50,
        gif_path="sprite.gif",  # <-- добавьте путь, чтобы получить GIF
    )

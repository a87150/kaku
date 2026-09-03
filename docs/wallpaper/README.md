# 壁纸源文件说明

`719841.png` 是原始 4K 壁纸（3840×2160，约 8MB），仅保存在本地，
**未加入 git**（体积过大）。

Web 页面实际使用的是压缩版：
`common_static/wallpaper.jpg`（1920×1080 JPEG，约 220KB），已随代码仓库推送。

如需替换壁纸：
1. 用新图覆盖 `common_static/wallpaper.jpg`（建议宽度 ≤1920）
2. 或重新生成：`python -c "from PIL import Image; im=Image.open('719841.png'); im.convert('RGB').save('common_static/wallpaper.jpg','JPEG',quality=78,optimize=True)"`

[app]
# 应用名称
title = Wallhaven壁纸浏览器
# 包名
package.name = wallhaven
# 域名（反向）
package.domain = org.wallhaven.app
# 源码目录
source.dir = .
# 源码文件扩展名
source.include_exts = py,png,jpg,kv,atlas,json
# 版本号
version = 1.0
# 依赖列表
requirements = python3,kivy,requests,urllib3,certifi,charset-normalizer,idna,Pillow
# 图标文件（需要准备一个 512x512 的 png）
# icon.filename = %(source.dir)s/icon.png
# 启动画面
# presplash.filename = %(source.dir)s/presplash.png
# 应用权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# API 级别
android.api = 33
# 最低 API 级别
android.minapi = 21
# 架构（支持更多架构兼容性更好）
android.archs = arm64-v8a, armeabi-v7a
# 混淆
android.enable_androidx = True
# orientation
orientation = portrait
# fullscreen
fullscreen = 0
[buildozer]
# 日志级别
log_level = 2
# 单次警告
warn_on_root = 1
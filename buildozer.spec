[app]

title = 单价计算器
package.name = unitpricecalculator

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

requirements = python3,kivy,pyjnius

orientation = portrait

fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a,armeabi-v7a

android.minapi = 21

android.api = 33

android.ndk = 17c

android.sdk = 33

[buildozer]

log_level = 2

warn_on_root = 1

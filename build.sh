#!/usr/bin/env bash
#
# python-for-android build script
#

p4a apk \
--private ./klppr \
--package=com.klppr.mobile \
--name "klppr" \
--version 0.1 \
--bootstrap=pygame \
--requirements=python2,kivy,plyer,requests \
--arch=armeabi-v7a \
--permission INTERNET \
--permission ACCESS_FINE_LOCATION \
--permission ACCESS_COARSE_LOCATION

echo Installing APK...
adb install -r klppr-0.1-debug.apk

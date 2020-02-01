#!/bin/sh

set -e

cd /app

echo "[*] Running yarn build"
yarn build

echo "[*] Cleaning /front"
rm -rf /front/*

echo "[*] Copying dist/* files to /front"
cp -r dist/* /front

echo "[+] Done, exiting"

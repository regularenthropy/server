#! /usr/bin/bash

set -e

mkdir -p /app/mecab
cd /app/mecab
wget https://cdn.ablaze.one/other/mecab-ipadic-neologd.zip > /dev/null 2>&1
unzip mecab-ipadic-neologd.zip > /dev/null 2>&1
rm mecab-ipadic-neologd.zip
touch /app/mecab/dic_installed

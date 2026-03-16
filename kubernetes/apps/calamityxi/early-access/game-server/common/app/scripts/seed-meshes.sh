#!/bin/sh
set -eu

mkdir -p /server/losmeshes /server/navmeshes
cp -R /losmeshes/. /server/losmeshes/
cp -R /navmeshes/. /server/navmeshes/

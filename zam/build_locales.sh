#!/bin/bash

# Build locales to ../locale
# Must be run from the zam/ directory
# Requires 'msgfmt' command. Only for development!

# Generate .mo files
for po in locale/*.po
do
    file=${po##*/}
    lang=${file%.*}
    echo "Building '$lang'..."

    mkdir -p ../locale/$lang/LC_MESSAGES
    msgfmt -o ../locale/$lang/LC_MESSAGES/madtrans.mo $po
done

echo "Done!"

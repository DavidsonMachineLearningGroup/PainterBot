#!/bin/bash

contentimage="$1"
paintingdir="/home/kbhit/git/deepdream/paintings_forslackbot"

convert "${contentimage}" -resize '800x800>' "${paintingdir}/resizedinput.jpg" # resize input image to no more than 800 in each direction and convert to jpg if not already
python /home/kbhit/git/deepdream/deepdream.py "${paintingdir}/resizedinput.jpg" "${paintingdir}/finaloutput.jpg"

montages=""
image="finaloutput.jpg"
echo "creating montage for ${image}"
montage -label content "${paintingdir}/resizedinput.jpg" -label botdream "${paintingdir}/${image}" -geometry +2+2  "${paintingdir}/montage_${image}"

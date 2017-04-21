#!/bin/bash

contentimage="$1"
styleimage="$2"

imagestages=(
"mycheckpoints0.jpg"
"mycheckpoints50.jpg"
"mycheckpoints100.jpg"
"mycheckpoints150.jpg"
"mycheckpoints200.jpg"
"mycheckpoints250.jpg"
"mycheckpoints300.jpg"
"mycheckpoints350.jpg"
"mycheckpoints400.jpg"
"mycheckpoints450.jpg"
"mycheckpoints500.jpg"
"mycheckpoints550.jpg"
"mycheckpoints600.jpg"
"mycheckpoints650.jpg"
"mycheckpoints700.jpg"
"mycheckpoints750.jpg"
"mycheckpoints800.jpg"
"mycheckpoints850.jpg"
"mycheckpoints900.jpg"
"mycheckpoints950.jpg"
"finaloutput.jpg")

paintingdir="/home/kbhit/git/neural-style/me-myself-ai/paintings/forslackbot"

convert "${contentimage}" -resize '800x800>' "${paintingdir}/resizedinput.jpg" # resize input image to no more than 800 in each direction and convert to jpg if not already
python /home/kbhit/git/neural-style/neural_style.py --network "/home/kbhit/git/neural-style/imagenet-vgg-verydeep-19.mat" --content "${paintingdir}/resizedinput.jpg" --styles "${styleimage}" --checkpoint-output "${paintingdir}/mycheckpoints%s.jpg" --checkpoint-iterations 50 --output "${paintingdir}/finaloutput.jpg"

montages=""
for image in ${imagestages[@]}; do
	echo "creating montage for ${image}"
   montage -label content "${paintingdir}/resizedinput.jpg" -label style "${styleimage}" -label painting "${paintingdir}/${image}" -geometry +2+2  "${paintingdir}/montage_${image}"
	montages="${montages} ${paintingdir}/montage_${image}"
done

echo "${montages}"
convert -delay 25 -loop 0 ${montages} "${paintingdir}/animate_checkpoints.gif"

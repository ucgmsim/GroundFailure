imdb=$1
h5_parent_dir=$2
output=$3
csv_folder=$4
ims="-ims PGA"


for dir in "$h5_parent_dir"/*; do
    if test -d "$dir"; then
        landslide=`ls -1 $dir/*_jessee_*.hdf5|head -1`
        liquefaction=`ls -1 $dir/*_zhu_*.hdf5|head -1`
        folder_name=`basename $dir`
        echo $folder_name
        output_folder="$output/$folder_name"
        mkdir -p $output_folder
        
        echo $landslide
        echo "$liquefaction"
        echo "$output_folder"
        echo "$csv_folder"
        echo "$imdb"

        python3 ./master_point_finder.py $imdb $landslide $liquefaction $output_folder $ims $csv_folder
    fi

done

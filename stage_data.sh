mkdir -p staged_data/$1
mv *_processed staged_data/$1/
mv PLOGS staged_data/$1/
mv $1.txt staged_data/$1/

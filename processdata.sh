source ENV/bin/activate

if ! [ -d 'PLOGS' ]
then
  mkdir PLOGS
fi

while read line; do
  nohup python pymed/process_data.py --articles-dir="$line" &>>PLOGS/"$line".log& 
done < $1
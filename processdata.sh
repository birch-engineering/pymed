source ENV/bin/activate

while read line; do
  nohup python pymed/process_data.py --articles-dir="$line" &>>PLOGS/"$line".log& 
done < $1
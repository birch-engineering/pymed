source ENV/bin/activate

while read line; do
  nohup python pymed/crawler.py --mesh-term="$line" &>>LOGS/"$line".log& 
  sleep 2
done < $1
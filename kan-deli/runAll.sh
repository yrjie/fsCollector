if [ $# -lt 1 ]
then
    echo 'Usage: auto script'
    exit
fi

for ((i=1;i<=18600;i++))
do
    python collect_info.py $i
done


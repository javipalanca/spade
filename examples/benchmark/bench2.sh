#!/bin/sh

#paremtres prova
nmsg=1000
nmsgt=1000
tmsg=10
bench=2
totalemisores=6

dir = "/home/magentix/benchmarks"

#control de hosts
ip="192.168.1"
nini="1"

#lanzamos receptor
ssh magentix@$ip.2 java -jar /home/magentix/benchmarks/libmagentix2.jar 2 receptor qpid://receptor1@$ip.2:8080 &

sleep 1
# result file 
for prueba in `seq 1 1 3`
do
	file=res_${prueba}_${bench}
	echo "#Benchmark $bench with $nmsg messages" > $file
	echo "#(total benchmark time)" >> $file
	echo "#" >> $file
	echo "#NAgxH\tTime(s)" >> $file
	echo "#-----\t-------" >> $file

	for nemisores in `seq 1 1 $totalemisores`
	do
		echo -n "$nemisores\t" >> $file
		#lanzamos agentes locales
		#java -jar libmagentix2.jar 1 controlador qpid://controlador@localhost:8080 $nemisores | awk '/Bench Time/ {print $4}' >> $file &
		java -jar libmagentix2.jar 2 controlador qpid://controlador@localhost:8080 $nemisores >> $file &
		pid=`ps -C java | tail -1 | awk '{print $1}'`
		echo 'Lanzados agentes locales'

		#lanzamos emisores
		for n in `seq 1 1 $nemisores`
		do
			h=`expr $n + 2`
			ssh magentix@$ip.$h java -jar /home/magentix/benchmarks/libmagentix2.jar 2 emisor qpid://emisor$n@$ip.$h:8080 $nmsgt $tmsg 1 $n &
			sleep 1
		done
		echo 'Lanzados todos los agentes'
		#sleep `expr 12 + $n`
		wait $pid
	done
done
#matamos receptor
#killall -9 java

#!/bin/sh

#paremtres prova
nmsg=1000
nmsgt=1000
tmsg=10
bench=4
ntotalagentes=240
nmaquinas=6
echo $nemisores
#numero de agentes por maquina
nagmaq=`expr $ntotalagentes / $nmaquinas`

dir = "/home/magentix/benchmarks"

#control de hosts
ip="192.168.1"
nini="1"

#lanzamos receptores
#las maquinas para receptores son 2, 3 y 4
cont=1
for i in `seq 2 1 4`
do
	for j in `seq 1 1 $nagmaq`
	do
		ssh magentix@$ip.$i java -jar /home/magentix/benchmarks/libmagentix2.jar 4 receptor qpid://receptor$cont@$ip.$i:8080 &
		cont=`expr $cont + 1`
	done
done

sleep 10

# result file 
file=res_grande_${bench}
echo "#Benchmark 1 with $nmsg messages" > $file
echo "#(total benchmark time)" >> $file
echo "#" >> $file
echo "#NAgxH\tTime(s)" >> $file
echo "#-----\t-------" >> $file

#for prueba in `seq 1 1 3`
#do
	for agentes in 75 90 105 120
	do
		nemisores=`expr $agentes / 3`

		#lanzamos controlador
		#java -jar libmagentix2.jar 1 controlador qpid://controlador@localhost:8080 $nemisores | awk '/Bench Time/ {print $4}' >> $file &
		echo -n "$nemisores\t" >> $file
		java -jar libmagentix2.jar 4 controlador qpid://controlador@localhost:8080 $agentes >> $file &
		sleep 1
		pid=`ps -C java | tail -1 | awk '{print $1}'`
		echo 'Lanzados agentes locales'

		#lanzamos emisores
		#las maquinas para emisores son 5, 6 y 7
		cont=1
		for i in `seq 5 1 7`
		do
			for j in `seq 1 1 $nemisores`
			do
				ssh magentix@$ip.$i java -jar /home/magentix/benchmarks/libmagentix2.jar 4 emisor qpid://emisor$cont@$ip.$i:8080 $nmsgt $tmsg 1 $cont &
				cont=`expr $cont + 1`
			done
		done

		echo 'Lanzados todos los agentes'
		wait $pid
	done
#done
#matamos receptor
#killall -9 java

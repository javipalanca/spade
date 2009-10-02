#!/bin/bash

#paremtres prova
nmsg=10
nmsgt=10
tmsg=1
bench=1
#nemisores=2

dir="/home/magentix/pybenchmarks/spade/examples/benchmark"

#control de hosts
ip="192.168.1"
nini="1"

#lanzamos receptores
#java -jar libmagentix2.jar 1 receptor qpid://receptor1@192.168.1.1:8080 &
# result file 
for prueba in `seq 1 1 3`
do
	echo "=================="
	echo "Iteracion numero $prueba"
	echo "=================="
	file=res_${prueba}_${bench}
	echo "#Benchmark 1 with $nmsg messages" > $file
	echo "#(total benchmark time)" >> $file
	echo "#" >> $file
	echo "#NAgxH\tTime(s)" >> $file
	echo "#-----\t-------" >> $file

	for nemisores in `seq 1 1 7`
	do
		echo -n "$nemisores\t" >> $file

		for i in `seq 1 1 $nemisores`
		do
			h=`expr $i + 1`
			#ssh magentix@$ip.$h java -jar /home/magentix/benchmarks/libmagentix2.jar 1 receptor qpid://receptor$i@$ip.$h:8080 &
			echo "Launching receiver $i"
			python2.6 $dir/bench1_receiver.py 1 receptor$i@$ip.1 2> /dev/null &
			#sleep 2
		done

		sleep 1

		#lanzamos agentes locales
		#java -jar libmagentix2.jar 1 controlador qpid://controlador@localhost:8080 $nemisores |  awk '/Bench Time/ {print $4}' &
		python2.6 $dir/bench1_controller.py 2 controlador@$ip.1 $nemisores 2> /dev/null >> $file &
		echo "Launching controller"
		#java -jar libmagentix2.jar 2 controlador qpid://controlador@localhost:8080 $nemisores &
		#pid=`ps -C python2.6 | tail -1 | awk '{print $1}'`
		pid=`ps ax | grep bench1_controller.py | awk '{print $1}'`
		echo "El pid es: $pid"
		echo 'Lanzados agentes locales'

		sleep 1

		#lanzamos emisores
		for n in `seq 1 1 $nemisores`
		do
			h=`expr $n + 1`		
			python2.6 $dir/bench1_sender.py 1 emisor$n@$ip.1 $nmsgt $tmsg $nemisores $n 2> /dev/null &
			echo "Launching sender $n"
			#sleep 1
		done
		echo 'Lanzados todos los agentes'
		#sleep 1
		echo "Esperando a $pid"
		wait $pid

        # Matar receptores
		for i in `seq 1 1 $nemisores`
		do
			h=`expr $i + 1`
			#ssh magentix@$ip.$h java -jar /home/magentix/benchmarks/libmagentix2.jar 1 receptor qpid://receptor$i@$ip.$h:8080 &
			echo "Killing receiver $i"
		    pid=`ps ax | grep bench1_controller.py | awk '{print $1}'`
			for pid in `ps ax|grep receiver|grep -v grep|awk '{print $1}'`; do
				echo "Matar a receptor de pid $pid" ;
				kill -9 $pid ;
			done
			#sleep 2
		done

	done
done
#matar receptores
#for n in `seq 1 1 7`
#do
#	h=`expr $n + 1`
#	ssh magentix@$ip.$h killall -9 java
#done
#matamos cualquier agente que se haya quedad aun vivo
#killall -9 java

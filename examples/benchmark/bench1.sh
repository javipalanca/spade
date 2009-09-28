#paremtres prova
nmsg=1000
nmsgt=1000
tmsg=10
bench=1
#nemisores=2

dir = "/home/magentix/pybenchmarks"

#control de hosts
ip="192.168.1"
nini="1"

#lanzamos receptores
#java -jar libmagentix2.jar 1 receptor qpid://receptor1@192.168.1.1:8080 &
for i in `seq 1 1 7`
do
	h=`expr $i + 1`
	#ssh magentix@$ip.$h java -jar /home/magentix/benchmarks/libmagentix2.jar 1 receptor qpid://receptor$i@$ip.$h:8080 &
	ssh magentix@$ip.$h python /home/magentix/benchmarks/bench1_receiver.py 1 receptor$i@$ip.1 &
	sleep 2
done

# result file 
for prueba in `seq 1 1 3`
do
	file=res_${prueba}_${bench}
	echo "#Benchmark 1 with $nmsg messages" > $file
	echo "#(total benchmark time)" >> $file
	echo "#" >> $file
	echo "#NAgxH\tTime(s)" >> $file
	echo "#-----\t-------" >> $file

	for nemisores in `seq 1 1 7`
	do
		echo -n "$nemisores\t" >> $file

		#lanzamos agentes locales
		#java -jar libmagentix2.jar 1 controlador qpid://controlador@localhost:8080 $nemisores |  awk '/Bench Time/ {print $4}' &
		python bench1_controller.py 2 controlador@$ip.1 $nemisores >> $file &
		#java -jar libmagentix2.jar 2 controlador qpid://controlador@localhost:8080 $nemisores &
		pid=`ps -C python | tail -1 | awk '{print $1}'`
		echo "El pid es: $pid"
		echo 'Lanzados agentes locales'

		#lanzamos emisores
		for n in `seq 1 1 $nemisores`
		do
			h=`expr $n + 1`		
			ssh python bench1_sender.py 1 emisor$n@$ip.1 $nmsgt $tmsg $nemisores $n &
			sleep 1
		done
		echo 'Lanzados todos los agentes'
		sleep 1
		wait $pid
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

conda run -n Seeming_Ai python Starter.py &
python_pid=$!  
./_build_linux/_build_linux/open_seeming_personal 
binary_pid=$!  
cleanup() {  

    echo "Killing Python script with PID $python_pid"  

    kill  "$python_pid"

    echo "Killing binary with PID $binary_pid"  

    kill  "$binary_pid" 

    wait "$python_pid" "$binary_pid"  

}  
trap cleanup EXIT    
trap cleanup SIGINT
wait $python_pid $binary_pid



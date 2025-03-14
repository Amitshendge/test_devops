. venv/bin/activate

nohup streamlit run git_code/app.py --server.port 8500 --server.address 0.0.0.0 > nohup2.out 2>&1 &

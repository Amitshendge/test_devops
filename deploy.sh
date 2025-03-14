. venv/bin/activate

nohup streamlit run git_code/app.py > nohup2.out 2>&1 &
disown

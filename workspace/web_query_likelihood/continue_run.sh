sed -i -e "s/u = .*/u = 300/g" main.py
rake p=web_query_likelihood id=u_100 all_soft &

sed -i -e "s/u = .*/u = 400/g" main.py
rake p=web_query_likelihood id=u_200 all_soft &

sed -i -e "s/u = .*/u = 500/g" main.py
rake p=web_query_likelihood id=u_200 all_soft &

sed -i -e "s/u = .*/u = 600/g" main.py
rake p=web_query_likelihood id=u_200 all_soft &
